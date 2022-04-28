#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "get_token", "rdm_traits"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

def create_material(a_site_id, a_server_config, a_material_name, a_headers, a_accepted_measurements=None, a_default_state=None, a_additional_states=None, a_haul_mixin=None, a_rds_mixin=None):
    
    material_id = str(uuid.uuid4())
    material_rdm_bean = MaterialRdmTraits.post_bean_json(a_material_name=a_material_name, a_id=material_id, a_accepted_measurements=a_accepted_measurements, a_default_state=a_default_state, a_additional_states=a_additional_states, a_haul_mixin = a_haul_mixin, a_rds_mixin = a_rds_mixin)

    logging.debug(json.dumps(material_rdm_bean, indent=4))

    url = "{0}/rdm_log/v1/site/{1}/domain/sitelink/events".format(a_server_config.to_url(), a_site_id)
    logging.debug ("Upload RDM to {}".format(url))
    
    json.dumps(material_rdm_bean,indent=4)

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(material_rdm_bean).encode('utf-8')).decode('utf-8') }
    logging.debug("Material RDM payload: {}".format(json.dumps(material_rdm_bean, indent=4)))

    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()   
    if response.status_code == 200:
        logging.info("Material created.")
        logging.debug ("create material returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))
    else:  
        logging.info("Material creation unsuccessful. Status code {}: '{}'".format(response.status_code, response.text))
    return material_id 

def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_rdm_material_name])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

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
    rds_mixin = MaterialRdmTraits.RDS(a_density=3, a_descriptions=["customer material", "low cost"], a_price=10.2, a_regulation="ce")

    logging.debug("Accepted measurement")
    logging.debug(json.dumps(accepted_measurement_volume.to_json(), indent=4))
    logging.debug("State conversion")
    logging.debug(json.dumps(conversion_volume.to_json(), indent=4))

    logging.debug("State")
    logging.debug(json.dumps(state_excavated.to_json(), indent=4))
                                                                                                                                                                                                                                                                  
    material_id = create_material(a_site_id=args.site_id, a_server_config=server, a_material_name=args.rdm_material_name, a_headers=headers, a_accepted_measurements=[accepted_measurement_volume,accepted_measurement_weight], a_default_state=state_default, a_additional_states=[state_excavated], a_haul_mixin = haul_mixin, a_rds_mixin = rds_mixin)


if __name__ == "__main__":
    main()    

