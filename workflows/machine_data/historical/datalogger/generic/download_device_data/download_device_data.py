#!/usr/bin/env python

# This example demonstrates the power of accessing historical raw data at a site using the Datalogger service. The Datalogger service provides
# historical data over a specified time period in a format consistent with the way data is provided live with MFK Live. That is to say that
# the data consists of three broad message types:
# 1. Events (not used in this example).
# 2. State.
# 3. MFK updates (Machine Forward Kinematics).
#
# This script is one of many potential applications for such raw data. Here, a detailed report of all (low frequency) machine positions along
# with associated state, position and AsBuilt related flags as well as RDM metadata such as selected Task and design information is produced.
# Interpreting raw Datalogger data enables API consumers to build their own customized reports or otherwise process data for statistical or
# any other purpose.
#
# The following is an overview of this example:
# 1. Extract raw data from the Datalogger (DBA) Service and iterate over the resulting lines.
# 2. Cache state information so that the most recent state is available to be output when kinematic updates are received.
# 3. Process mfk::Replicate packets containing binary encoded kinematic updates, conditioning the data to be output as a CSV line.

def particular_from_design_type(a_design_type):
    if(a_design_type == "Lines"):
        return "LN3"
    elif(a_design_type == "Planes"):
        return "PL3"
    elif(a_design_type == "Points"):
        return "PT3"
    elif(a_design_type == "Roads"):
        return "RD3"
    elif(a_design_type == "Surfaces"):
        return "TN3"
    else:
        return "Invalid"

import logging
import os
import sys
from dateutil import tz
import urllib

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk", "site_detail", "datalogger_utils", "transform", "rdm_pagination_traits", "rdm_list", "rdm_query_object"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_time_start_ms, arg_time_end_ms, arg_datalogger_output_file_name, arg_datalogger_output_folder])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
logging.basicConfig(format=args.log_format, level=int(args.log_level))
logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
# remove any previous error files in case one is generated from below exception handling
target_dir=args.datalogger_output_folder

output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_target_dir=target_dir, a_site_id=args.site_id)
os.makedirs(output_dir, exist_ok=True)
error_file_name = os.path.join(output_dir, "error.txt")

try:
    os.remove(error_file_name)
    logging.info("Removed previous error file.")
except OSError as error:
    pass

try:
    report_file_name = os.path.join(output_dir, args.datalogger_output_file_name)
    report_file = open(report_file_name, "w")
    
    report_file.write("Device, Machine, Name, Modified At Time (UTC), Design Type, Count, Feature Name, Description, Color, coordinate 1, coordinate 2, coordinate 3\n")
        

    rdm_view_list = GetTransform(a_server=server, a_site_id=args.site_id, a_headers=headers)
    if len(rdm_view_list["items"]) == 0:
        raise SitelinkProcessingError("Couldn't find site transformation list.")
    transform_rev = rdm_view_list["items"][0]["value"]["_rev"]
    logging.debug(json.dumps(rdm_view_list,indent=4))

    start=["site"] 
    end=["site", None]
    rdm_url = "{}/rdm/v1/site/{}/domain/sitelink/view/_head?limit=500".format(server.to_url(), args.site_id)
    params={}
    params["start"] = base64.urlsafe_b64encode(json.dumps(start).encode('utf-8')).decode('utf-8').rstrip("=")
    params["end"] = base64.urlsafe_b64encode(json.dumps(end).encode('utf-8')).decode('utf-8').rstrip("=")
    response = session.get(rdm_url, headers=headers, params=params)
    if response.status_code != 200:
        raise SitelinkProcessingError("Couldn't find site transformation list.")

    site_json = response.json()    
    logging.debug(json.dumps(site_json,indent=4))
    site_rev=site_json["items"][0]["value"]["_rev"]

    # get site assets to pair devices with machines for output
    assets = GetDbaAssets(a_server_config=server, a_site_id=args.site_id, a_headers=headers)
    asset_items = assets["items"]

    deviceDesignObject_by_deviceURN = {}
    # first query the design objects in RDM by device URN
    def callback(a_item):

        if a_item["value"]["designType"] == "Planes":
            return

        # check whether the time of this item fits within the requested window
        if int(a_item["value"]["createdAt"]) <  int(args.time_start_ms) or int(a_item["value"]["createdAt"]) > int(args.time_end_ms):
            return
      
        urn = a_item["value"]["deviceURN"]
        if urn not in deviceDesignObject_by_deviceURN.keys():
            deviceDesignObject_by_deviceURN[urn] = {} 
        deviceDesignObject_by_deviceURN[urn][a_item["value"]["name"]] = a_item["value"]

        urn_toks = urn.split(":")
        dev_hash = "{} {} ({})".format(urn_toks[6], urn_toks[8], urn_toks[12])

        machine_name = "[machine name unavailable]"
        for asset in asset_items:
            if asset["urn"] == urn:
                for machine in asset_items:
                    if machine["id"] == asset["last_seen_with"][0]:
                        machine_urn = machine["urn"] 
                        machine_name = urllib.parse.unquote(machine_urn.split(":")[-1])
                        break

        utc_time = datetime.datetime.fromtimestamp(int(a_item["value"]["createdAt"])/1000,tz=tz.UTC)
        line_prefix = "{},{},{},{},{},{}".format( dev_hash, machine_name, a_item["value"]["name"], utc_time, a_item["value"]["designType"], a_item["value"]["count"] )

        current_dir = os.path.dirname(os.path.realpath(__file__))
        device_output_dir = os.path.join(output_dir, a_item["value"]["deviceURN"].replace(':', "-"))

        converted_dir = os.path.join(device_output_dir, "converted")
        rdm_file_name = a_item["value"]["name"]

        os.makedirs(converted_dir, exist_ok=True)

        particular = particular_from_design_type(a_item["value"]["designType"])
        base = "{}/designfile/v1/sites/{}/design_files/{}?design_type={}&particular=".format(
            server.to_url(), args.site_id, a_item["value"]["doFileUUID"], a_item["value"]["designType"])
        
        url_landjson = ["{}GEOJSON".format(base), "geojson", converted_dir]
        for url, ext, target in [url_landjson]:
            response = session.get("{}{}".format(url,"&site_rev={}&transform_gc3_rev={}".format(site_rev,transform_rev)), headers=headers, stream=True)
            response.raise_for_status()

            chunks = []
            for chunk in tqdm(response.iter_content()):
                chunks.append(chunk)

            full_content = b''.join(chunks)
            parsed_data = json.loads(full_content)

            # now we write a row to csv per point
            features = parsed_data["features"]
            for feature in features:
                point_str = ",{},{},{},{},{},{}".format(feature["properties"]["name"], feature["properties"]["description"], feature["properties"]["color"],feature["geometry"]["coordinates"][0][0], feature["geometry"]["coordinates"][0][1], feature["geometry"]["coordinates"][0][2])
                report_file.write("{}{}\n".format(line_prefix, point_str))

    query_rdm_object_properties_in_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink", a_view="v_sl_deviceDesignObject_by_deviceURN", a_headers=headers, a_page_traits=RdmViewPaginationTraits(a_page_size="100", a_start=""), a_callback=callback)
    keys = deviceDesignObject_by_deviceURN.keys()

    logging.debug(json.dumps(deviceDesignObject_by_deviceURN, indent=4))

except SitelinkProcessingError as e:
    log_and_exit_on_error(a_message=e, a_target_dir=output_dir)    
