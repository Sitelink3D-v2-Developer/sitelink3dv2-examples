#!/usr/bin/env python
import os
import sys

# This example demonstrates the power of accessing historical raw data at a site using the Datalogger service. The Datalogger service provides
# historical data over a specified time period in a format consistent with the way data is provided live with MFK Live. That is to say that
# the data consists of three broad message types:
# 1. Events.
# 2. State.
# 3. MFK updates (Machine Forward Kinematics).
#
# This script is one of many potential applications for such raw data. Here, the available events, state and kinematic updates are
# written to separate text files in human readable form to provide a generic overview of the activity at the site in a machine agnostic way.
# The detailed resource (machine definition) files for every asset encountered in the data stream over the specified time interval are written
# in a "resources" folder nested under the output folder.

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk", "datalogger_payload", "datalogger_utils"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_datalogger_start_ms, arg_datalogger_end_ms])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
logging.basicConfig(format=args.log_format, level=int(args.log_level))
logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

logging.debug(headers)
dba_url = "{}/dba/v1/sites/{}/updates?startms={}&endms={}&category=low_freq".format(server.to_url(), args.site_id, args.datalogger_start_ms, args.datalogger_end_ms)
logging.debug("dba_url: {}".format(dba_url))

# get the datalogger data
response = session.get(dba_url, headers=headers)
response.raise_for_status()

resource_definitions = {}
assets = {}
mfk = {}

output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_target_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)

resources_dir = os.path.join(output_dir, "resources")
os.makedirs(resources_dir, exist_ok=True)

state_file_name = os.path.join(output_dir, "states.txt")
event_file_name = os.path.join(output_dir, "events.txt")
kinematics_file_name = os.path.join(output_dir, "kinematics.txt")
lift_file_name = os.path.join(output_dir, "lifts.txt")

payload_output_file = {}
payload_output_file["sitelink::Event"] = open(event_file_name, "w")
payload_output_file["sitelink::State"] = open(state_file_name, "w")
payload_output_file["mfk::Replicate"]  = open(kinematics_file_name, "w")
lift_file = open(lift_file_name, "w")
lift_file.write("Job, machine, truck, trailer, material, time, weight, job_uuid, last_material_lifted_for_job")

none_string = "[none]"

class Lift():
    def __init__(self, a_truck_name, a_trailer_name, a_material, a_weight, a_time):
        self.m_truck_name = a_truck_name
        self.m_trailer_name = a_trailer_name
        self.m_material = a_material
        self.m_weight = a_weight
        self.m_time = a_time

class Job():
    def __init__(self, a_job_uuid, a_open_time_ms):
        self.m_job_uuid = a_job_uuid
        self.m_material_pending_for_lift = none_string
        self.m_last_material_lifted = none_string
        self.m_lift_list = []

class DataloggerPayloadBase():
    def __init__(self, a_json):
        self.m_json = a_json
        
    def payload_type(self):
        return self.m_json["type"]
        
    def data_type(self):
        return self.m_json["data"]["type"]

# Log formatted payload specific data to the provided file handle.
def LogPayload(a_payload, a_file):
    a_file.write("\n{}".format(a_payload.format()))

# Main datalogger data processing loop
line_count = 0
job_uuid_dict = {}
ac_state_dict = {}
name_cache_dict = {}
ac_last_selected_job_dict = {}

