from pathlib import Path
def save_ssh_key(type: str, public_key: str, email: str) -> None:
	home = str(Path.home())

	file_object = open(home+'/.ssh/authorized_keys', 'a')
	file_object.write(type + " " + public_key + " " + email)
	file_object.write('\n')
	file_object.close()