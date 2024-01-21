from hashlib import sha256
from api.metadata import *
from log.initialize import initialize_logger

logger = initialize_logger()

def update_password(metadata):
    logger.info("-- Update password starts --")
    readablePassword = metadata['password']
    password = sha256(readablePassword.encode()).hexdigest()
    logger.info("Starting password check")
    # We will add password check in here because we cannot understand if the password is changed in metadata
    # or not. That is why we added this variable here. For future user.
    isChanged = False
    if (isChanged == True):
        logger.info(
            'isChanged variable is set to True. Executing password change call')
        p = sp.Popen('passwd', stdout=sp.PIPE, stdin=sp.PIPE, stderr=sp.STDOUT)
        stdout, stderr = p.communicate(
            input="{0}\n{0}\n".format(readablePassword).encode())
        if stderr:
            logger.error(stderr)
        else:
            logger.info('Password has been updated successfully')

    print('password change assumed')
    logger.info("-- Update password ends --")