for line in response.iter_lines():
    line_count += 1
    decoded_json = json.loads(base64.b64decode(line).decode('UTF-8'))

    # Before we intepret the payload, we fetch the Asset Context and Resource Configuration
    # definitions and initialise the MFK code for the Resource Configuration if required.
    #
    # This requires separate calls to the API so the results are cached to avoid the need to
    # query on every message.
    rc_uuid = ""
    rc_uuid_definition = None
    rc_uuid_mfk_component_instance = None
    try:    
        if decoded_json["type"] == "mfk::Replicate":
            rc_uuid = decoded_json['data']['rc_uuid']

            if not rc_uuid in resource_definitions:

                logging.debug("Getting Resource Configuration for RC_UUID {}".format(rc_uuid))
                resource_definitions[rc_uuid] = GetDbaResource(a_server_config=server, a_site_id=args.site_id, a_uuid=rc_uuid, a_headers=headers)

                mfk_rc = resource_definitions[rc_uuid]
                logging.debug("Resource Configuration: {}".format(json.dumps(mfk_rc,indent=4)))

                # Instantiate the MFK code for this Resource Configuration and cache it for subsequent queries.
                rc = ResourceConfiguration(mfk_rc)
                mfk[rc_uuid] = rc

                # Write the Resource Configuration to file for ease of inspection.
                resource_description = resource_definitions[rc_uuid]["description"] + " [" + resource_definitions[rc_uuid]["uuid"][0:8] + "]"
                resource_file_name = os.path.join(resources_dir, resource_description + ".json")
                resource_file = open(resource_file_name, "w")
                resource_file.write(json.dumps(resource_definitions[rc_uuid], indent=4))

            else:
                logging.debug("Already have Resource Configuration for RC_UUID {}".format(rc_uuid))

            rc_uuid_definition = resource_definitions[rc_uuid]["components"][0]["interfaces"]
            rc_uuid_mfk_component_instance = mfk[rc_uuid].components[0]
    except KeyError as err:
        logging.error("Error processing replicate resource configuration.")
        pass
    try:   
        ac_uuid = decoded_json['data']['ac_uuid']
        if not ac_uuid in assets:
            logging.debug("Getting Asset Context for AC_UUID {}".format(ac_uuid))
            assets[ac_uuid] = GetDbaResource(a_server_config=server, a_site_id=args.site_id, a_uuid=ac_uuid, a_headers=headers)

        else:
            logging.debug("Already have Asset Context for AC_UUID {}".format(ac_uuid))
    except KeyError as err:
        logging.error("Error processing replicate asset context.")
        pass

    # Now that the Resource Configuration and Asset Context information is available we process each
    # message before logging to file with the LogPayload function.
    #
    # State and Event payloads are self contained and can be written to file without extra processing.
    #
    # Replicate payloads however contain updates that must be applied to the MFK code instantiated for the
    # associated UUID. Once the replicate manifest is applied to the MFK code, the latter can be queried
    # by the LogPayload function for the latest kinematic information which is then written to file.
    try:
        payload = DataloggerPayload.payload_factory(decoded_json, assets, rc_uuid_definition, rc_uuid_mfk_component_instance)
        if payload is not None:
            logging.debug("Payload factory found {} {}".format(payload.payload_type(), payload.data_type()))
            logging.debug(payload.format())

            if payload.payload_type() == "mfk::Replicate":
                Replicate.load_manifests(mfk[rc_uuid], payload.manifest())
                mfk[rc_uuid].update_transforms()

            LogPayload(a_payload=payload, a_file=payload_output_file[payload.payload_type()])

            # The payload type may now contribute to our job list
            if isinstance(payload, DataloggerPayloadOnBoardWeighingOpen):
                # a new job has been birthed
                job_uuid = decoded_json["data"]["job_uuid"]
                if job_uuid not in job_uuid_dict:
                    job_uuid_dict[job_uuid] = Job(a_job_uuid=job_uuid, a_open_time_ms=decoded_json["at"])
                
                # track the most recently selected job for this AC so we can track its last know material independent of lifts
                ac_uuid = decoded_json["data"]["ac_uuid"]
                ac_last_selected_job_dict[ac_uuid] = job_uuid

            if isinstance(payload, DataloggerPayloadOnBoardWeighingClear):
                job_uuid = decoded_json["data"]["job_uuid"]
                this_job = job_uuid_dict[job_uuid]
                this_job.m_job_number = decoded_json["data"]["job_num"]
                ac_uuid = decoded_json["data"]["ac_uuid"]
                machine_name = get_machine_name_for_ac_uuid(assets, ac_uuid)
                for lift in this_job.m_lift_list:
                    seconds = lift.m_time / 1000
                    dt_object = datetime.datetime.fromtimestamp(seconds)
                    formatted_date = dt_object.strftime("%Y/%m/%d %H:%M:%S")
                    lift_string="{}, {}, {}, {}, {}, {}, {}, {}, {}".format(this_job.m_job_number, machine_name, lift.m_truck_name, lift.m_trailer_name, lift.m_material, formatted_date, lift.m_weight, job_uuid, this_job.m_last_material_lifted)
                    lift_file.write("\n"+lift_string)
                this_job = job_uuid_dict[decoded_json["data"]["job_uuid"]].m_lift_list.append(lift)

            def update_states(a_ac_uuid, a_state_name, a_state_uuid, a_ac_state_dict, a_name_cache_dict):
                if a_ac_uuid not in a_ac_state_dict:
                    a_ac_state_dict[a_ac_uuid] = {}
                
                if a_state_name not in a_ac_state_dict[a_ac_uuid]:
                    a_ac_state_dict[a_ac_uuid][a_state_name] = none_string

                # populate name cache if needed
                if a_state_uuid:
                    if a_state_name not in a_name_cache_dict:
                        a_name_cache_dict[a_state_name] = {}
                    if a_state_uuid not in a_name_cache_dict[a_state_name]:
                        state_value = get_rdm_object_name(a_server=server, a_site_id=args.site_id, a_uuid=a_state_uuid, a_view="_head", a_headers=headers)
                        a_name_cache_dict[a_state_name][a_state_uuid] = state_value

                a_ac_state_dict[a_ac_uuid][a_state_name] = a_name_cache_dict[a_state_name][a_state_uuid] if a_state_uuid else none_string

            if isinstance(payload, DataloggerPayloadState):
                state_name = decoded_json["data"]["state"]
                state_value = decoded_json["data"]["value"]
                ac_uuid = decoded_json["data"]["ac_uuid"]
                update_states(a_ac_uuid=ac_uuid, a_state_name=state_name, a_state_uuid=state_value, a_ac_state_dict=ac_state_dict, a_name_cache_dict=name_cache_dict)
                if state_name == "material" and len(state_value) > 0:
                    material_name = ac_state_dict[ac_uuid][state_name]
                    if ac_uuid in ac_last_selected_job_dict:
                        job_uuid_dict[ac_last_selected_job_dict[ac_uuid]].m_material_pending_for_lift = material_name
                
            if isinstance(payload, DataloggerPayloadOnBoardWeighingLift):
                weight = decoded_json["data"]["weight"]     
                ac_uuid = decoded_json["data"]["ac_uuid"]
                if ac_uuid not in ac_state_dict:
                    ac_state_dict[ac_uuid] = {}    

                job_uuid = decoded_json["data"]["job_uuid"]
                if job_uuid in job_uuid_dict:
                    lift = Lift(a_truck_name=ac_state_dict[ac_uuid]["truck"] if "truck" in ac_state_dict[ac_uuid] else none_string, a_trailer_name=ac_state_dict[ac_uuid]["trailer"] if "trailer" in ac_state_dict[ac_uuid] else none_string, a_material=ac_state_dict[ac_uuid]["material"] if "material" in ac_state_dict[ac_uuid] else none_string, a_weight=weight, a_time=decoded_json["at"])
                    this_job = job_uuid_dict[job_uuid]
                    this_job.m_lift_list.append(lift)
                    this_job.m_last_material_lifted = this_job.m_material_pending_for_lift
                    
    except KeyError as err:
        logging.error("Error processing replicate payload.")
        pass

logging.info("Processed {} lines".format(line_count))
