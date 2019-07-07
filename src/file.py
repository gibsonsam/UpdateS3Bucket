from os import path
from re import search
import logging.handlers
from src.checksum import Checksum
from src.error import Error
from src.config import Configuration


class File:
    __updated_local_files = []
    __outdated_s3_objects = []
    __ignored_filename = ''

    # Returns a list of omitted files.
    @staticmethod
    def omitted(settings):
        omitted_files = []
        omit_settings = settings['file_omittance']
        verified_settings = Configuration.verify(omit_settings, 'omit')

        if verified_settings is None:
            Error.log("Unable to find ignored file: '%s'"
                      % omit_settings['filename'])

        with open(verified_settings['filename'], 'r') as f:
            for filename in f.readlines():
                omitted_files.append(filename.replace('\n', ''))
        return omitted_files

    # Format a list of files, returning the object/file name and extension.
    @staticmethod
    def format(files):
        formatted_files = []
        for file in files:
            result = search('(.*) :', file).group(1)
            formatted_files.append(result)
        return formatted_files

    # Compare MD5 and ETag and files, removing up-to-date (unmodified) files from the list.
    def compare(self, repo, s3, settings, bucket_name):
        if not path.exists(repo):
            logging.error("The specified directory does not exist: '%s'" % repo)
            exit(1)
        local = Checksum.get_md5(settings, repo, File.omitted(settings))
        objects = Checksum.get_etag(s3, bucket_name)
        self.__updated_local_files = File.format(list(set(local) - set(objects)))
        self.__outdated_s3_objects = File.format(list(set(objects) - set(local)))

    @property
    def updated_local_files(self):
        return self.__updated_local_files

    @property
    def outdated_s3_objects(self):
        return self.__outdated_s3_objects
