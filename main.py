from boto3 import client
from os import path, walk
from hashlib import md5
from re import search
from mimetypes import guess_type  # https://github.com/boto/boto3/issues/548

# Create an S3 client
s3 = client('s3')

bucket_name = 'mybucketname'
local_repo = "localpath"


# Removes outdated files from S3, uploading and replacing them with the newer, updated local files.
def update_s3_objects(_s3_path):
    if _s3_path:
        for x in range(0, len(_s3_path)):
            mimetype, _ = guess_type(local_repo + _s3_path[x])
            if mimetype is None:
                raise Exception("Failed to guess mimetype")
            s3.delete_object(Bucket=bucket_name, Key=_s3_path[x])
            print("Deleted: %s/%s from S3" % (bucket_name, _s3_path[x]))
            s3.upload_file(local_repo + _s3_path[x], bucket_name, _s3_path[x], ExtraArgs={'ACL': 'public-read', 'ContentType': mimetype})
            print("Uploaded %s to %s bucket." % (_s3_path[x], bucket_name))
    else:
        print("No file updates required for S3.")
        exit = input("Press 'enter' key to exit...")


# Retrieve the ETag from head of each Object in S3.
s3_list_etag = []
for val in s3.list_objects(Bucket=bucket_name)['Contents']:
    head = s3.head_object(Bucket=bucket_name, Key=val['Key'])
    s3_list_etag.append(" " + val['Key'] + " : " + head['ETag'])


# Retrieve the MD5 Hash Value of each local file.
local_list_md5 = []
for localpath, subdirs, files in walk(local_repo):
    for name in files:
        s3_val = path.join(localpath.replace(local_repo, ""), name.replace("\\", "/"))
        local_val = path.join(localpath.replace("\\", "/"), name.replace("\\", "/"))
        hash_md5 = md5()
        with open(local_val, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
            local_list_md5.append(" " + s3_val.replace("\\", "/") + " : " + '"' + hash_md5.hexdigest() + '"')


# Compare MD5 and ETag and files, removing up-to-date files from the list.
mismatched_files = list(set(local_list_md5) - set(s3_list_etag))
s3_path = []
for item in mismatched_files:
    result = search(' (.*) :', item).group(1)
    s3_path.append(result.replace("\\", "/"))


update_s3_objects(s3_path)
