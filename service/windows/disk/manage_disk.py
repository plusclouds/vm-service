import subprocess as sp
from log.initialize import initialize_logger

logger = initialize_logger()

def update_disk(metadata):
    logger.info(" ------ Disk Check ------")
    p = sp.Popen(["diskpart"], stdout=sp.PIPE,
                 stdin=sp.PIPE, stderr=sp.PIPE)
    commands = ['select disk 0\n', 'select vol 2\n', 'extend\n', 'exit\n']
    for command in commands:
        p.stdin.write(bytes(command, 'utf-8'))
        time.sleep(.3)
    logger.info(" ------ Disk Check End ------")