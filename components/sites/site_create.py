#!/usr/bin/python
import argparse
import json
import logging
import os
import requests
import uuid
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "metadata"))

from get_token import *
from utils import *
from metadata_traits import *

def create_site(a_site_name, a_dc, a_server_config, a_owner_id, a_latitude, a_longitude, a_phone, a_email, a_name, a_timezone, a_headers):

    create_site_url = "{0}/siteowner/v1/owners/{1}/create_site".format(a_server_config.to_url(), a_owner_id)

    payload_json = {
        "site_uuid": str(uuid.uuid4()),
        "name"  : a_site_name,
        "dc"    : a_dc,
        "region": "medium"
    }

    print(create_site_url)
    print(json.dumps(payload_json, indent=4)) 
    response = session.post(create_site_url, headers=a_headers, data=json.dumps(payload_json))
    site_details_json = response.json()
    print(json.dumps(site_details_json))
    logging.debug(json.dumps(site_details_json))
    site_id = site_details_json["identifier"]
    time.sleep(1)

    logging.debug(json.dumps(site_details_json))

    # Create site bean
    payload_json = SiteMetadataTraits.post_bean_json(a_site_name=a_site_name, a_latitude=a_latitude, a_longitude=a_longitude, a_phone=a_phone, a_email=a_email, a_name=a_name, a_timezone=a_timezone)

    data_encoded_json = {"data_b64": base64.b64encode(json.dumps(payload_json).encode('utf-8')).decode('utf-8')}
    create_site_rdm_url = "{0}/rdm_log/v1/site/{1}/domain/{2}/events".format(a_server_config.to_url(), site_id, "sitelink")
    response = session.post(create_site_rdm_url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()
    return site_id

def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Site Creation.")

    # script parameters:
    arg_parser.add_argument("--log-format", default='> %(asctime)-15s %(module)s %(levelname)s %(funcName)s:   %(message)s')
    arg_parser.add_argument("--log-level", default=logging.INFO)

    # server parameters:
    arg_parser.add_argument("--dc", default="SR_EDGE_DC")
    arg_parser.add_argument("--env", default="", help="deploy env (which determines server location)")
    arg_parser.add_argument("--jwt", default="", help="jwt")

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

    header_json = to_jwt_token_header(a_jwt_token=args.jwt)

    logging.info("Running {0} for server={1} dc={2} owner={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.owner_id))

    site_id = create_site(a_site_name=args.site_name, a_dc=args.dc, a_server_config=server, a_owner_id=args.owner_id, a_latitude=args.site_latitude, a_longitude=args.site_longitude, a_phone=args.site_contact_phone, a_email=args.site_contact_email, a_name=args.site_contact_name, a_timezone=args.site_timezone, a_headers=header_json)

    logging.info("Site {0} successfully created \n".format(site_id, indent=4))


if __name__ == "__main__":
    main()    