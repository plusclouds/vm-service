import json
import time
import platform
import os
import sys
import subprocess as sp
import requests
from . import storage
from hashlib import sha256
import logging
from logging.handlers import RotatingFileHandler
from .util.ssh_keys.ssh_key_parser import save_ssh_key
from .module_search.service_search import PlusCloudsService

#Updates the pip module if there are any updates
def update(module: str) -> None:
    sp.check_call([sys.executable,'-m','pip','install',module,'--upgrade'])

#Returns the system uuid based on the system platform
def get_uuid(platform: str) -> str:
	if platform.lower() == 'linux':
		return sp.getoutput('/usr/sbin/dmidecode -s system-uuid'
							) if not storage.file_exists('/var/local/temp_uuid.txt'
							) else storage.file_read('/var/local/temp_uuid.txt')
							
	elif platform.lower() == 'windows':
		return sp.check_output('wmic bios get serialnumber'
							   ).decode().split('\n')[1].strip()
		
	else:
		raise Exception("Platform: {} is not supported",platform.capitalize())

def service_messager(service: PlusCloudsService, message: str, method: str) -> None:
    if service != None:
        getattr(service.service_agent,method)(message)

def initialize_logger():
	log_formatter = logging.Formatter(
		'%(levelname)s %(lineno)4s => %(message)s ')

	logFile = '/var/log/plusclouds/plusclouds.log' if platform.system(
	) == 'Linux' else 'C:\Windows\System32\winevt\Logs\plusclouds.log'

	log_handler = RotatingFileHandler(
		logFile, mode='a', maxBytes=2 * 1024 * 1024, backupCount=1, encoding=None, delay=0)
	log_handler.setFormatter(log_formatter)
	log_handler.setLevel(logging.INFO)

	app_log = logging.getLogger('root')
	app_log.setLevel(logging.INFO)

	app_log.addHandler(log_handler)
	app_log.info("")
	app_log.info("============== Start of Execution at {}  =============".format(
		time.asctime()))
	return app_log

base_url = os.getenv('LEO_URL', "http://api.plusclouds.com")

