from os import path
from re import search
import logging.handlers
from src.validate import Validate


class File:
    __updated_local_files = []
    __outdated_s3_objects = []

    # Returns a list of omitted files.
    @staticmethod
    def get_omitted_files(settings):
        omitted_files = []
        ignored = settings['file_omittance']['filename']
        if not ignored.startswith('..\\'):
            ignored = '..\\%s' % ignored
        if path.exists(ignored):
            with open(ignored, 'r') as f:
                for filename in f.readlines():
                    omitted_files.append(filename.replace('\n', ''))
        return omitted_files

    # Format a list of files, returning the object/file name and extension.
    @staticmethod
    def format_files(files):
        formatted_files = []
        for file in files:
            result = search('(.*) :', file).group(1)
            formatted_files.append(result)
        return formatted_files

    # Compare MD5 and ETag and files, removing up-to-date (unmodified) files from the list.
    def compare_files(self, repo, s3, settings, bucket_name):
        if not path.exists(repo):
            logging.error("The specified directory does not exist: '%s'" % repo)
            exit(1)
        if not repo.endswith("\\"):
            repo += '\\'
        val = Validate(s3, settings, bucket_name, repo, File.get_omitted_files(settings))
        self.__updated_local_files = File.format_files(list(set(val.get_md5()) - set(val.get_etag())))
        self.__outdated_s3_objects = File.format_files(list(set(val.get_etag()) - set(val.get_md5())))

    @property
    def updated_local_files(self):
        return self.__updated_local_files

    @property
    def outdated_s3_objects(self):
        return self.__outdated_s3_objects
