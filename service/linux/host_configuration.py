import os

from log.initialize import initialize_logger

logger = initialize_logger()

def update_hostname(metadata):
    logger.info(" ------  Hostname Check  ------")
    hostname = metadata['hostname']
    changeHostname = True
    if changeHostname:
        logger.info('Hostname is different in API. Changing hostname in VM.')
        os.system('hostnamectl set-hostname {}'.format(hostname))
    else:
        logger.info('Hostname is not changed in API')
    logger.info('Hostname change process finished')