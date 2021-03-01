#!/usr/bin/python
import argparse
import logging
import os
import sys
import requests
import json
import base64
import uuid
import time

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))

from get_token import *
from utils import *


session = requests.Session()


def query_file_features(a_server_config, a_site_id, a_file_upload_uuid, a_file_name, a_headers):

    url = "{0}/designfile/v1/sites/{1}/files/{2}/feature_jobs".format(a_server_config.to_url(), a_site_id, a_file_upload_uuid)

    # we need the provide file name to tell design file what the file extension is. only RDM knows the file name and design file doesn't talk with RDM.
    data_payload = { "file_name" : a_file_name }
    response = session.post(url, headers=a_headers, data=json.dumps(data_payload))
    response.raise_for_status()
    job_reponse_json = response.json()
    logging.debug ("post feature job returned {0}\n{1}".format(response.status_code, json.dumps(job_reponse_json,indent=4)))

    job_id = job_reponse_json["id"]

    # Now get the features from the job via long poll

    # ------------------------------------------------------------------------------
    logging.debug ("Get result of feature query job via long poll:")
    # ------------------------------------------------------------------------------

    url = "{0}/designfile/v1/sites/{1}/feature_jobs/{2}".format(a_server_config.to_url(), a_site_id, job_id)

    response = session.get(url, headers=a_headers, params={"long_poll":True})
    response.raise_for_status()
    rj = response.json()
    logging.debug ("get feature job returned {0}\n{1}".format(response.status_code, json.dumps(rj,indent=4)))

    # Select all returned features to post an import job. This will extract the design data from the file.
    file_uuid = rj["file_uuid"]
    features_to_import = []
    feature_list = rj["features"]
    

    for i, feature in enumerate(feature_list):
    
        v = {k : feature.get(k) for k in ["design_type", "filter", "source_name"] if k in feature}
        features_to_import.append(v)
    return features_to_import


def import_file_features(a_server_config, a_site_id, a_file_upload_uuid, a_file_name, a_features, a_headers):
    data_payload = { "file_name": a_file_name,
        "import_uuid":str(a_file_upload_uuid),
        "imports" : a_features
    }

    logging.debug ("Import payload: {}".format(json.dumps(data_payload, indent=4)))

    url = "{0}/designfile/v1/sites/{1}/files/{2}/import_jobs".format(a_server_config.to_url(), a_site_id, a_file_upload_uuid)

    response = session.post(url, headers=a_headers, data=json.dumps(data_payload))
    response.raise_for_status()
    job_reponse_json = response.json()
    logging.debug ("Post import job returned {0}\n{1}".format(response.status_code, json.dumps(job_reponse_json,indent=4)))

    # ------------------------------------------------------------------------------
    logging.info ("Get result of import job via long poll:")
    # ------------------------------------------------------------------------------

    url = "{0}/designfile/v1/sites/{1}/import_jobs/{2}".format(a_server_config.to_url(), a_site_id, job_reponse_json["id"])

    response = session.get(url, headers=a_headers, params={"long_poll":True})
    response.raise_for_status()
    rj = response.json()
    logging.debug ("get import job returned {0}\n{1}".format(response.status_code, json.dumps(rj,indent=4)))

    # Add an RDM representation for each feature imported to MAXML
    file_uuid = rj["file_uuid"]
    import_uuid = rj["import_uuid"]
    import_list = rj["imports"]
    design_objects_to_import = []

    logging.debug ("{} design objects were imported by the job".format(len(import_list)))


    # ------------------------------------------------------------------------------
    logging.debug ("\nAdd an RDM representation for each imported design object so it can be found & managed:")
    # ------------------------------------------------------------------------------


    for i, design_object in enumerate(import_list):

        v = {k : design_object.get(k) for k in ["design_type", "source_name", "count", "design_file_uuid", "design_object_id", "path"] if k in design_object}
        design_objects_to_import.append(v)
        logging.debug (json.dumps(v, sort_keys=True, indent=4))

        at = int(round(time.time() * 1000))
        data_payload = { "_id" : v["design_object_id"], # recommended value for RDM as it's deterministic
            "_at"    : at,
            "_rev"   : str(uuid.uuid4()),
            "_type":"sl::designObject",
            "designType": v["design_type"],
            "name" : v["source_name"],
            "count" : v["count"],
            "doFileUUID" : v["design_file_uuid"],
            "importUUID": import_uuid,
            "importFileUUID": file_uuid,
            "path": v["path"]
        }

        logging.debug ("RDM payload: {}".format(json.dumps(data_payload, indent=4)))

        data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(data_payload).encode('utf-8')).decode('utf-8') }
        url = "{0}/rdm_log/v1/site/{1}/domain/sitelink/events".format(a_server_config.to_url(),a_site_id)

        response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
        response.raise_for_status()

        rj = response.json()
        logging.debug ("RDM post returned {0}\n{1}".format(response.status_code, json.dumps(rj,indent=4)))


def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Upload a file.")

    # script parameters:
    arg_parser.add_argument("--log-format", default='> %(asctime)-15s %(module)s %(levelname)s %(funcName)s:   %(message)s')
    arg_parser.add_argument("--log-level", default=logging.INFO)

    # server parameters:
    arg_parser.add_argument("--dc", default="us", required=True)
    arg_parser.add_argument("--env", default="", help="deploy environment (which determines server location)")
    arg_parser.add_argument("--jwt", default="", help="jwt")
    arg_parser.add_argument("--oauth_id", default="", help="oauth_id")
    arg_parser.add_argument("--oauth_secret", default="", help="oauth_secret")
    arg_parser.add_argument("--oauth_scope", default="", help="oauth_scope")

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)
    arg_parser.add_argument("--file_uuid", default="", help="UUID of file")
    arg_parser.add_argument("--file_name", default="", help="File name to interrogate")

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments


    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
   
    token = get_token(a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
  
    features_to_import = query_file_features(a_server_config=server, a_site_id=args.site_id, a_file_upload_uuid=args.file_uuid, a_file_name=args.file_name, a_headers=to_bearer_token_content_header(token["access_token"]))

    logging.info ("Found {} features in the file".format(len(features_to_import)))
    for feature in features_to_import:
        logging.debug (json.dumps(feature, sort_keys=True, indent=4))

    

if __name__ == "__main__":
    main()    

