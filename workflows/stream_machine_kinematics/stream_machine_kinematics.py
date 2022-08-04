#!/usr/bin/env python
import os
import sys
import websocket
import ssl
import json

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk"]:
    exec(import_cmd(components_dir, imp))

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

server_wss = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="wss")
server_https = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")

logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server_wss.to_url(), args.dc, args.site_id))

token = token_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server_https)

mfk_live_url = "{0}/mfk_live/v1/subscribe/{1}?access_token={2}".format(server_wss.to_url(), args.site_id, token)
logging.info("connecting to web socket at {0}".format(mfk_live_url))
ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
ws.connect(mfk_live_url)

rc = ResourceConfiguration(json.loads(ws.recv()))

while True:
    msg_json = json.loads(ws.recv())
    print(json.dumps(msg_json,indent=4))
    if msg_json['type'] == "mfk::Replicate":
        Replicate.load_manifests(rc, msg_json['data']['manifest'])
