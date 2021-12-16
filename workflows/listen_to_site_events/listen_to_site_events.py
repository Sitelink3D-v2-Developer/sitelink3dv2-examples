#!/usr/bin/env python

import argparse
import requests
import logging
import argparse
import json
import logging
import os
import requests
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "utils"))

from get_token      import *
from utils          import *
from args           import *
from events         import *

logger = logging.getLogger("listen_to_events")

arg_parser = argparse.ArgumentParser(description="Print out event activity for a site")
arg_parser = add_arguments_environment(arg_parser)
arg_parser = add_arguments_logging(arg_parser, logging.INFO)
arg_parser = add_arguments_auth(arg_parser)
arg_parser = add_arguments_site(arg_parser)

arg_parser.set_defaults()
args = arg_parser.parse_args()
logging.basicConfig(format=args.log_format, level=args.log_level)

# >> Server settings
session = requests.Session()

server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
site_event_manager = HttpEventManager(a_server_config=server, a_identifier=args.site_id, a_source=EventSource.Site, a_headers=headers)

try:
    while True:
        item = site_event_manager.wait_for_data({"scope":"site", "id":str(args.site_id)}, "message", None)
        print(json.dumps(item,indent=4))
except KeyboardInterrupt:
    exit(0)