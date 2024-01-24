import requests
import json
import os
import subprocess as sp
import fnmatch
import distro

def get_distribution() -> str:
    return distro.id() + distro.version()

