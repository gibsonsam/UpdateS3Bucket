from sys import argv
from yaml import safe_load, YAMLError, dump
from os import path
from src.error import Error


class Configuration:
    __settings = {}
    __config = ''

    # Read the Configuration file.
    @staticmethod
    def read():
        if len(argv) == 1:
            Error.log("No Configuration file argument passed to Python script.")
        elif len(argv) > 1:
            Configuration.__config = argv[1]
            if Configuration.__config.startswith("..\\") is False:
                pre_config = Configuration.__config
                Configuration.__config = "..\\%s" % Configuration.__config
                if path.exists(Configuration.__config) is False:
                    Error.log("Configuration file: '%s' not found." % pre_config)
            with open(Configuration.__config, 'r') as stream:
                try:
                    Configuration.__settings = safe_load(stream)
                except YAMLError as e:
                    Error.log("An error occurred loading the Configuration file. %s" % e)

    @property
    def settings(self):
        return self.__settings

    # Update the Configuration file with any changes.
    @staticmethod
    def update(omit_file=None, log_file=None, local_repo=None):
        with open(Configuration.__config) as f:
            yml = safe_load(f)

        if omit_file is not None:
            yml['file_omittance']['filename'] = omit_file
            with open(Configuration.__config, 'w') as f:
                dump(yml, f, default_flow_style=False)
                return yml['file_omittance']

        elif log_file is not None:
            yml['logging']['handlers']['file_handler']['filename'] = log_file
            with open(Configuration.__config, 'w') as f:
                dump(yml, f, default_flow_style=False)
                return yml['logging']

        elif local_repo is not None:
            yml['local_repository_path'] = local_repo
            with open(Configuration.__config, 'w') as f:
                dump(yml, f, default_flow_style=False)
                return yml['local_repository_path']

    # Verify settings returned from the Configuration file are correct.
    @staticmethod
    def verify(settings, file):
        filename = ''
        # logging...handlers..file_handler...filename
        if file == 'log': filename = settings['handlers']['file_handler']['filename']
        # file_omittance...filename
        elif file == 'omit': filename = settings['filename']
        if path.exists(filename): return settings
        elif path.exists(filename) is False:
            if filename.startswith('..\\') is False:
                __filename = '..\\%s' % filename
                if path.exists(__filename) is True:
                    if file == 'log': return Configuration.update(log_file=__filename)
                    elif file == 'omit': return Configuration.update(omit_file=__filename)
                return None
