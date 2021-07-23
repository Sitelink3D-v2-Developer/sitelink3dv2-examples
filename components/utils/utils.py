#!/usr/bin/python
import uuid
import datetime
import dateutil.parser
import pytz
import time

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