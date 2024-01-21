import requests
import os
from log.initialize import *

logger = initialize_logger()

base_url = os.getenv('LEO_URL', "http://api.plusclouds.com")

api_uris = [
	os.getenv('LEO_URL'),
	"https://api.plusclouds.com",
	"https://api4.plusclouds.com",
	"https://10.0.0.1:60000"
]

api_uri = "https://api.plusclouds.com"

def get_metadata(uuid):
	response = requests.get(
		'{}/v2/iaas/virtual-machines/meta-data?uuid={}'.format(api_uri, uuid))

	if response.status_code != 200:
		logger.error("I think we cannot retrieve the metadata, result is below")
		logger.error(response)
		raise requests.exceptions.ConnectionError("Cannot retrieve metadata")

	metadata = response.json()

	if 'error' in metadata.keys():
		raise Exception(metadata["error"]["message"])

	if 'data' not in metadata.keys():
		raise Exception("Faulty metadata.")

	return metadata['data']