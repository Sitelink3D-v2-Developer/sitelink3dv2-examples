#!/usr/bin/env python

import argparse
import requests
import logging
import json
import logging
import os
import sys
import websocket
import ssl

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "mfk"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "tokens"))

from get_token      import *
from utils          import *
from args           import *
from mfk            import *


# Configure Arguments
arg_parser = argparse.ArgumentParser(description="Sample test rig to read Machine Forward Kinematics information for machines at a site.")
arg_parser = add_arguments_environment(arg_parser)
arg_parser = add_arguments_logging(arg_parser, logging.INFO)
arg_parser = add_arguments_site(arg_parser)
arg_parser = add_arguments_auth(arg_parser)
arg_parser.set_defaults()
args = arg_parser.parse_args()

# Configure Logging
logger = logging.getLogger("mfk")
logging.basicConfig(format=args.log_format, level=args.log_level)

# >> Server settings
session = requests.Session()

server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="wss")

logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

token = token_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

mfk_live_url = "{0}/mfk_live/v1/subscribe/{1}?access_token={2}".format(server.to_url(), args.site_id, token)
logging.info("connecting to web socket at {0}".format(mfk_live_url))
ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
ws.connect(mfk_live_url)

rc = ResourceConfiguration(json.loads(ws.recv()))

while True:
    msg_json = json.loads(ws.recv())
    print(json.dumps(msg_json,indent=4))
    if msg_json['type'] == "mfk::Replicate":
        rc.apply_manifest(msg_json['data']['manifest'])
