#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["utils", "get_token", "rdm_traits", "args"]:
    exec(import_cmd(components_dir, imp))

def create_site(a_site_name, a_dc, a_server_config, a_owner_id, a_latitude, a_longitude, a_phone, a_email, a_name, a_timezone, a_headers):

    create_site_url = "{0}/siteowner/v1/owners/{1}/create_site".format(a_server_config.to_url(), a_owner_id)

    payload_json = {
        "site_uuid": str(uuid.uuid4()),
        "name"  : a_site_name,
        "dc"    : a_dc,
        "region": "medium"
    }

    logging.info("post site creation to site owner {}".format(create_site_url))
    logging.debug(json.dumps(payload_json, indent=4))
    response = session.post(create_site_url, headers=a_headers, data=json.dumps(payload_json))
    site_details_json = response.json()
    logging.debug("response from site owner {}".format(json.dumps(site_details_json, indent=4)))
    site_id = site_details_json["identifier"]
    time.sleep(1)

    # Create site bean
    payload_json = SiteRdmTraits.post_bean_json(a_site_name=a_site_name, a_latitude=a_latitude, a_longitude=a_longitude, a_phone=a_phone, a_email=a_email, a_name=a_name, a_timezone=a_timezone)
    data_encoded_json = {"data_b64": base64.b64encode(json.dumps(payload_json).encode('utf-8')).decode('utf-8')}
    create_site_rdm_url = "{0}/rdm_log/v1/site/{1}/domain/{2}/events".format(a_server_config.to_url(), site_id, "sitelink")
    logging.info("post site definition to RDM {}".format(create_site_rdm_url))
    logging.debug(json.dumps(payload_json, indent=4))
    response = session.post(create_site_rdm_url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()
    rdm_json = response.json()
    logging.debug("response from RDM {}".format(json.dumps(rdm_json, indent=4)))
    return site_id

def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Site Creation.")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    # request parameters:
    arg_parser.add_argument("--owner_id", help="Organization ID", required=True)
    arg_parser.add_argument("--site_name", help="Name for the site", required=True)
    arg_parser.add_argument("--site_latitude", help="Site Latitude",  default="-27.4699")
    arg_parser.add_argument("--site_longitude", help="Site Longitude", default="153.0252")
    arg_parser.add_argument("--site_timezone", help="Site Timezone", default="Australia/Brisbane")
    arg_parser.add_argument("--site_contact_name", help="Site Contact Name")
    arg_parser.add_argument("--site_contact_email", help="Site Contact Email")
    arg_parser.add_argument("--site_contact_phone", help="Site Contact Phone")

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments


    # << Server settings
    session = requests.Session()

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    logging.info("Running {0} for server={1} dc={2} owner={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.owner_id))

    site_id = create_site(a_site_name=args.site_name, a_dc=args.dc, a_server_config=server, a_owner_id=args.owner_id, a_latitude=args.site_latitude, a_longitude=args.site_longitude, a_phone=args.site_contact_phone, a_email=args.site_contact_email, a_name=args.site_contact_name, a_timezone=args.site_timezone, a_headers=headers)

    logging.info("Site {0} successfully created \n".format(site_id, indent=4))


if __name__ == "__main__":
    main()    