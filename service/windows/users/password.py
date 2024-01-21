from api.metadata import *
from log.initialize import initialize_logger

logger = initialize_logger()

def update_password(metadata):
    password = metadata['data']['password']
    hashed_password = sha256(password.encode()).hexdigest()
    logger.info("-- Update password starts --")
    isChanged = True
    if isChanged == True:
        logger.info("Executing password change call.")
        sp.call("net users" + " Administrator " + password, shell=True)
    logger.info("-- Update password ends --")