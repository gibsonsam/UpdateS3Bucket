from sys import argv
import logging.handlers
from yaml import safe_load, YAMLError
from os import path
from src.logger import Logger


class Configuration:
    __settings = {}

    def read(self):
        if len(argv) == 1:
            Logger.notify()
            exit(1)
        if not path.exists(argv[1]):
            Logger.notify(True)
            exit(1)
        else:
            with open(argv[1], 'r') as stream:
                try:
                    self.__settings = safe_load(stream)
                except YAMLError as e:
                    logging.error("An error occurred when loading the config file '%s': '%s'" % (argv[1], e))
                    exit(1)

    @property
    def settings(self):
        return self.__settings
