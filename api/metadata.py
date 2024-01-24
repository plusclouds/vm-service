import requests
import os
import socket
import pathlib
from log.initialize import *

logger = initialize_logger()

api_uris = [
	os.getenv('LEO_URL', "http://api.plusclouds.com/v2"),
	"https://api4.plusclouds.com/",
	"https://api.plusclouds.com/v3",
	"https://10.0.0.1:60000/v2",
	"https://api.bivabu.com/v2"
]

api_uri = "https://api.plusclouds.com"

def get_metadata(uuid):
	metadata = None

	version = pathlib.Path('version').read_text()

	for uri in api_uris:
		if (uri == None):
			continue

		try:
			response = requests.get(
				'{}/iaas/virtual-machines/meta-data?uuid={}&version={}'.format(uri, uuid, version), timeout=5)
		except socket.error:
			logger.error("Could not get response from " + uri + ", continuing")
			continue

		if response.status_code != 200:
			logger.error("I think we cannot retrieve the metadata, result is below")
			logger.error(response)
			continue
		else:
			metadata = response.json()
			break

	if metadata == None:
		raise requests.exceptions.ConnectionError("Cannot retrieve metadata")

	if 'error' in metadata.keys():
		raise Exception(metadata["error"]["message"])

	if 'data' not in metadata.keys():
		raise Exception("Faulty metadata.")

	return metadata['data']