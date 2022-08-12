#!/usr/bin/env python
import os
import sys
from textwrap import indent
import websocket
import ssl

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep) + len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk", "datalogger_utils", "rdm_pagination_traits", "rdm_list"]:
    exec(import_cmd(components_dir, imp))

# Configure Arguments
arg_parser = argparse.ArgumentParser(description="Sample test rig to read Machine Forward Kinematics information for machines at a site.")
arg_parser = add_arguments_environment(arg_parser)
arg_parser = add_arguments_logging(arg_parser, logging.DEBUG)
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
headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server_https)

mfk_live_url = "{0}/mfk_live/v1/subscribe/{1}?access_token={2}".format(server_wss.to_url(), args.site_id, token)
logging.debug("connecting to web socket at {0}".format(mfk_live_url))
ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
ws.connect(mfk_live_url)

rc = ResourceConfiguration(json.loads(ws.recv()))

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

            jobs[job_uuid]["lifts"].append(msg_json["data"])
            logging.debug("{}, machine '{}' lifted {} tonnes for job {}".format(at, machine_name, msg_json["data"]["weight"], job_uuid))

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

            # aggregate the lifts for this job now that it's closed
            total_weight = 0
            try:
                for i, lift in enumerate(jobs[job_uuid]["lifts"]):
                    total_weight += lift["weight"]
            except KeyError:
                pass

            output_string = "{}, machine '{}' cleared weighing job '{}' ({})".format(at, machine_name, job_uuid, msg_json["data"]["job_num"])

            material_name = ""
            try:
                material_uuid = states[ac_uuid]["material"]
                page_traits = RdmPaginationTraits(a_page_size="500", a_start="")

                rdm_list = query_rdm_by_domain_view(a_server_config=server_https, a_site_id=args.site_id, a_domain="sitelink", a_view="v_sl_material_by_name", a_headers=headers, a_params=page_traits.params())
                for material in rdm_list["items"]:
                    if material["id"] == material_uuid:
                        material_name = material["value"]["name"]
                        break
            except KeyError:
                pass

            if total_weight > 0:
                lift_count = len(jobs[job_uuid]["lifts"])
                total_weight = '%.3f'%(total_weight)
                output_string += " totalling {} tonnes {}".format(total_weight, "of {}".format(material_name) if len(material_name) > 0 else "")
                output_string += " over {} {}".format(lift_count, "lifts" if lift_count > 1 else "lift")
                output_string += " (trade legal)" if msg_json["data"]["legal_trade"] else " (not trade legal)"

            truck_name = ""
            target_weight = ""
            try:
                truck_uuid = states[ac_uuid]["truck"]
                page_traits = RdmPaginationTraits(a_page_size="500", a_start="")

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
