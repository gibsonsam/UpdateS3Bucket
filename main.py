__author__ = "Sam Gibson"
__version__ = "1.1"
__date__ = "20feb2019"

from os import path, walk
from hashlib import md5
from re import search
from mimetypes import guess_type  # https://github.com/boto/boto3/issues/548
from boto3 import client

# Create an S3 client
s3 = client('s3')

bucket_name = 'mybucketname'
local_repo = "localpath"


# Removes outdated files from S3, uploading and replacing them with the newer, updated local files.
def sync_s3_objects(_s3_path):
    if _s3_path:  # if outdated files exist ...
        for value in _s3_path:
            mimetype, _ = guess_type(local_repo + value)
            if mimetype is None:
                raise Exception("Failed to guess mimetype")
            s3.delete_object(Bucket=bucket_name, Key=value)
            print("Deleted: %s/%s from S3" % (bucket_name, value))
            s3.upload_file(local_repo + value, bucket_name, value, ExtraArgs={'ACL': 'public-read',
                                                                              'ContentType': mimetype})
            print("Uploaded %s to %s bucket." % (value, bucket_name))
    else:
        print("No file updates required for S3.")


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
    for localpath, subdirs, files in walk(local_repo):
        for file in files:
            s3_val = path.join(localpath.replace(local_repo, ""), file).replace("\\", "/")
            local_val = path.join(localpath, file).replace("\\", "/")
            hash_md5 = md5()
            with open(local_val, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
                local_list_md5.append(s3_val + " : " + '"' + hash_md5.hexdigest() + '"')
    return local_list_md5


# Compare MD5 and ETag and files, removing up-to-date (unmodified) files from the list.
def compare_files():
    mismatched_files = list(set(get_md5()) - set(get_etag()))
    s3_path = []
    for item in mismatched_files:
        result = search(' (.*) :', item).group(1)
        s3_path.append(result)
    sync_s3_objects(s3_path)


compare_files()
