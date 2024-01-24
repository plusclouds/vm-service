import requests
import os
from log.initialize import *

logger = initialize_logger()

base_url = os.getenv('LEO_URL', "http://api.plusclouds.com")

api_uris = [
	os.getenv('LEO_URL'),
	"https://api.plusclouds.com",
	"https://api4.plusclouds.com",
	"https://10.0.0.1:60000",
	"https://api.bivabu.com"
]

api_uri = "https://api.plusclouds.com"

def find_leo(uuid):
	for uri in api_uris:
		if(uri == None):
			continue

		metadata
	exit()
