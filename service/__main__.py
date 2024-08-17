from service.linux import generic as genericLinux
from service.windows import generic as genericWindows
from api.metadata import get_metadata
from log.initialize import *
from service.util import stats
import time

logger = initialize_logger()

logger.info("============== Starting leo service at {}  =============".format(
    time.asctime()))

#uuid = get_uuid()
uuid = '97136816-d27e-63ed-17ba-acc64438ef4f'

stats.init_stats_process()

while True:
    metadata = get_metadata(uuid)
    logger.info("Got metadata like below;")
    logger.info("{}", metadata)

    if platform.system() == 'Linux':
        genericLinux.start(metadata)
    elif platform.system() == 'Windows':
        genericWindows.start(metadata)
    else:
        logger.info("============== End of Execution at {}  =============".format(
            time.asctime()))
    time.sleep(600)