if platform.system() == 'Linux':
	storage.create_folder_if_not_exists("/var/log/plusclouds")
	storage.create_file_if_not_exists("/var/log/plusclouds/plusclouds.log")
	storage.create_file_if_not_exists("/var/log/plusclouds/isExtended.txt")
	storage.create_file_if_not_exists("/var/log/plusclouds/disklogs.txt")
	storage.create_file_if_not_exists("/var/log/disklogs.txt")
	app_log = initialize_logger()
	# uuid of the vm assigned to uuid variable
	uuid = get_uuid(platform.system())
	# requests the information of the instance  sm
	try:
		response = requests.get(
			'{}/v2/iaas/virtual-machines/meta-data?uuid={}'.format(base_url, uuid))

		if response.status_code != 200:
			raise requests.exceptions.ConnectionError("")
		response = response.json()

	except requests.exceptions.ConnectionError as e:
		if not storage.file_exists("metadata.json"):
			print("Cannot access API in {} url".format(base_url))
			exit(-1)
		metadata_file = open("metadata.json", "r")
		response = json.load(metadata_file)


	oldDisk = '0'

	if "error" in response.keys():
		raise Exception(response["error"]["message"])
	if "data" not in response.keys():
		raise Exception("Faulty response.")

	total_disk = str(response['data']['virtualDisks']['data'][0]['total_disk'])
	hostname = response['data']['hostname']
	readablePassword = response['data']['password']
	password = sha256(readablePassword.encode()).hexdigest()
	service = None
	# Service Roles
	if "serviceRoles" in response["data"].keys():
		app_log.info(" ------  Service Roles Check  ------")

		if len(response["data"]["serviceRoles"]["data"]) > 0:
			for i in response["data"]["serviceRoles"]["data"]:
				app_log.info(
					'Installing unzipping and executing the ' + i["name"] + " execution files in url" + i["url"])

				service = PlusCloudsService(i["name"], i["url"],
											i["callback_url"]["ansible_url"],
											i["callback_url"]["service_url"])
				try:
					service.run()
				except Exception as e:
					app_log.error(
						"Exception occured while download and execution of service role {}, the following error has been caught {}".format(
							i["name"], e))
				#Check if api has update flag set to true
				if(str(i["has_update"]).lower() == "true"):
					try:
						module = "plusclouds-service"
						service_messager(service, "Starting to update the {} module".format(module),"starting")
						update(module)
						app_log.info("Updated {}".format(module))
						service_messager(service, "Successfully updated the {} module".format(module),"completed")
					except Exception as e:
						service_messager(service, "Failed updating the {} module with following error {}".format(module,e),"failed")
						app_log.error("Exception occurred while updating {}, following error has been caught {}".format(module,e))
				else:
					app_log.info("Service is not updated as has_update is not set to true")
					service_messager(service, "Service is not updated as has_update is not set to true","completed")
	# Password
	app_log.info(" ------  Password Check  ------")
	service_messager(service,"Starting password check","starting")
	isChanged = False
	if (storage.file_exists('/var/log/plusclouds/passwordlogs.txt')):
		oldPassword = storage.file_read('/var/log/plusclouds/passwordlogs.txt')
		if (oldPassword != password):
			service_messager(service,"Password is different in API, initiating password change","initiating")
			app_log.info(
				'Password in API is different. Setting isChanged variable to True')
			isChanged = True
			storage.file_write("/var/log/plusclouds/passwordlogs.txt", password)
		else:
			app_log.info("Password is not changed in API.")
	else:
		service_messager(service,"Password log file doesn't exist. Creating log file","initiating")
		app_log.info(
			"Password log file doesn't exist. Setting isChanged variable to True")
		isChanged = True
		storage.file_write("/var/log/plusclouds/passwordlogs.txt", password)
	if (isChanged == True):
		app_log.info(
			'isChanged variable is set to True. Executing password change call')
		p = sp.Popen('passwd', stdout=sp.PIPE, stdin=sp.PIPE, stderr=sp.STDOUT)
		stdout, stderr = p.communicate(
			input="{0}\n{0}\n".format(readablePassword).encode())
		if stderr:
			service_messager(service,"Following error occurred while changing password:\n"+str(stderr),"failed")
			app_log.error(stderr)
		else:
			service_messager(service,"Password has been updated successfully","completed")
			app_log.info('Password has been updated successfully')
	service_messager(service,"Password check is completed","completed")
 
	# Hostname
	app_log.info(" ------  Hostname Check  ------")
	service_messager(service,"Starting hostname check", "starting")
	oldHostname = storage.file_read('/etc/hostname')
	if oldHostname != hostname:
		service_messager(service,"Hostname is different in API. Initiating hostname change","initiating")
		app_log.info('Hostname is different in API. Changing hostname in VM.')
		os.system('hostnamectl set-hostname {}'.format(hostname))
	else:
		app_log.info('Hostname is not changed in API')
	service_messager(service,"Hostname check is completed","completed")

	# SSH Key
	service_messager(service,"Starting SSH key check","starting")
	app_log.info(" ------  SSH Key Check  ------")
	if "SSHPublicKeys" in response["data"].keys() and "data" in response["data"]["SSHPublicKeys"] and len(
			response["data"]["SSHPublicKeys"]["data"]) > 0:
		ssh_keys = response["data"]["SSHPublicKeys"]["data"]
		service_messager(service,"Saving ssh keys","initiating")
		for ssh_key in ssh_keys:
			save_ssh_key(ssh_key["ssh_encryption_type"], ssh_key["public_key"], ssh_key["email"])
	service_messager(service,"SSH key check is completed","completed")

	# Storage
	app_log.info(" ------  Storage Check  ------")
	service_messager(service,"Starting storage check", "starting")
	if (storage.file_exists('/var/log/plusclouds/disklogs.txt')):
		oldDisk = storage.file_read('/var/log/plusclouds/disklogs.txt')
		if oldDisk != total_disk:
			service_messager(service,"Disk is changed from API. Initiating check_disk","initiating")
			app_log.info("Disk is changed from API. Executing check_disk")
			storage.check_disk(uuid)
		if storage.file_exists("/var/log/plusclouds/isExtended.txt"):
			isExtended = storage.file_read("/var/log/plusclouds/isExtended.txt")
			if isExtended == '1':
				service_messager(service,"Disk is extended before reboot. Executing check_disk to resize","initiating")
				app_log.info(
					"Disk is extended before reboot. Executing check_disk to resize")
				storage.check_disk(uuid)
	else:
		app_log.info("Storage log file doesn't exist. Executing check_disk")
		service_messager(service,"Storage log file doesn't exist. Executing check_disk","initiating")
		storage.check_disk(uuid)
	service_messager(service,"Storage check is completed","completed")

