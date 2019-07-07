import logging.config
from src.error import Error
from src.config import Configuration


class Logger:
    # Setup the logger and verify its settings.
    @staticmethod
    def setup(settings):
        logger_settings = settings['logging']
        if logger_settings['log'] is False:
            logging.getLogger().disabled = True
            return

        verified_settings = Configuration.verify(settings=logger_settings, file='log')

        if verified_settings is None:
            Error.log("Unable to find log file: '%s'"
                      % logger_settings['handlers']['file_handler']['filename'])
        logging.config.dictConfig(verified_settings)
