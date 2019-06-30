# UpdateS3Bucket
Update S3 Bucket objects with files stored locally on your PC. For AWS Static Website Hosting.

## Getting Started
Here's how to get started:

1. Clone this repo.
2. Open `config.yml` with your favourite editor and insert values for `aws_bucket_name` and`local_repository_path`.
3. By default, logging is set to `true` and outputs messages into `sync.log`. You may specify another log
file by inserting the name of the new log file in `config.yml` under `logging...handlers...filename`. To disable logging
navigate to `logging...log` and set the value to `false`.
4. To omit any files/directories contained within `local_repository_path` from upload, first ensure `file_omittance...omit_files` 
is set to `true`. Specify each omitted file/directory on a separate line in `ignore.txt`.
You may also change the default file by inserting a new value for `file_omittance...filename`.
5. Execute `main.py`, passing the name of the YAML file (`config.yml`) as a parameter.
6. Outdated files will be identified and replaced, newly discovered files are uploaded and omitted files are ignored.
##

#### Note:
Boto requires configuration before use.
Please refer to [this](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html?fbclid=IwAR2LlrS4O2gYH6xAF4QDVIH2Q2tzfF_VZ6loM3XfXsPAOR4qA-pX_qAILys) guide to set up your credentials.
