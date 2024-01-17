import os
import requests


def execute_playbook_script(directory: str):
	print("executing Playbook in dir: ", directory)

	if not os.path.exists(directory):
		return False, ""

	path = "/".join(directory.split("/")[0:-1])

	os.system("sudo apt install ansible -y")
	result = os.system("ansible-playbook -i hosts " + directory + " > " + path + "/execution.log 2>&1")
	print("Execution complete!")
	return True, result


def download(url: str, dest_folder: str) -> str:
	if not os.path.exists(dest_folder):
		os.makedirs(dest_folder)  # create folder if it does not exist

	filename = url.split('/')[-1].replace(" ", "_") + ".tar.gz"  # be careful with file names
	file_path = os.path.join(dest_folder, filename)

	r = requests.get(url, stream=True)
	if r.ok:
		print("saving to", os.path.abspath(file_path))
		with open(file_path, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024 * 8):
				if chunk:
					f.write(chunk)
					f.flush()
					os.fsync(f.fileno())

		return file_path
	else:  # HTTP status code 4XX/5XX
		print("Download failed: status code {}\n{}".format(r.status_code, r.text))
		return ""


def unzip(directory: str) -> bool:
	print("Unzipping in dir: ", directory)

	if not os.path.exists(directory):
		return False

	directory_list = directory.split("/")
	file_name = directory_list[-1]

	directory_list.pop()

	path = "/".join(directory_list)

	if ".zip" in file_name:
		os.system("apt-get install unzip -y")

		os.system("sudo unzip -o " + directory + " -d " + path + "/")

		print("Execution complete!")

	if ".tar.gz" in file_name:
		os.system("tar -xf " + directory + " -C " + path)

	return True
