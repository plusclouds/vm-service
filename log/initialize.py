import platform
import time
import logging
from utils import file
from logging.handlers import RotatingFileHandler
# from .module_search.service_search import PlusCloudsService

# def service_messager(plusclouds: PlusCloudsService, message: str, method: str) -> None:
#     if plusclouds != None:
#         getattr(plusclouds.service_agent, method)(message)

logger = None

def initialize_logger() -> logging.Logger:
    log_formatter = logging.Formatter(
        '%(levelname)s %(lineno)4s => %(message)s ')

    if platform.system() == 'Linux':
        file.create_folder_if_not_exists("./service-logs")
        file.create_file_if_not_exists("./service-logs/leo.log")
        file.create_file_if_not_exists("./service-logs/isExtended.txt")
        file.create_file_if_not_exists("./service-logs/disklogs.txt")

    logFile = './service-logs/leo.log' if platform.system(
    ) == 'Linux' else 'C:\Windows\System32\winevt\Logs\leo.log'

    log_handler = RotatingFileHandler(
        logFile, mode='a', maxBytes=2 * 1024 * 1024, backupCount=1, encoding=None, delay=0)
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.INFO)

    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)

    logger.addHandler(log_handler)

    return logger