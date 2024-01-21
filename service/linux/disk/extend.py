from machine.distribution import *



def extend_disk(metadata) -> None:
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