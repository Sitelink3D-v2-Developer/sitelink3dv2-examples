#!/usr/bin/python
import uuid
import datetime
import dateutil.parser
import pytz
import time
import os
import logging
import requests

session = requests.Session()

# >> Server URL:
def shp(env, a_scheme):
    if env == "qa":    return a_scheme, "qa-api.sitelink.topcon.com", "443"
    if env == "prod":  return a_scheme, "api.sitelink.topcon.com", "443"
    raise ValueError("no idea about env={}".format(env))

class ServerConfig():
    def __init__(self, a_environment, a_data_center, a_scheme="https"):
        self._scheme, self._host, self._port = shp(a_environment, a_scheme)
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

def current_milli_time(): return int(round(time.time() * 1000))        

def parse_iso_date_to_datetime(isostring, tz=None):
    try:
        if isostring is None: return None
        dRaw = dateutil.parser.parse(isostring)
        if dRaw.tzinfo is None: dRaw = dRaw.replace(tzinfo=pytz.utc)
        if tz is None: return dRaw
        d = dRaw.astimezone(pytz.utc).replace(tzinfo=tz)
        return d + d.utcoffset()
    except ValueError as err:
        raise ValueError("cannot parse {} as a date".format(isostring))

def datetime_to_unix_time_millis(a_date_time):
    if a_date_time.tzinfo is not None: a_date_time = a_date_time.replace(tzinfo=None) - a_date_time.utcoffset()
    return int((a_date_time - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000)

def json_from(r):
    r.raise_for_status()
    return r.json()

def compare_dict(expected, actual):
    for (key, expected_value) in expected.items():
        actual_value = actual[key]
        if type(expected_value) is dict:
            if type(actual_value) is not dict:
                return False
            if not compare_dict(expected_value, actual_value):
                return False
        elif actual_value != expected_value:
            return False
    return True

    site_name = site_detail(server, headers, args.site_id)["name"]

def site_detail(a_server_config, a_headers, a_site_id): 
    list_detail_url = "{0}/siteowner/v1/sites/{1}".format(a_server_config.to_url(), a_site_id)
    logging.debug("Querying Site Owner for details of site {} from {}".format(a_site_id, list_detail_url))

    response = session.get(list_detail_url, headers=a_headers)
    response.raise_for_status()
    
    site_list_json = response.json()
    return site_list_json

def get_site_name_summary(a_server_config, a_headers, a_site_id):
    site_name = site_detail(a_server_config, a_headers, a_site_id)["name"]
    return site_name + " [" + a_site_id[0:12] + "]"

def make_site_output_dir(a_server_config, a_headers, a_current_dir, a_site_id):
    output_dir = os.path.join(a_current_dir, get_site_name_summary(a_server_config, a_headers, a_site_id))
    os.makedirs(output_dir, exist_ok=True)
    return output_dir