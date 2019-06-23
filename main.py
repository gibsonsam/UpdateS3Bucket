__author__ = "Sam Gibson"
__version__ = "2.0"
__date__ = "23jun2019"

from os import path, walk
from hashlib import md5
from re import search
from mimetypes import guess_type  # https://github.com/boto/boto3/issues/548
from boto3 import client
from botocore.exceptions import ClientError

# Create an S3 client
s3 = client('s3')

bucket_name = 'www.sam-gibson.co.uk'
local_repo = "E:/Documents/Repository/HTML/%s/" % bucket_name


# Removes outdated files from S3, uploading and replacing them with the newer, updated local files.
def sync_s3_objects(_s3_path):
    if not _s3_path:  # if no outdated files exist ...
        print("No file updates required for S3.")
        return
    for value in _s3_path:
        mimetype, _ = guess_type(local_repo + value)
        if mimetype is None:
            raise Exception("There was an issue uploading: %s%s" % (local_repo, value))
        try: s3.head_object(Bucket=bucket_name, Key=value)
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
                upload(value, {'ACL': 'public-read', 'ContentType': mimetype}, False)
            else:
                print("Unexpected error: %s" % e)
        else:
            s3.delete_object(Bucket=bucket_name, Key=value)
            print("[Removed] outdated file: %s from %s S3 Bucket." % (value, bucket_name))
            upload(value, {'ACL': 'public-read', 'ContentType': mimetype}, True)


# Uploads a file to S3, then outputs whether the file is newly discovered.
def upload(file, args, exists):
    s3.upload_file(local_repo + file, bucket_name, file, args)
    if not exists:
        print("[Uploaded] newly discovered file: %s to %s S3 Bucket." % (file, bucket_name))
        return
    print("[Uploaded] updated file: %s to %s S3 Bucket." % (file, bucket_name))


# Retrieve the ETag from head of each Object in S3.
def get_etag():
    s3_list_etag = []
    for obj in s3.list_objects(Bucket=bucket_name)['Contents']:
        head = s3.head_object(Bucket=bucket_name, Key=obj['Key'])
        s3_list_etag.append(obj['Key'] + " : " + head['ETag'])
    return s3_list_etag


# Retrieve the MD5 Hash Value of each local file.
def get_md5():
    local_list_md5 = []
    for root, dirs, files in walk(local_repo):
        for omitted_file in get_omitted_files():
            if omitted_file in dirs: dirs.remove(omitted_file)
            elif omitted_file in files: files.remove(omitted_file)
        for file in files:
            s3_val = path.join(root.replace(local_repo, ""), file).replace("\\", "/")
            local_val = path.join(root, file).replace("\\", "/")
            hash_md5 = md5()
            with open(local_val, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
                local_list_md5.append(s3_val + " : " + '"' + hash_md5.hexdigest() + '"')
    return local_list_md5


# Returns a list of omitted files specified in 'ignore.txt'.
def get_omitted_files():
    omitted_files = []
    if path.exists('ignore.txt'):
        with open('ignore.txt', 'r') as f:
            for filename in f.readlines():
                omitted_files.append(filename.replace('\n', ''))
    return omitted_files


# Compare MD5 and ETag and files, removing up-to-date (unmodified) files from the list.
def compare_files():
    outdated_files = list(set(get_md5()) - set(get_etag()))
    s3_file_path = []
    for file in outdated_files:
        result = search('(.*) :', file).group(1)
        s3_file_path.append(result)
    sync_s3_objects(s3_file_path)


compare_files()
