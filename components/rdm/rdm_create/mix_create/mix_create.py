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

def create_mix(a_site_id, a_server_config, a_mix_name, a_headers, a_porportion_list):
    
    mix_id = str(uuid.uuid4())

    mix_rdm_bean = MixRdmTraits.post_bean_json(a_name=a_mix_name, a_porportion_list=a_porportion_list)

    logging.debug(json.dumps(mix_rdm_bean, indent=4))

    url = "{0}/rdm_log/v1/site/{1}/domain/sitelink/events".format(a_server_config.to_url(), a_site_id)
    logging.debug ("Upload RDM to {}".format(url))
    
    json.dumps(mix_rdm_bean,indent=4)

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(mix_rdm_bean).encode('utf-8')).decode('utf-8') }
    logging.debug("Mix RDM payload: {}".format(json.dumps(mix_rdm_bean, indent=4)))

    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()   
    if response.status_code == 200:
        logging.info("Mix created.")
        logging.debug ("create mix returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))
    else:  
        logging.info("Mix creation unsuccessful. Status code {}: '{}'".format(response.status_code, response.text))
    return mix_id 

def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_rdm_mix_name, arg_rdm_mix_material_1_uuid, arg_rdm_mix_material_1_ratio, arg_rdm_mix_material_2_uuid, arg_rdm_mix_material_2_ratio])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=int(args.log_level))
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    proportion_list = [
        {
            "ratio": int(args.rdm_mix_material_1_ratio),
            "material": args.rdm_mix_material_1_uuid
        },
        {
            "ratio": int(args.rdm_mix_material_2_ratio),
            "material": args.rdm_mix_material_2_uuid
        }
    ]

    create_mix(a_site_id=args.site_id, a_server_config=server, a_mix_name=args.rdm_mix_name, a_headers=headers, a_porportion_list=proportion_list)


if __name__ == "__main__":
    main()    

