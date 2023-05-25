"""Create Logger for app"""
import logging
from os import path, getcwd
from time import strftime
from utils import create_directory


def create_logger(log_name):
    """Create Log"""
    create_directory(['Logs'])
    logging.basicConfig(format=u'[%(asctime)s] %(levelname)s %(message)s',
                        level=logging.INFO,
                        handlers=[logging.FileHandler(path.join(getcwd(),
                                                                'Logs', log_name +
                                                                strftime('%d-%m-%Y') +
                                                                '.log'), 'a', 'utf-8')])

    return logging


def logger_level_change(logger, level):
    """Logger level change"""
    if level == 'error':
        logging.getLogger(logger).setLevel(logging.ERROR)
    elif level == 'info':
        logging.getLogger(logger).setLevel(logging.INFO)
    elif level == 'debug':
        logging.getLogger(logger).setLevel(logging.DEBUG)
    elif level == 'warning':
        logging.getLogger(logger).setLevel(logging.WARNING)
    else:
        pass
