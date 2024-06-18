import logging

from jproperties import Properties

configs = Properties()
with open('db.properties', 'rb') as config_file:
    configs.load(config_file)

debug_file_name = configs.get('debug_file_name').data
info_file_name = configs.get('info_file_name').data
warning_file_name = configs.get('warning_file_name').data
error_file_name = configs.get('error_file_name').data


def output_to_file_log_debug(message):
    print(message)
    logging.basicConfig(filename='simulator.log', level=logging.DEBUG)
    logging.debug(message)


def output_to_file_log_info(message):
    print(message)
    logging.basicConfig(filename='simulator.log', level=logging.INFO)
    logging.debug(message)


def output_to_file_log_warning(message):
    print(message)
    logging.basicConfig(filename='simulator.log', level=logging.WARNING)
    logging.debug(message)


def output_to_file_log_error(message):
    print(message)
    logging.basicConfig(filename='simulator.log', level=logging.CRITICAL)
    logging.debug(message)
