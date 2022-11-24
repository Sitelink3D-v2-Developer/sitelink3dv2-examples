#!/usr/bin/python
import json
import time
import websocket
import ssl
import queue
import threading
import signal
from enum import Enum
import logging


import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "rdm_pagination_traits", "rdm_list"]:
    exec(import_cmd(components_dir, imp))



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
    def __init__(self, a_server_config, a_identifier, a_headers, a_subscription_timeout_seconds=5, a_source=EventSource.Owner):
        self.headers = a_headers
        self.server = a_server_config
        self.identifier = a_identifier
        self.data_queue = queue.Queue()
        self.event_source = a_source
        t = threading.Thread(target=self.event_stream_processor)
        t.daemon = True
        t.start()
        self.connected = False
        try:
            if(EventSource.Owner == self.event_source):
                self.wait_for_owner_subscription(a_timeout_seconds=a_subscription_timeout_seconds)
            else:
                self.wait_for_site_subscription(a_timeout_seconds=a_subscription_timeout_seconds)
        except EventManagerException as e:
            logging.info("Exception: {}".format(e))
            pass

    def wait_for_owner_subscription(self, a_timeout_seconds=None):
        return self.wait_for_data({"scope":"owner", "id":str(self.identifier)}, "subscribe", None, a_timeout_seconds)

    def wait_for_site_subscription(self, a_timeout_seconds=None):
        return self.wait_for_data({"scope":"site", "id":str(self.identifier)}, "subscribe", None, a_timeout_seconds)

    def wait_for_owner_key(self, a_timeout_seconds=None):
        expected_event_json = {
                "data": {
                    "type": "owner_key"
                },
                "type": "update",
                "service": "siteowner"
            }
        while True:
            item = self.wait_for_data({"scope":"owner", "id":str(self.identifier)}, "message", None, a_timeout_seconds)
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
            item = self.wait_for_data({"scope":"owner", "id":str(self.identifier)}, "message", None, a_timeout_seconds)
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
            item = None
            try:
                item = self.wait_for_data({"scope":"site", "id":str(self.identifier)}, "message", None, a_timeout_seconds)
            except (EventManagerException):
                return item
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
            item = self.wait_for_data({"scope":"owner", "id":str(self.identifier)}, "message", None, a_timeout_seconds)
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
            item = None
            try:
                item = self.wait_for_data({"scope":"site", "id":str(self.identifier)}, "message", None, a_timeout_seconds)
            except (EventManagerException):
                return item
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
            item = self.wait_for_data({"scope":"owner", "id":str(self.identifier)}, "message", None, a_timeout_seconds)
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
            item = self.wait_for_data({"scope":"site", "id":str(self.identifier)}, "message", None, a_timeout_seconds)
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
            item = self.wait_for_data(expected_topic, "message", None, a_timeout_seconds)
            try:
                if not compare_dict(expected_event, item["event"]):
                    continue
                return item
            except (KeyError, AttributeError, EventManagerException) as e:
                continue

    def wait_for_data(self, a_topic_json, a_type, a_event_list=None, a_timeout_seconds=None):
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
            except (queue.Empty):
                raise EventManagerException("Event Manager operation has timed out")

            try:
                if( self.topic_compare_equal(a_topic_json, item["topic"]) and a_type == item["type"] ):
                    if a_event_list is None:
                        return item
                    else: # further check for whether the supplied event details match this message and discard if not. This filters the wait further.
                        for i, expected_event in enumerate(a_event_list):
                            if compare_dict(a_expected=expected_event, a_actual=item["event"]):
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
                text = line.decode('ascii')
                if text:
                    if text.startswith(data_tag):
                        resp = json.loads(text[len(data_tag):])
                        self.data_queue.put(resp)

def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.DEBUG, a_arg_list=[arg_site_id])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    
    ev_mgr_site = HttpEventManager(a_server_config=server, a_identifier=args.site_id, a_headers=headers, a_subscription_timeout_seconds=None, a_source=EventSource.Site)

    while True:
        event = ev_mgr_site.wait_for_data({"scope":"site", "id":args.site_id}, "message", None, None)

        if event is not None:
            logging.info(json.dumps(event,indent=4))


if __name__ == "__main__":
    main()    
