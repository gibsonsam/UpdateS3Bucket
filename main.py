__author__ = "Sam Gibson"
__version__ = "2.2"
__date__ = "30jun2019"

from os import path, walk
from hashlib import md5
from re import search
from mimetypes import guess_type
import logging.config
from sys import argv
from boto3 import client
from botocore.exceptions import ClientError
from yaml import safe_load, YAMLError

# Read configuration file.
settings = {}


def read_config_file():
    if len(argv) == 1:
        logging.error("No config file argument passed to script. Usage: $ python %s file.yml"
                      % path.basename(__file__))
        exit(1)
    if not path.exists(argv[1]):
        logging.error("The specified config file does not exist: '%s'" % argv[1])
        exit(1)
    else:
        with open(argv[1], 'r') as stream:
            try:
                global settings
                settings = safe_load(stream)
            except YAMLError as e:
                logging.error("An error occurred when loading the config file '%s': '%s'" % (argv[1], e))
                exit(1)


read_config_file()

# Setup Logging
logging.config.dictConfig(settings['logging'])

if settings['logging']['log'] is False:
    logging.getLogger().disabled = True

# Create an S3 client
s3 = client('s3')

bucket_name = settings['aws_bucket_name']
local_repo = settings['local_repository_path']


# Removes outdated files from S3, uploading and replacing them with the newer, updated local files.
def sync_s3_objects(_updated_local_files, _outdated_s3_objects):
    if not _updated_local_files and not _outdated_s3_objects:  # if no outdated objects/files exist ...
        logging.info("No updates require for S3. All S3 Objects are already mirrored with '%s'." % local_repo)
    for file in _updated_local_files:
        mimetype, _ = guess_type(local_repo + file)
        if mimetype is None:
            raise Exception("There was an issue uploading: %s%s" % (local_repo, file))
        try:
            s3.head_object(Bucket=bucket_name, Key=file)
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
                upload(file, {'ACL': 'public-read', 'ContentType': mimetype}, False)
            else:
                logging.error("An unexpected error occurred when attempting to upload file '%s' to '%s' S3 Bucket: '%s'"
                              % (file, bucket_name, e))
        else:
            s3.delete_object(Bucket=bucket_name, Key=file)
            logging.warning("Removed outdated object: '%s' from '%s' S3 Bucket." % (file, bucket_name))
            upload(file, {'ACL': 'public-read', 'ContentType': mimetype}, True)
    for obj in _outdated_s3_objects:
        s3.delete_object(Bucket=bucket_name, Key=obj)
        logging.warning("Removed outdated object: '%s' from '%s' S3 Bucket." % (obj, bucket_name))


# Uploads a file to S3, then outputs whether the file is newly discovered.
def upload(file, args, exists):
    s3.upload_file(local_repo + file, bucket_name, file, args)
    if not exists:
        logging.info("Uploaded newly discovered file: '%s' to '%s' S3 Bucket." % (file, bucket_name))
        return
    logging.info("Uploaded updated file: '%s' to '%s' S3 Bucket." % (file, bucket_name))


# Retrieve the ETag from head of each Object in S3.
def get_etag():
    s3_list_etag = []
    try:
        for obj in s3.list_objects(Bucket=bucket_name)['Contents']:
            head = s3.head_object(Bucket=bucket_name, Key=obj['Key'])
            s3_list_etag.append(obj['Key'] + " : " + head['ETag'])
    except ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] == 403:
            logging.error("S3 Bucket '%s' doesn't exist or client has insufficient permissions." % bucket_name)
        else: logging.error("An unexpected error occurred when retrieving ETag from S3 Object: '%s'" % e)
        exit(1)
    return s3_list_etag


# Retrieve the MD5 Hash Value of each local file.
def get_md5():
    local_list_md5 = []
    for root, dirs, files in walk(local_repo):
        if settings['file_omittance']['omit_files']:
            for omitted_file in get_omitted_files():
                if omitted_file in dirs:
                    dirs.remove(omitted_file)
                elif omitted_file in files:
                    files.remove(omitted_file)
        for file in files:
            s3_val = path.join(root.replace(local_repo, ""), file).replace("\\", "/")
            local_val = path.join(root, file).replace("\\", "/")
            hash_md5 = md5()
            with open(local_val, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
                local_list_md5.append(s3_val + " : " + '"' + hash_md5.hexdigest() + '"')
    return local_list_md5


# Returns a list of omitted files.
def get_omitted_files():
    omitted_files = []
    if path.exists(settings['file_omittance']['filename']):
        with open(settings['file_omittance']['filename'], 'r') as f:
            for filename in f.readlines():
                omitted_files.append(filename.replace('\n', ''))
    return omitted_files


# Format a list of files, returning the object/file name and extension.
def format_files(files):
    formatted_files = []
    for file in files:
        result = search('(.*) :', file).group(1)
        formatted_files.append(result)
    return formatted_files


# Compare MD5 and ETag and files, removing up-to-date (unmodified) files from the list.
def compare_files(repo):
    if not path.exists(repo):
        logging.error("The specified directory does not exist: '%s'" % repo)
        return
    if not repo.endswith("\\"):
        repo += '\\'
    updated_local_files = format_files(list(set(get_md5()) - set(get_etag())))
    outdated_s3_objects = format_files(list(set(get_etag()) - set(get_md5())))
    sync_s3_objects(updated_local_files, outdated_s3_objects)


compare_files(local_repo)
