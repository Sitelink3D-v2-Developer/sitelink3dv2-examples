#!/usr/bin/python
import json
import logging
import requests

session = requests.Session()

def GetDbaResource(a_server_config, a_site_id, a_uuid, a_headers):
    resrouce_url = "{}/dba/v1/sites/{}/resources/{}".format(a_server_config.to_url(), a_site_id, a_uuid)
    resource_response = session.get(resrouce_url, headers=a_headers)
    return resource_response.json()
