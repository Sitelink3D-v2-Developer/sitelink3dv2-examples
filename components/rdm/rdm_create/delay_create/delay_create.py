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

def create_delay(a_site_id, a_server_config, a_delay_name, a_delay_code, a_headers):
    
    delay_rdm_bean = DelayRdmTraits.post_bean_json(a_delay_name=a_delay_name, a_id=str(uuid.uuid4()), a_delay_code=a_delay_code)

    url = "{0}/rdm_log/v1/site/{1}/domain/sitelink/events".format(a_server_config.to_url(), a_site_id)
    logging.debug ("Upload RDM to {}".format(url))
    
    json.dumps(delay_rdm_bean,indent=4)

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(delay_rdm_bean).encode('utf-8')).decode('utf-8') }
    logging.debug("Delay RDM payload: {}".format(json.dumps(delay_rdm_bean, indent=4)))

    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()
    if response.status_code == 200:
        logging.info("Delay created.")
        logging.debug ("create delay returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))
    else:  
        logging.info("Delay creation unsuccessful. Status code {}: '{}'".format(response.status_code, response.text))


def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_rdm_delay_name, arg_rdm_delay_code])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=int(args.log_level))
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    create_delay(a_site_id=args.site_id, a_server_config=server, a_delay_name=args.rdm_delay_name, a_delay_code=args.rdm_delay_code, a_headers=headers)

if __name__ == "__main__":
    main()    

