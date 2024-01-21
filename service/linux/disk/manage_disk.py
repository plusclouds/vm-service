import os

from log.initialize import initialize_logger

logger = initialize_logger()

def update_disk(metadata):
    logger.info("-- Disk check started --")
    oldDisk = '0'
    total_disk = str(metadata['virtualDisks']['data'][0]['total_disk'])
    if (storage.file_exists('/var/log/plusclouds/disklogs.txt')):
        oldDisk = storage.file_read('/var/log/plusclouds/disklogs.txt')
        if oldDisk != total_disk:
            logger.info("Disk is changed from API. Executing check_disk")
            storage.check_disk(get_uuid())
        if storage.file_exists("/var/log/plusclouds/isExtended.txt"):
            isExtended = storage.file_read("/var/log/plusclouds/isExtended.txt")
            if isExtended == '1':
                logger.info(
                    "Disk is extended before reboot. Executing check_disk to resize")
                storage.check_disk(get_uuid())
    else:
        logger.info("Storage log file doesn't exist. Executing check_disk")
        storage.check_disk(get_uuid())
    logger.info("-- Disk checking and updating process finished --")


def check_disk(uuid):
    # app_log.info('isExtended = ' + file_read('/var/log/plusclouds/isExtended.txt') +
    #            ' || disklogs = ' + file_read('/var/log/plusclouds/disklogs.txt'))
    xvdaCount = str(len(fnmatch.filter(os.listdir('/dev'), 'xvda*')) - 1)
    distributionName = get_distribution()
    if distributionName in ['centos7', 'centos8', 'fedora30']:
        # app_log.info(
        # 'Declaring resizecall variable to that in centos7-8, or fedora30')
        resizeCall = 'sudo xfs_growfs /dev/xvda{}'.format(xvdaCount)
    # else:
    # app_log.info('Declaring resizecall for other OSes')
    # resizeCall = 'sudo resize2fs /dev/xvda{}'.format(xvdaCount)

    # uuid of the vm assigned to uuid variable

    base_url = os.getenv('LEO_URL', "http://api.plusclouds.com")

    try:
        response = requests.get(
            '{}/v2/iaas/virtual-machines/meta-data?uuid={}'.format(base_url, uuid))
        if response.status_code != 200:
            raise requests.exceptions.ConnectionError("")
        response_dict = response.json()  # json to dict

    except requests.exceptions.ConnectionError as e:
        if not file_exists("metadata.json"):
            print("Cannot access API in {} url".format(base_url))
            exit(-1)
        metadata_file = open("metadata.json", "r")
        response = json.load(metadata_file)
        response_dict = response

    total_disk = str(response_dict['data']['virtualDisks']['data'][0]['total_disk'])

    oldDisk = '0' if not file_exists(
        '/var/log/plusclouds/disklogs.txt') else file_read('/var/log/plusclouds/disklogs.txt')

    file_write("/var/log/plusclouds/disklogs.txt", total_disk)

    if (total_disk != '10240'):
        if (not file_exists('/var/log/plusclouds/isExtended.txt')) or (oldDisk != total_disk):
            # app_log.info(
            # 'Calling extend_disk function due either to inequalit of oldDisk and total_disk or non-existence of isExtended.txt file')
            extend_disk()

    else:
        # app_log.info('No need to extend disk because total_disk is 10240')
        file_write("/var/log/plusclouds/isExtended.txt", '0')

    isExtended = file_read("/var/log/plusclouds/isExtended.txt")
    if (isExtended == '1'):
        # app_log.info('Resizing the disk since isExtended is 1')
        if distributionName in ['centos7', 'centos8', 'fedora30']:
            os.system(resizeCall)

        file_write("/var/log/plusclouds/isExtended.txt", '0')
