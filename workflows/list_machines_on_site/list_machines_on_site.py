#!/usr/bin/env python

import argparse
import base64
import json
import requests
import logging

import argparse
import datetime
import json
import logging
import os
import requests
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "smartview"))

from get_token      import *
from utils          import *
from smartview      import *

logger = logging.getLogger("smartview-app")


arg_parser = argparse.ArgumentParser(description="Sample test rig to connect to a SmartApp and print its responses")
arg_parser.add_argument("--app"  , help="the SmartApp required", default="topcon/machines/machine_list:fc271df3-0df7-4f83-b8f7-e5f806bac959")
arg_parser.add_argument("--start", help="""Value for start. A JSON object detailed elsewhere.""", default="""{"from":"continuous"}""")
arg_parser.add_argument("--token", help="JWT to access server")
arg_parser.add_argument("--keep-alive", help="maximum interval between messages being sent", default="10s")
arg_parser.add_argument("--url"  , help="URL of server", default="https://api.edge-router:443")
arg_parser.add_argument("--args" , help="""extra arguments passed to the SmartApp. String of the form "a=1&b=2&b=3".""")

arg_parser.add_argument("--log-format", default='> %(asctime)-15s %(module)s %(levelname)s %(funcName)s:   %(message)s')
arg_parser.add_argument("--log-level", default=logging.INFO)

# server parameters:
arg_parser.add_argument("--env", default="", help="deploy env (which determines server location)")
arg_parser.add_argument("--oauth_id", default="", help="oauth-id")
arg_parser.add_argument("--oauth_secret", default="", help="oauth-secret")
arg_parser.add_argument("--oauth_scope", default="", help="oauth-scope")

arg_parser.add_argument("--dc", default="qa")
arg_parser.add_argument("--site_id", default="", help="Site Identifier")
arg_parser.set_defaults()
args = arg_parser.parse_args()
logging.basicConfig(format=args.log_format, level=args.log_level)

# >> Server settings
session = requests.Session()

server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

token = get_token(a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
header_json = to_bearer_token_content_stream_header(token["access_token"])

logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))


sv = SmartView(args.app).configure(server.to_url(), args.site_id, header_json)
try:
    for line in sv.stream_data(args.start, args.args, args.keep_alive):
        print(line)
except KeyboardInterrupt:
    exit(0)
