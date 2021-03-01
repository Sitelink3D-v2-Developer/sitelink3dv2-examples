#!/usr/bin/python
import base64
import requests
import uuid

# >> Server URL:
def shp(env):
    if env == "qa":    return "https", "qa-api.code.topcon.com", "443"
    if env == "prod":  return "https", "api.code.topcon.com", "443"
    raise ValueError("no idea about env={}".format(env))

class ServerConfig():
    def __init__(self, a_environment, a_data_center):
        self._scheme, self._host, self._port = shp(a_environment)
        self._data_center = a_data_center        

    def to_url(self):
        ret = "{}://{}-{}:{}".format(self._scheme, self._data_center, self._host, self._port)
        return ret    

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
