#!/usr/bin/env python
import os
import sys
import websocket
import ssl
import json

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")
fixtures_dir = os.path.join(components_dir, "utils", "fixtures")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk", "datalogger_utils"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_machine_resource_configuration_file])
# << Argument handling

# >> Server & logging configuration
server_wss = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="wss")
server_https = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
logging.basicConfig(format=args.log_format, level=int(args.log_level))
logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server_wss.to_url(), args.dc, args.site_id))
# << Server & logging configuration

token = token_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server_https)
headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server_https)

degrees_per_km = 360.0 / 40000.0
km_per_hour = 100.0
km_per_second = km_per_hour / (60.0 * 60.0)
degrees_per_second = degrees_per_km * km_per_second


start = int(round(time.time() * 1000))
at = start

asset_machine_truck = Asset(asset_type="machine", asset_class="truck", a_oem="Bell", a_model="B30E", a_serial_number="633bdcad-7909-4ff9-90a1-fff95cbe3c95", a_asset_id="TR-007", a_asset_uuid="1c107231-217b-40d8-b438-79be0514d8a1")
asset_device_phone = Asset(asset_type="device", asset_class="Phone", a_oem="Samsung", a_model="Galaxy", a_serial_number="S10 Note+", a_asset_id="PH-007", a_asset_uuid="c504e67c-cdd7-47bf-85e6-913729c6cc43")

asset_context = AssetContext([asset_machine_truck, asset_device_phone], at)

site_detail = site_detail(server_https, headers, args.site_id)
datalogger_context = DataLoggerAggregatorSocket(server_wss, args.site_id, args.dc, "context", site_detail["region"])

payload=asset_machine_truck.make_payload(at)
logging.debug("Sending asset machine payload {}".format(json.dumps(payload, indent=4)))
ret = datalogger_context.send(json.dumps(payload))
logging.debug("Asset payload send returned {}".format(ret))

payload=asset_device_phone.make_payload(at)
logging.debug("Sending asset device payload {}".format(json.dumps(payload, indent=4)))
ret = datalogger_context.send(json.dumps(payload))
logging.debug("Device payload send returned {}".format(ret))

payload=asset_context.make_payload()
logging.debug("Sending asset context payload {}".format(json.dumps(payload, indent=4)))
ret = datalogger_context.send(json.dumps(payload))
logging.debug("Asset Context payload send returned {}".format(ret))

with open(args.machine_resource_configuration_file) as file:
    ret = datalogger_context.send(file.read())
    logging.debug("Resource Configuration payload send returned {}".format(ret))

rc_uuid = "777a93c0-ec0d-4994-b1fc-83271f5618f0"
latitude = -27.0
datalogger_update = DataLoggerAggregatorSocket(server_wss, args.site_id, args.dc, "update", site_detail["region"])
expected_update_count = 0
iterations = random.randint(10, 50)
beacon_expiry_epoch = 0
for i in range(0, iterations):
    expected_message_count = random.randint(50, 150)
    for j in range(0, expected_message_count):
        time.sleep(1)
        at = int(round(time.time() * 1000))
        latitude += degrees_per_second
        payload,beacon_expiry_epoch=make_haul_mfk_replicate_payload(asset_context, rc_uuid, latitude, 153.0, 0.0, 0.0, at, beacon_expiry_epoch)
        logging.debug("Sending replicate payload {}".format(json.dumps(payload, indent=4)))
        ret = datalogger_update.send(json.dumps(payload))
        logging.debug("Replicate payload send returned {}".format(ret))
        expected_update_count += 1

    expected_message_count = random.randint(50, 150)
    for j in range(0, expected_message_count):
        time.sleep(1)
        at = int(round(time.time() * 1000))
        latitude -= degrees_per_second
        payload,beacon_expiry_epoch=make_haul_mfk_replicate_payload(asset_context, rc_uuid, latitude, 153.0, 0.0, 0.0, at, beacon_expiry_epoch)
        logging.debug("Sending replicate payload {}".format(json.dumps(payload, indent=4)))
        ret = datalogger_update.send(json.dumps(payload))
        logging.debug(ret)
        expected_update_count += 1

# allow some time for dl-store to write the updates
