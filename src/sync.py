__author__ = "Sam Gibson"
__version__ = "2.4"
__date__ = "07jul2019"

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


# Synchronise S3 bucket Objects with local files.
def sync_s3_objects(_updated_local_files, _outdated_s3_objects):
    if len(_outdated_s3_objects) == 0 and len(_updated_local_files) == 0:
        logging.info("No updates require for S3. All S3 Objects are already mirrored with '%s'." % local_repo)
        return
    for file in _outdated_s3_objects:
        s3.delete_object(Bucket=bucket_name, Key=file)
        logging.warning("Removed outdated object: '%s' from '%s' S3 Bucket." % (file, bucket_name))
    for file in _updated_local_files:
        mimetype, _ = guess_type(local_repo + file)
        if mimetype is None:
            logging.error("Could not upload: '%s'. The file has an unsupported MIME type." % (local_repo + file))
        try: s3.head_object(Bucket=bucket_name, Key=file)
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
                s3.upload_file(local_repo + file, bucket_name, file, {'ACL': 'public-read', 'ContentType': mimetype})
                logging.info("Uploaded file: '%s' to '%s' S3 Bucket." % (file, bucket_name))
            else:
                logging.error("An unexpected error occurred when attempting to upload file '%s' to '%s' S3 Bucket: '%s'"
                              % (file, bucket_name, e))


if local_repo.endswith('\\') is False:
    local_repo = Configuration.update(local_repo=local_repo+"\\")
    config.settings['local_repository_path'] = local_repo

file_obj = File()
file_obj.compare(local_repo, s3, config.settings, bucket_name)
sync_s3_objects(_updated_local_files=file_obj.updated_local_files,
                _outdated_s3_objects=file_obj.outdated_s3_objects)
