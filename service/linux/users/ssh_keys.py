from api.metadata import *
from log.initialize import initialize_logger
from pathlib import Path

logger = initialize_logger()


def update_ssh_keys(metadata):
    logger.info("-- SSH Key process start --")
    if "SSHPublicKeys" in metadata["data"].keys() and "data" in metadata["data"]["SSHPublicKeys"] and len(
            metadata["data"]["SSHPublicKeys"]["data"]) > 0:
        ssh_keys = metadata["data"]["SSHPublicKeys"]["data"]
        for ssh_key in ssh_keys:
            save_ssh_key(ssh_key["ssh_encryption_type"], ssh_key["public_key"], ssh_key["email"])
    logger.info("-- SSH Key process finished --")

def save_ssh_key(type: str, public_key: str, email: str) -> None:
    home = str(Path.home())

    file_object = open(home + '/.ssh/authorized_keys', 'a')
    file_object.write(type + " " + public_key + " " + email)
    file_object.write('\n')
    file_object.close()
