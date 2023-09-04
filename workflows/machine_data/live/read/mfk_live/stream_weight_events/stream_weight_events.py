#!/usr/bin/env python

# This example demonstrates how the Sitelink3D v2 API can be used to access detailed weight and state information streamed over one of our two
# live data technologies, MFK (Machine Forward Kinematics). State information is common to all Sitelink3D v2 compatible client software but
# weight information will be provided by client software specifically designed for weighing applications. Examples include the RDS LoadMaster
# and LoadEx on-board-weighing (OBW) systems and the Haul App running in excavator or loader mode.
#
# This example does not configure the site with the required RDM metadata for facilitating this demonstration but will stream live weight
# payloads for existing sites as the accompanying demonstration video illustrates. 
#
# The type of information available from MFK includes:
# 1. The weighing job identifier (both a UUID and a job number).
# 2. Individual lift payloads including the material and weight for each lift.
# 3. The target truck or trailer and their associated target tonnes (weight limits).
# 4. Whether the job is from a calibrated legal for trade weighing system. 
# 5. Loading machine identifier.
# 6. Aggregated weight for the job.
# 7. Lift count for the job.
#
# The following is an overview of this example:
# 1. Subscribe to MFK Live web socket at the site.
# 2. Loop over the messages received over the web socket processing the Sitelink::Event and Sitelink::State types.
# 3. For each event message, query the asset details referenced by the event using the "GetDbaResource" function.
# 4. Handle the events of data types "obw_open", "obw_lift" and "obw_clear" to track the progress of each weighing job.
# 5. Cache each state update as it is processed so that the current state can be associated with the weighing job once it is cleared.
# 6. Output processing details to the console as part of the message processing loop. More information is available by running this example in debug.
#
# Note that an instructional video of this example is provided in the "videos" folder accompanying this example script.


import os
import sys
import websocket
import ssl

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep) + len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk", "datalogger_utils", "rdm_pagination_traits", "rdm_list"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id])
# << Argument handling

# >> Server & logging configuration
server_wss = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="wss")
server_https = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
logging.basicConfig(format=args.log_format, level=int(args.log_level))
logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server_wss.to_url(), args.dc, args.site_id))
# << Server & logging configuration

token = token_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server_https)
headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server_https)

mfk_live_url = "{0}/mfk_live/v1/subscribe/{1}?access_token={2}".format(server_wss.to_url(), args.site_id, token)
logging.debug("connecting to web socket at {0}".format(mfk_live_url))
ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
ws.connect(mfk_live_url)

rc = ResourceConfiguration(json.loads(ws.recv())["data"])

assets = {}
jobs = {}
states = {}

