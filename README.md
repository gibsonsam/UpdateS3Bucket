# UpdateS3Bucket
Update S3 Bucket objects with files stored locally on your PC. For Static Website Hosting.

## Getting Started
Here's how to get started:

1. Clone this repo.
2. Open `main.py` with your favourite IDE/Editor and insert values for `bucket_name` and `local_repo`.
3. To omit any files/directories within `local_repo` from upload, specify each on a seperate line in `ignore.txt`.
4. Run `main.py`.
5. Outdated files will be indentified and replaced, newly discovered files are uploaded and omitted files are ignored.
