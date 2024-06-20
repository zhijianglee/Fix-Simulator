import logging

from jproperties import Properties

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)

debug_file_name = configs.get('debug_file_name').data
info_file_name = configs.get('info_file_name').data
warning_file_name = configs.get('warning_file_name').data
error_file_name = configs.get('error_file_name').data


def output_to_file_log_debug(message):
    print(message)
    logging.basicConfig(filename=debug_file_name, level=logging.DEBUG)
    logging.debug(message)


def output_to_file_log_info(message):
    print(message)
    logging.basicConfig(filename=info_file_name, level=logging.INFO)
    logging.debug(message)


def output_to_file_log_warning(message):
    print(message)
    logging.basicConfig(filename=warning_file_name, level=logging.WARNING)
    logging.debug(message)


def output_to_file_log_error(message):
    print(message)
    logging.basicConfig(filename=error_file_name, level=logging.CRITICAL)
    logging.debug(message)
