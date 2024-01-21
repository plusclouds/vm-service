import subprocess as sp
from service.windows.users.password import update_password
from service.windows.host_configuration import update_hostname
from service.windows.disk.manage_disk import update_disk

def start(metadata):
    # Updating password
    update_password(metadata)
    # Updateing hostname
    update_hostname(metadata)
    # Updating disks
    update_disk(metadata)