while True:
    msg_json = json.loads(ws.recv())

    if msg_json['type'] == "sitelink::Event":
        # For all messages, we cache the asset context if the payload specifies one.
        # This allows us to interrogate machine names when processing event payloads.
        ac_uuid = ""
        try:
            ac_uuid = msg_json['ac_uuid']
            if ac_uuid not in assets:
                assets[ac_uuid] = GetDbaResource(a_server_config=server_https, a_site_id=args.site_id, a_uuid=ac_uuid, a_headers=headers)
        except KeyError:
            pass

        # Opening a weighing job is the first step in recording onboard weighing payloads.
        # Process open events here to start recording associated data in the jobs dictionary.
        if msg_json["data"]["type"] == "obw_open":
            machine_name = get_machine_name_for_ac_uuid(assets, ac_uuid)
            at = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
            job_uuid = msg_json["data"]["job_uuid"]
            jobs[job_uuid] = msg_json["data"]
            jobs[job_uuid]["at"] = at
            jobs[job_uuid]["lifts"] = []
            logging.debug("{}, machine '{}' opened weighing job {}".format(at, machine_name, job_uuid))

        # Cache the weights recorded for each lift as they come off the weighing system.
        # These will be summed when the job is cleared.
        if msg_json["data"]["type"] == "obw_lift":
            machine_name = get_machine_name_for_ac_uuid(assets, ac_uuid)
            at = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
            job_uuid = msg_json["data"]["job_uuid"]

            # add the job uuid if we missed the open event
            if job_uuid not in jobs:
                jobs[job_uuid] = {}
                jobs[job_uuid]["at"] = at
                jobs[job_uuid]["lifts"] = []

            # add the material to the lift event
            lift_json = msg_json["data"]
            lift_material_name = ""
            try:
                lift_material_uuid = states[ac_uuid]["material"]
                if len(lift_material_uuid) > 0:
                    lift_json["material_uuid"] = lift_material_uuid
                page_traits = RdmViewPaginationTraits(a_page_size="500", a_start="")
                rdm_list = query_rdm_by_domain_view(a_server_config=server_https, a_site_id=args.site_id, a_domain="sitelink", a_view="v_sl_material_by_name", a_headers=headers, a_params=page_traits.params())
                for material in rdm_list["items"]:
                    if material["id"] == lift_material_uuid:
                        lift_material_name = material["value"]["name"]
                        lift_json["material_name"] = lift_material_name
                        break
            except KeyError:
                pass

            # add the lift to the job data
            jobs[job_uuid]["lifts"].append(lift_json)
            logging.debug("{}, machine '{}' lifted {} tonnes for job {} {}".format(at, machine_name, '%.2f' % (lift_json["weight"]), job_uuid, "of {}".format(lift_material_name) if len(lift_material_name) > 0 else ""))

        # The clear event indicates that the weighing system has finished loading the truck.
        # We can hence aggregate the lift payloads and produce a final weight for the job.
        if msg_json["data"]["type"] == "obw_clear":
            machine_name = get_machine_name_for_ac_uuid(assets, ac_uuid)
            at = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
            job_uuid = msg_json["data"]["job_uuid"]

            # add the job uuid if we missed the open event
            if job_uuid not in jobs:
                jobs[job_uuid] = {}
                jobs[job_uuid]["at"] = at
                jobs[job_uuid]["lifts"] = []

            # aggregate the lifts by materials for this job now that it's closed
            total_weight = 0
            job_totals = {}
            job_totals["total"] = 0
            job_totals["count"] = 0
            job_totals["materials"] = {}
            for lift in jobs[job_uuid]["lifts"]:
                if "material_uuid" not in lift:
                    job_totals["total"] += lift["weight"]
                    if lift["weight"] > 0:
                        job_totals["count"] += 1
                    else:
                        job_totals["count"] -= 1
                else:
                    lift_material_uuid = lift["material_uuid"]
                    if lift_material_uuid not in job_totals["materials"]:
                        job_totals["materials"][lift_material_uuid] = {}
                        job_totals["materials"][lift_material_uuid]["total"] = 0
                        job_totals["materials"][lift_material_uuid]["count"] = 0
                        if "material_name" not in lift:
                            job_totals["materials"][lift_material_uuid]["material"] = "unknown_material_name"
                        else:
                            job_totals["materials"][lift_material_uuid]["material"] = lift["material_name"]
                    lift_weight = job_totals["materials"][lift_material_uuid]
                    lift_weight["total"] += lift["weight"]
                    if lift["weight"] > 0:
                        lift_weight["count"] += 1
                    else:
                        lift_weight["count"] -= 1
                total_weight += lift["weight"]

            output_string = "{}, machine '{}' cleared weighing job '{}' ({})".format(at, machine_name, job_uuid, msg_json["data"]["job_num"])

            # output the weight data
            if total_weight > 0:
                lift_count = len(jobs[job_uuid]["lifts"])
                output_string += " totalling {} tonnes".format('%.2f' % (total_weight))
                output_string += " (legal for trade)" if msg_json["data"]["legal_trade"] else " (not legal for trade)"
                # output the lift weight data
                if job_totals["count"] > 0:
                    lift_count = job_totals["count"]
                    output_string += " ({} tonnes over {} {} of undefined material)".format('%.2f' % (job_totals["total"]), lift_count, "lifts" if lift_count > 1 else "lift")
                for material in job_totals["materials"]:
                    lift_material = job_totals["materials"][material]
                    lift_count = lift_material["count"]
                    output_string += " ({} tonnes over {} {} of {})".format('%.2f' % (lift_material["total"]), lift_count, "lifts" if lift_count > 1 else "lift", lift_material["material"])

            # output the truck data
            truck_name = ""
            target_weight = ""
            try:
                truck_uuid = states[ac_uuid]["truck"]
                page_traits = RdmViewPaginationTraits(a_page_size="500", a_start="")
                rdm_list = query_rdm_by_domain_view(a_server_config=server_https, a_site_id=args.site_id, a_domain="sitelink", a_view="v_sl_truck_by_name", a_headers=headers, a_params=page_traits.params())
                for truck in rdm_list["items"]:
                    if truck["id"] == truck_uuid:
                        truck_name = truck["value"]["name"]
                        target_weight = truck["value"]["target"]
                        break
                if len(truck_name) > 0:
                    output_string += " for truck {} ({}) with target {} tonnes".format(truck_name ,truck_uuid, target_weight)
            except KeyError:
                pass

            del jobs[job_uuid]
            logging.info(output_string)

    # State information can be sent at any time during a job. We simply track the most recent state
    # for each machine so it can be queried when a clear event is received and processed.
    if msg_json['type'] == "sitelink::State":
        if msg_json["data"]["ns"] == "topcon.rdm.list":
            if msg_json["data"]["state"] == "truck":
                ac_uuid = msg_json["ac_uuid"]
                if ac_uuid not in states:
                    states[ac_uuid] = {}
                states[ac_uuid]["truck"] = msg_json["data"]["value"]

            if msg_json["data"]["state"] == "material":
                ac_uuid = msg_json["ac_uuid"]
                if ac_uuid not in states:
                    states[ac_uuid] = {}
                states[ac_uuid]["material"] = msg_json["data"]["value"]
