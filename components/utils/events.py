import json
import time
import websocket
import ssl
import queue
import threading
import signal
from enum import Enum
import logging
import requests
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "utils"))

from utils import *

session = requests.Session()

def get_dc_from_event(a_event_json):
    if("us;eu;ap" == a_event_json["dc"]):
        return "us"
    return a_event_json["dc"]

class EventSource(Enum):
    Owner = "owners"
    Site = "sites"

class EventManagerException(Exception):
    pass

class HttpEventManager:
    def __init__(self, a_server_config, a_identifier, a_source, a_headers):
        self.server = a_server_config
        self.identifier = a_identifier
        self.data_queue = queue.Queue()
        self.event_source = a_source
        self.headers = a_headers
        t = threading.Thread(target=self.event_stream_processor)
        t.daemon = True
        t.start()
        self.connected = False
        try:
            if(EventSource.Owner == self.event_source):
                self.wait_for_owner_subscription()
            else:
                self.wait_for_site_subscription()
        except EventManagerException:
            pass

    def wait_for_owner_subscription(self, a_timeout_seconds=None):
        return self.wait_for_data({"scope":"owner", "id":str(self.identifier)}, "subscribe", a_timeout_seconds)

    def wait_for_site_subscription(self, a_timeout_seconds=None):
        return self.wait_for_data({"scope":"site", "id":str(self.identifier)}, "subscribe", a_timeout_seconds)

    def wait_for_owner_key(self, a_timeout_seconds=None):
        expected_event_json = {
                "data": {
                    "type": "owner_key"
                },
                "type": "update",
                "service": "siteowner"
            }
        while True:
            item = self.wait_for_data({"scope":"owner", "id":str(self.identifier)}, "message", a_timeout_seconds)
            try:
                if( compare_dict(expected_event_json, item["event"])):
                    return item
            except (KeyError, AttributeError) as e:
                continue # this is no drama, we simply don't yet have the msg we want

    def wait_for_owner_scope_service_update(self, a_service, a_data_json, a_timeout_seconds=10):
        expected_event_json = {
                "data": a_data_json,
                "type": "update",
                "service": a_service
            }
        while True:
            item = self.wait_for_data({"scope":"owner", "id":str(self.identifier)}, "message", a_timeout_seconds)
            try:
                if( compare_dict(expected_event_json, item["event"])):
                    return item
            except (KeyError, AttributeError) as e:
                continue # this is no drama, we simply don't yet have the msg we want

    def wait_for_site_scope_service_update(self, a_service, a_data_json, a_timeout_seconds=10):
        expected_event_json = {
            "data": a_data_json,
            "type": "update",
            "service": a_service
            }
        while True:
            item = self.wait_for_data({"scope":"site", "id":str(self.identifier)}, "message", a_timeout_seconds)
            try:
                if( compare_dict(expected_event_json, item["event"])):
                    return item
            except (KeyError, AttributeError) as e:
                continue # this is no drama, we simply don't yet have the msg we want

    def wait_for_site_update(self, a_timeout_seconds=None):
        expected_event_json = {
                "data": {
                    "type": "site"
                },
                "type": "update",
                "service": "siteowner"
            }
        while True:
            item = self.wait_for_data({"scope":"owner", "id":str(self.identifier)}, "message", a_timeout_seconds)
            try:
                if( compare_dict(expected_event_json, item["event"])):
                    return item
            except (KeyError, AttributeError) as e:
                continue # this is no drama, we simply don't yet have the msg we want

    def wait_for_site_scope_rdm_update(self, a_timeout_seconds=None):
        expected_event_json = {
                "data": {
                    "domain": "sitelink"
                },
                "type": "update",
                "service": "rdm"
            }
        while True:
            item = self.wait_for_data({"scope":"site", "id":str(self.identifier)}, "message", a_timeout_seconds)
            try:
                if( compare_dict(expected_event_json, item["event"])):
                    return item
            except (KeyError, AttributeError) as e:
                continue # this is no drama, we simply don't yet have the msg we want

    def wait_for_rdm_site_update(self, a_timeout_seconds=None):
        expected_event_json = {
                "data": {
                    "type": "rdm_site"
                },
                "type": "update",
                "service": "siteowner"
            }
        while True:
            item = self.wait_for_data({"scope":"owner", "id":str(self.identifier)}, "message", a_timeout_seconds)
            try:
                if( compare_dict(expected_event_json, item["event"])):
                    return item
            except (KeyError, AttributeError) as e:
                continue # this is no drama, we simply don't yet have the msg we want

    def wait_for_site_designfile_job(self, a_job_id, a_timeout_seconds=None):
        expected_event_json = {
                "data": {
                    "type": "job",
                    "id": str(a_job_id)
                },
                "type": "update",
                "service": "designfile"
            }
        while True:
            item = self.wait_for_data({"scope":"site", "id":str(self.identifier)}, "message", a_timeout_seconds)
            try:
                if( compare_dict(expected_event_json, item["event"])):
                    return item
            except (KeyError, AttributeError) as e:
                continue # this is no drama, we simply don't yet have the msg we want

    def wait_for_report_job_update(self, a_job_info, a_timeout_seconds = None):
        expected_topic = {
            "scope": "site",
            "id": str(self.identifier),
        }
        expected_event = {
            "type": "update",
            "service": "spark-reporting",
            "data": {
                "_type": a_job_info["job_type"],
                "_id": a_job_info["_id"],
            },
        }
        while True:
            item = self.wait_for_data(expected_topic, "message", a_timeout_seconds)
            try:
                if not compare_dict(expected_event, item["event"]):
                    continue
                return item
            except (KeyError, AttributeError) as e:
                continue

    def wait_for_data(self, a_topic_json, a_type, a_timeout_seconds=None):
        t0 = time.time()
        while True:
            elapsed_time = time.time() - t0
            timeout = None
            if a_timeout_seconds is not None:
                timeout = a_timeout_seconds - elapsed_time
                if timeout < 0:
                    raise EventManagerException("Event Manager operation has timed out")

            try:
                item = self.data_queue.get(timeout = timeout)
                print(json.dumps(item))
            except (queue.Empty):
                raise EventManagerException("Event Manager operation has timed out")

            try:
                if( self.topic_compare_equal(a_topic_json, item["topic"]) and a_type == item["type"] ):
                    return item
            except (KeyError, AttributeError) as e:
                continue # this is no drama, we simply don't yet have the msg we want
            finally:
                self.data_queue.task_done()

    def topic_compare_equal(self, a_topic_json_1, a_topic_json_2):
        return (a_topic_json_1["scope"]== a_topic_json_2["scope"] and
                a_topic_json_1["id"] == a_topic_json_2["id"])

    def event_stream_processor(self):
        url = "{}/events/v1/{}/{}/subscribe".format(self.server.to_url(), self.event_source.value, self.identifier)
        data_tag = "data: "
        with session.get(url, headers=self.headers, stream=True) as r:
            if(200 != r.status_code):
                return
            self.connected = True
            for line in r.iter_lines():
                if line:
                    if line.startswith(bytes(data_tag, 'utf-8')):
                        resp = json.loads(line[len(data_tag):])
                        self.data_queue.put(resp)
