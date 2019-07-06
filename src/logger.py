import logging.config
from os import walk


class Logger:
    @staticmethod
    def setup(settings):
        logging.config.dictConfig(settings['logging'])

        if settings['logging']['log'] is False:
            logging.getLogger().disabled = True

    @staticmethod
    def notify(invalid_config=False):
        if invalid_config is True:
            file = open('..\\error.txt', 'w+')
            file.write("UpdateS3Bucket was unable to locate important files.\n\
            Error: The config file specified in the arguments could not be found.")
            file.close()
        log_exists = False
        config_exists = False
        for root, dirs, files in walk("..\\"):
            for file in files:
                if file.endswith(".log"):
                    log_exists = True
                elif file.endswith(".yml"):
                    config_exists = True
        file = open('..\\error.txt', 'w+')
        if log_exists is False or config_exists is False:
            file.write("UpdateS3Bucket was unable to locate important files.\n\
            Error: Missing config file or log files.")
            file.close()
        file.write("UpdateS3Bucket was unable to run due to missing required arguments.\n\
        Error: No config file argument passed to script. Usage: $ python sync.py ..\\file.yml")
        file.close()
