import logging


def output_to_file_log_debug(message):
    print(message)
    logging.basicConfig(filename='simulator.log', level=logging.DEBUG)
    logging.debug(message)


def output_to_file_log_info(message):
    logging.basicConfig(filename='example.log', level=logging.INFO)
    logging.debug(message)


def output_to_file_log_warning(message):
    logging.basicConfig(filename='example.log', level=logging.WARNING)
    logging.debug(message)


def output_to_file_log_error(message):
    logging.basicConfig(filename='example.log', level=logging.CRITICAL)
    logging.debug(message)