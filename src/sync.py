__author__ = "Sam Gibson"
__version__ = "2.3"
__date__ = "06jul2019"

from mimetypes import guess_type
import logging.handlers
from boto3 import client
from botocore.exceptions import ClientError
from src.logger import Logger
from src.config import Configuration
from src.file import File

# Read configuration file.
config = Configuration()
config.read()

# Setup Logging
Logger.setup(config.settings)

# Create an S3 client
s3 = client('s3')

bucket_name = config.settings['aws_bucket_name']
local_repo = config.settings['local_repository_path']


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


file_obj = File()
file_obj.compare_files(local_repo, s3, config.settings, bucket_name)
sync_s3_objects(file_obj.updated_local_files, file_obj.outdated_s3_objects)
