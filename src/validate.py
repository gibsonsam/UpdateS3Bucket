from botocore.client import ClientError
from os import path, walk
import logging.handlers
from hashlib import md5


class Validate:
    def __init__(self, s3_obj, settings, bucket_name, local_repo, omitted_files):
        self.s3 = s3_obj
        self.settings = settings
        self.bucket_name = bucket_name
        self.local_repo = local_repo
        self.omitted_files = omitted_files

    # Retrieve the ETag from head of each Object in S3.
    def get_etag(self):
        s3_list_etag = []
        try:
            for obj in self.s3.list_objects(Bucket=self.bucket_name)['Contents']:
                head = self.s3.head_object(Bucket=self.bucket_name, Key=obj['Key'])
                s3_list_etag.append(obj['Key'] + " : " + head['ETag'])
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] == 403:
                logging.error("S3 Bucket '%s' doesn't exist or client has insufficient permissions." % self.bucket_name)
            else:
                logging.error("An unexpected error occurred when retrieving ETag from S3 Object: '%s'" % e)
            exit(1)
        return s3_list_etag

    # Retrieve the MD5 Hash Value of each local file.
    def get_md5(self):
        local_list_md5 = []
        for root, dirs, files in walk(self.local_repo):
            if self.settings['file_omittance']['omit_files']:
                for omitted_file in self.omitted_files:
                    if omitted_file in dirs:
                        dirs.remove(omitted_file)
                    elif omitted_file in files:
                        files.remove(omitted_file)
            for file in files:
                s3_val = path.join(root.replace(self.local_repo, ""), file).replace("\\", "/")
                local_val = path.join(root, file).replace("\\", "/")
                hash_md5 = md5()
                with open(local_val, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                    local_list_md5.append(s3_val + " : " + '"' + hash_md5.hexdigest() + '"')
        return local_list_md5
