#!/usr/bin/env python

# ------------------------------------------------------------------------------
# Create a site and configure it for material haulage.
# ------------------------------------------------------------------------------

import sys
import os
from datetime       import datetime

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "site_create", "delay_create", "material_create", "region_create", "task_create", "auth_code_create"]:
    exec(import_cmd(components_dir, imp))

# >> Arguments
arg_parser = argparse.ArgumentParser(description="Create a complete site.")

# script parameters:
arg_parser = add_arguments_logging(arg_parser, logging.INFO)

# server parameters:
arg_parser = add_arguments_environment(arg_parser)
arg_parser = add_arguments_auth(arg_parser)

# site creation parameters
arg_parser.add_argument("--owner_id", help="Organization ID", required=True)
arg_parser.add_argument("--site_name", help="Name for the site", required=True)
arg_parser.add_argument("--site_latitude", help="Site Latitude",  default="-27.4699")
arg_parser.add_argument("--site_longitude", help="Site Longitude", default="153.0252")
arg_parser.add_argument("--site_timezone", help="Site Timezone", default="Australia/Brisbane")
arg_parser.add_argument("--site_contact_name", help="Site Contact Name")
arg_parser.add_argument("--site_contact_email", help="Site Contact Email")
arg_parser.add_argument("--site_contact_phone", help="Site Contact Phone")
arg_parser.add_argument("--site_auth_code", help="PIN used by clients to connect to this site", required=True)

# region creation parameters
arg_parser.add_argument("--region_discovery_verticies_file", help="A file containing points outlining a region used for site discovery", required=True)
arg_parser.add_argument("--region_load_verticies_file", help="A file containing points outlining a region used for auto loading haul trucks", required=True)
arg_parser.add_argument("--region_dump_verticies_file", help="A file containing points outlining a region used for auto dumping haul trucks", required=True)

arg_parser.set_defaults()
args = arg_parser.parse_args()
logging.basicConfig(format=args.log_format, level=args.log_level)
# << Arguments

# >> Server settings
session = requests.Session()

server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

logging.info("Running {0} for server={1} dc={2} owner={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.owner_id))


###### First create a site
logging.info("creating site")
site_id = create_site(a_site_name=args.site_name, a_dc=args.dc, a_server_config=server, a_owner_id=args.owner_id, a_latitude=args.site_latitude, a_longitude=args.site_longitude, a_phone=args.site_contact_phone, a_email=args.site_contact_email, a_name=args.site_contact_name, a_timezone=args.site_timezone, a_headers=headers)
logging.info("Site {0} successfully created.".format(site_id, indent=4))

###### Create some materials that we can reference as haul mixins when we later create regions. One basic material and another with some additional optional configuration.
logging.info("creating materials")
material_waste_id = create_material(a_site_id=site_id, a_server_config=server, a_material_name="Waste", a_headers=headers)

accepted_measurement_volume =  MaterialRdmTraits.AcceptedMeasurement(a_axis="volume", a_units="cubic_metres")
conversion_volume = MaterialRdmTraits.Conversion(a_accepted_measurement=accepted_measurement_volume, a_factor=10.1)

accepted_measurement_weight = MaterialRdmTraits.AcceptedMeasurement(a_axis="weight", a_units="metric_tons")
conversion_weight = MaterialRdmTraits.Conversion(a_accepted_measurement=accepted_measurement_weight, a_factor=100.2)

state_excavated = MaterialRdmTraits.AdditionalState(a_name="Excavated", a_conversions=[conversion_volume, conversion_weight])

default_measurement_volume =  MaterialRdmTraits.AcceptedMeasurement(a_axis="volume", a_units="cubic_metres")
default_measurement_weight = MaterialRdmTraits.AcceptedMeasurement(a_axis="weight", a_units="metric_tons")

conversion_default_left = MaterialRdmTraits.Conversion(a_accepted_measurement=default_measurement_volume, a_factor=1)
conversion_default_right = MaterialRdmTraits.Conversion(a_accepted_measurement=default_measurement_weight, a_factor=1)

paired_conversion = MaterialRdmTraits.PairedConversion(a_left_conversion=conversion_default_left, a_right_conversion=conversion_default_right)
state_default = MaterialRdmTraits.DefaultState(a_name="Default", a_paired_conversions=[paired_conversion])

haul_mixin = MaterialRdmTraits.Haul(a_operator_entry_measurement=accepted_measurement_volume, a_operator_entry_state_name=state_default.name)

material_overburden_id = create_material(a_site_id=site_id, a_server_config=server, a_material_name="Overburden", a_headers=headers, a_accepted_measurements=[accepted_measurement_volume,accepted_measurement_weight], a_default_state=state_default, a_additional_states=[state_excavated], a_haul_mixin = haul_mixin)

load_waste_region_haul_mixin = RegionRdmTraits.Haul(a_autoload_material_uuid=material_waste_id)
dump_waste_region_haul_mixin = RegionRdmTraits.Haul(a_autoload_material_uuid=None, a_autodump_material_uuid=material_waste_id)

###### Now add some regions: Site discovery to allow easy connection, a load region and a dump region for the haul trucks to use.
logging.info("creating regions")
create_region(a_region_name="Discovery", a_site_id=site_id, a_server_config=server, a_verticies_file=args.region_discovery_verticies_file, a_headers=headers, a_discoverable=True)
create_region(a_region_name="Load Waste", a_site_id=site_id, a_server_config=server, a_verticies_file=args.region_load_verticies_file, a_headers=headers, a_discoverable=False, a_color="#088a08", a_coordinate_system="wgs84", a_opacity=50, a_haul_mixin=load_waste_region_haul_mixin)
create_region(a_region_name="Dump Waste", a_site_id=site_id, a_server_config=server, a_verticies_file=args.region_dump_verticies_file, a_headers=headers, a_discoverable=False, a_color="#ff7f00", a_coordinate_system="wgs84", a_opacity=50, a_haul_mixin=dump_waste_region_haul_mixin)


###### Add some delays to enable auto delay prompts when trucks are stationary
logging.info("creating delays")
delays = ["Fuel", "Traffic", "Queueing", "Breakdown", "Maintenance"]
for idx,item in enumerate(delays):
    create_delay(a_site_id=site_id, a_server_config=server, a_delay_name=item, a_delay_code=str(idx), a_headers=headers)


###### Create a descriptively named Task for Hauler operators to select on their apps
logging.info("creating task")
rj = create_task(a_server_config=server, a_site_id=site_id, a_task_name="Haul Waste", a_headers=headers)
logging.debug("Task RDM post returned\n{0}".format(json.dumps(rj,indent=4)))

###### Lastly an Auth Code so that applications can connect to this site
logging.info("creating auth code")
create_auth_code(a_server_config=server, a_site_id=site_id, a_code_name="Hauling Code", a_code_pin=args.site_auth_code, a_headers=headers)