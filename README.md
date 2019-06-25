# UpdateS3Bucket
Update S3 Bucket objects with files stored locally on your PC. For AWS Static Website Hosting.

## Getting Started
Here's how to get started:

1. Clone this repo.
2. Open `main.py` with your favourite IDE/Editor and insert values for `bucket_name` and `local_repo`.
3. To omit any files/directories within `local_repo` from upload, specify each on a separate line in `ignore.txt`.
4. Run `main.py`.
5. Outdated files will be identified and replaced, newly discovered files are uploaded and omitted files are ignored.
##

#### Note:
Boto requires configuration before use.
Please refer to [this](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html?fbclid=IwAR2LlrS4O2gYH6xAF4QDVIH2Q2tzfF_VZ6loM3XfXsPAOR4qA-pX_qAILys) guide to set up your credentials.
