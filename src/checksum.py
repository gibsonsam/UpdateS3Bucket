from botocore.client import ClientError
from os import path, walk
import logging.handlers
from hashlib import md5


class Checksum:
    # Retrieve the ETag from head of each Object in S3.
    @staticmethod
    def get_etag(s3, bucket_name):
        s3_list_etag = []
        try:
            for obj in s3.list_objects(Bucket=bucket_name)['Contents']:
                head = s3.head_object(Bucket=bucket_name, Key=obj['Key'])
                s3_list_etag.append(obj['Key'] + " : " + head['ETag'])
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] == 403:
                logging.error("S3 Bucket '%s' doesn't exist or client has insufficient permissions." % bucket_name)
            else:
                logging.error("An unexpected error occurred when retrieving ETag from S3 Object: '%s'" % e)
            exit(1)
        return s3_list_etag

    # Retrieve the MD5 Hash Value of each local file.
    @staticmethod
    def get_md5(settings, local_repo, omitted_files):
        local_list_md5 = []
        for root, dirs, files in walk(local_repo):
            if settings['file_omittance']['omit_files']:
                for omitted_file in omitted_files:
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
