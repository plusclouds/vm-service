import os

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