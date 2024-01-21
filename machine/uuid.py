import os
import subprocess as sp
import platform

def get_uuid() -> str:
    #   This is added here for external VMs or physical machines to be able to recognized by the api
    if "VM-UUID" in os.environ:
        return os.getenv("VM-UUID")

    if platform.system().lower() == 'linux':
        return sp.getoutput('/usr/sbin/dmidecode -s system-uuid')
    elif platform.system().lower() == 'windows':
        return sp.check_output('wmic bios get serialnumber').decode().split('\n')[1].strip()
    else:
        raise Exception("Platform: {} is not supported", platform.system().capitalize())