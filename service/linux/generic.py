from log.initialize import initialize_logger
from service.linux.users.password import update_password
from service.linux.host_configuration import update_hostname
from service.linux.disk.manage_disk import update_disk

logger = initialize_logger()

def start(metadata):
    #password
    update_password(metadata)
    #updating the system disk
    #update_disk(metadata)
    #hostname
    update_hostname(metadata)
    #services
    #run_service_roles(metadata)
    #ssh key
    #update_ssh_keys(metadata)