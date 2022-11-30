import requests
import json
import os
import subprocess as sp
import fnmatch
import distro

def create_file_if_not_exists(fname: str) -> None:
	if not file_exists(fname):
		file = open(fname, "w")
		file.close()

def create_folder_if_not_exists(dir_name: str) -> None:
	os.makedirs(dir_name, exist_ok=True)

# This function takes filename as input, and then read it and return as a string variable
def file_read(fname: str) -> str:
	with open(fname, "r") as myfile:
		return myfile.readline().rstrip()

def file_write(fname: str, data: str) -> None:
	file = open(fname, "w+")
	file.write(data)
	file.close()


def file_exists(fname: str) -> bool:
	return os.path.exists(fname)

def get_distribution() -> str:
    return distro.id() + distro.version()


def extend_disk() -> None:
	distributionName = get_distribution()
	try:
		if distributionName in ['ubuntu18.04']:
			xvdaCount = len(fnmatch.filter(os.listdir('/dev'), 'xvda*'))
			gdisk_command = "bash -c \"echo -e 'd\n{}\nn\n\n\n\n\nw\nY\nY\n' | sudo gdisk /dev/xvda\"".format(
				str(xvdaCount - 1))
			sp.check_call(gdisk_command, shell=True)
			cmd = "bash -c \"echo -e 'd\n\nn\n\n\n\nN\nw\n' | sudo fdisk /dev/xvda\""

		if distributionName in ['centos7', 'centos8', 'debian17.5', 'pardus19.0', 'ubuntu16.04']:
			cmd = "bash -c \"echo -e 'd\n\nn\n\n\n\n\nw\n' | sudo fdisk /dev/xvda\""

		if distributionName in ['debian9', 'debian10', 'debian11', 'fedora30']:
			cmd = "bash -c \"echo -e 'd\n\nn\n\n\n\n\nN\nw\n' | sudo fdisk /dev/xvda\""

		if distributionName in ['ubuntu19.04', 'ubuntu19.10', 'ubuntu20.04']:
			cmd = "bash -c \"echo -e 'd\n\nn\n\n\n\nN\nw\n' | sudo fdisk /dev/xvda\""

		sp.check_call(cmd, shell=True)

	except Exception as e:
		# app_log.info(e)
		pass

	file = open("/var/log/plusclouds/isExtended.txt", "w+")
	file.write("1")
	file.close()
	# app_log.info('Rebooting system due to extend_disk operation')
	os.system('sudo reboot')

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