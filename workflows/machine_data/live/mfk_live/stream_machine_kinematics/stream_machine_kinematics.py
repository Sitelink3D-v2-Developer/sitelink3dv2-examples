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

for imp in ["args", "utils", "get_token", "mfk", "datalogger_utils"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_log_level=logging.DEBUG, a_arg_list=[arg_site_id])
# << Argument handling

# >> Server & logging configuration
server_wss = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="wss")
server_https = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
logging.basicConfig(format=args.log_format, level=args.log_level)
logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server_wss.to_url(), args.dc, args.site_id))
# << Server & logging configuration

token = token_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server_https)

mfk_live_url = "{0}/mfk_live/v1/subscribe/{1}?access_token={2}".format(server_wss.to_url(), args.site_id, token)
logging.info("connecting to web socket at {0}".format(mfk_live_url))
ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
ws.connect(mfk_live_url)

resource_definitions = {}

while True:
    msg_json = json.loads(ws.recv())

    if msg_json['type'] == "mfk::ResourceConfiguration":
        ac_uuid = msg_json['ac_uuid']
        logging.info("Received Resource Configuration for Asset Context {}".format(ac_uuid))
        resource_definitions[ac_uuid] = msg_json['data']

    if msg_json['type'] == "mfk::Replicate":
        ac_uuid = msg_json['ac_uuid']
        logging.info("Received Replicate update for Asset Context {}".format(ac_uuid))
        resource_config_processor = UpdateResourceConfigurationProcessor(a_resource_config_uuid=ac_uuid, a_resource_config_dict=resource_definitions)
        Replicate.load_manifests(resource_config_processor, msg_json['data']['manifest'])
        resource_config_processor.update_transforms()
