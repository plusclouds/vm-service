from requests.exceptions import ConnectionError
from ..module_search.ansible_operations import execute_playbook_script, download, unzip
from ..module_search.callback_agent import CallbackAgent


class PlusCloudsService:
	def __init__(self, service_name: str, service_url: str, callback_ansible_url: str, callback_service_url: str):
		self.service_name = service_name

		self.download_path = "./services_" + service_name

		self.is_downloaded = False

		self.is_initiated = False

		self.service_url = service_url if (service_url.startswith("http")) else "http://" + service_url

		self.callback_ansible_url = callback_ansible_url

		self.callback_service_url = callback_service_url

		self.callback_agent = CallbackAgent(self.callback_ansible_url,'ansible')
		
		self.service_agent = CallbackAgent(self.callback_service_url,'service')

	def download_module(self):
		if self.is_downloaded:
			raise Exception("Already downloaded!")

		result = download(self.service_url, self.download_path)
		#Changing is_downloaded after executing download function
		self.is_downloaded = True if (result != "") else False
		return result

	def initiate_ansible(self):
		if not self.is_downloaded:
			self.download_module()

		result, log = execute_playbook_script(self.download_path + "/install.yml")
		self.is_initiated = True
		return result, log
		
	def run(self):
		self.callback_agent.downloading("Downloading starting")
		try:
			path = self.download_module()
			if path == "":
				raise ConnectionError()
		except ConnectionError as e:
			self.callback_agent.failed("Download failed ")
			return
		except Exception as e:
			self.callback_agent.failed(e)
			return

		else:
			self.callback_agent.initiating("Download completed, starting unzipping")

		if not unzip(path):
			self.callback_agent.failed("Unzip failed")
			return
		else:
			self.callback_agent.initiating("Playbook Execution starting.")

		self.initiate_ansible()

		log_file = open(self.download_path + "/execution.log", "r")
		log_file_content = log_file.read()

		if len(log_file_content) == 0:
			log_file_content = "Contents of ansible execution.log file missing."

		self.callback_agent.completed(log_file_content)
		self.service_agent.initiating("Initiating the service")