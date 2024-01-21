import subprocess as sp
from hashlib import sha256

def start(metadata):
    password = metadata['data']['password']
    hashed_password = sha256(password.encode()).hexdigest()
    hostname = metadata['data']['hostname']

    # Password
    logger.info(" ------  Password Check  ------")
    isChanged = False
    if (storage.file_exists('C:\Windows\System32\winevt\Logs\passwordlog.txt')):
        oldPassword = storage.file_read(
            'C:\Windows\System32\winevt\Logs\passwordlog.txt')
        if (oldPassword != hashed_password):
            logger.info(
                "Password in API is different. Setting isChanged to True")
            isChanged = True
            storage.file_write(
                "C:\Windows\System32\winevt\Logs\passwordlog.txt", hashed_password)
        else:
            logger.info(
                "Password hasn't been changed in API")
    else:
        isChanged = True
        storage.file_write("C:\Windows\System32\winevt\Logs\passwordlog.txt",
                           hashed_password)
    if (isChanged == True):
        logger.info("Executing password change call.")
        sp.call("net users" + " Administrator " + password, shell=True)

    # Hostname

    logger.info(" ------  Hostname Check  ------")
    current_hostname = sp.check_output(
        'hostname').decode().split('\n')[0].strip()
    hostname = hostname if len(hostname) <= 15 else hostname[0:15]
    if hostname != current_hostname:
        logger.info(" Hostname is changed in API. Changing hostname in VM.")
        sp.call(["powershell", "Rename-Computer -NewName " + hostname], shell=True)
    else:
        logger.info("Hostname is NOT changed in API.")

    # Disk

    logger.info(" ------ Disk Check ------")
    p = sp.Popen(["diskpart"], stdout=sp.PIPE,
                 stdin=sp.PIPE, stderr=sp.PIPE)
    commands = ['select disk 0\n', 'select vol 2\n', 'extend\n', 'exit\n']
    for command in commands:
        p.stdin.write(bytes(command, 'utf-8'))
        time.sleep(.3)
    logger.info(" ------ Disk Check End ------")

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
        logger.info(out)
        if err:
            logger.info(err)

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
    if 'winrm_enabled' in metadata['data']:
        winrm_api_status = metadata['data']['winrm_enabled']
    is_winrm_running = True if sp.check_output(
        'powershell.exe Get-Service winrm').decode("utf-8").split()[6].lower() == "running" else False

    if winrm_api_status:
        if not is_winrm_running:
            p = sp.Popen('powershell.exe Start-Service winrm')
            logger.info(" Starting WinRM plusclouds.")
        if not is_winrm_set():
            logger.info(" WinRM is not set. Setting it up.")
            setup_winrm()
    else:
        if is_winrm_running:
            p = sp.Popen('powershell.exe Stop-Service winrm')
            logger.info(" Stopping WinRM plusclouds.")