# Windows
if platform.system() == 'Windows':
	uuid = get_uuid(platform.system())
	app_log = initialize_logger()
	# Requests the information of the instance
	response = requests.get(
		'{}/v2/iaas/virtual-machines/meta-data?uuid={}'.format(base_url, uuid)).json()
	password = response['data']['password']
	hashed_password = sha256(password.encode()).hexdigest()
	hostname = response['data']['hostname']

	# Password
	app_log.info(" ------  Password Check  ------")
	isChanged = False
	if (storage.file_exists('C:\Windows\System32\winevt\Logs\passwordlog.txt')):
		oldPassword = storage.file_read(
			'C:\Windows\System32\winevt\Logs\passwordlog.txt')
		if (oldPassword != hashed_password):
			app_log.info(
				"Password in API is different. Setting isChanged to True")
			isChanged = True
			storage.file_write(
				"C:\Windows\System32\winevt\Logs\passwordlog.txt", hashed_password)
		else:
			app_log.info(
				"Password hasn't been changed in API")
	else:
		isChanged = True
		storage.file_write("C:\Windows\System32\winevt\Logs\passwordlog.txt",
				   hashed_password)
	if (isChanged == True):
		app_log.info("Executing password change call.")
		sp.call("net users" + " Administrator " + password, shell=True)

	# Hostname

	app_log.info(" ------  Hostname Check  ------")
	current_hostname = sp.check_output(
		'hostname').decode().split('\n')[0].strip()
	hostname = hostname if len(hostname) <= 15 else hostname[0:15]
	if hostname != current_hostname:
		app_log.info(" Hostname is changed in API. Changing hostname in VM.")
		sp.call(["powershell", "Rename-Computer -NewName " + hostname], shell=True)
	else:
		app_log.info("Hostname is NOT changed in API.")

	# Disk

	app_log.info(" ------ Disk Check ------")
	p = sp.Popen(["diskpart"], stdout=sp.PIPE,
				 stdin=sp.PIPE, stderr=sp.PIPE)
	commands = ['select disk 0\n', 'select vol 2\n', 'extend\n', 'exit\n']
	for command in commands:
		p.stdin.write(bytes(command, 'utf-8'))
		time.sleep(.3)
	app_log.info(" ------ Disk Check End ------")


	# WinRM toggle

	def setup_winrm():
		file_loc = sp.check_output('powershell.exe $env:temp')
		file_loc = file_loc.decode("utf-8").split()[0]

		file = open(file_loc + '\\ansible_setup.ps1', 'w+')
		file.write('''
		[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
		$url = "https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"
		$file = "$env:temp\\ConfigureRemotingForAnsible.ps1"
		(New-Object -TypeName System.Net.WebClient).DownloadFile($url, $file)
		powershell.exe -ExecutionPolicy ByPass -File $file
		''')

		file.close()

		p = sp.Popen(['powershell.exe', file_loc +
					  '\\ansible_setup.ps1'], stdout=sp.PIPE)
		out, err = p.communicate()
		app_log.info(out)
		if err:
			app_log.info(err)


	def is_winrm_set():
		output = sp.check_output(
			'powershell.exe winrm enumerate winrm/config/Listener')
		if len(output.decode("utf-8").split('Listener')) != 3:
			return False
		output = output.decode("utf-8").split('Listener')[2].split('\r\n    ')
		winrm_listener = dict([i.split(' = ') for i in output[1:]])

		return (winrm_listener['Enabled'] == 'true' and winrm_listener['CertificateThumbprint'] and winrm_listener[
			'ListeningOn'])


	winrm_api_status = False
	if 'winrm_enabled' in response['data']:
		winrm_api_status = response['data']['winrm_enabled']
	is_winrm_running = True if sp.check_output(
		'powershell.exe Get-Service winrm').decode("utf-8").split()[6].lower() == "running" else False

	if winrm_api_status:
		if not is_winrm_running:
			p = sp.Popen('powershell.exe Start-Service winrm')
			app_log.info(" Starting WinRM service.")
		if not is_winrm_set():
			app_log.info(" WinRM is not set. Setting it up.")
			setup_winrm()
	else:
		if is_winrm_running:
			p = sp.Popen('powershell.exe Stop-Service winrm')
			app_log.info(" Stopping WinRM service.")

app_log.info("============== End of Execution at {}  =============".format(
	time.asctime()))
