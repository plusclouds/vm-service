import subprocess as sp
from api.metadata import *
from log.initialize import initialize_logger

logger = initialize_logger()

def update_password(metadata):
    logger.info("-- Update password starts --")
    password = metadata['password']
    isChanged = True
    if isChanged == True:
        logger.info("Executing password change call.")
        sp.call("net users" + " Administrator " + password, shell=True)
    logger.info("-- Update password ends --")