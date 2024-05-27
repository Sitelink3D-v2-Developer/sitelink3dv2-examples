#!/usr/bin/env python

import sys
import os
from datetime import datetime

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "file_upload", "rdm_traits", "events"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_file_name])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
logging.basicConfig(format=args.log_format, level=int(args.log_level))
logging.info("Running {0} for server={1} dc={2}".format(script_name, server.to_url(), args.dc))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

file_upload_uuid = str(uuid.uuid4())

file_upload_bean = FileUploadBean(a_upload_uuid=file_upload_uuid, a_file_location=".", a_file_name=os.path.basename(args.file_name))

file_uuid = str(uuid.uuid4())

logging.debug("file_upload_uuid={}, file_uuid={}".format(file_upload_uuid, file_uuid))

file_rdm_bean = FileRdmTraits.post_bean_json(a_file_name=args.file_name, a_id=file_uuid, a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_domain="file_system", a_parent_uuid=None)

upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_headers=headers)

# post the map tile import job
frame = {
    "job_type": "import",
    "file_uuid": file_upload_uuid
}

logging.debug(json.dumps(frame,indent=4))
url = "{}/maptile/v1/sites/{}/jobs".format(server.to_url(), args.site_id)
j = json_from(requests.post(url, data=json.dumps(frame), headers=headers))

logging.debug(json.dumps(j,indent=4))
job_id = j["id"]

site_event_manager = HttpEventManager(a_server_config=server, a_identifier=args.site_id, a_source=EventSource.Site, a_headers=headers)

# post to RDM to define an object for the import
url = "{}/rdm_log/v1/site/{}/domain/sitelink/events".format(server.to_url(), args.site_id)

mod = os.path.getmtime(args.file_name) * 1000
now = int(round(time.time() * 1000))
mod_ms = now - int(mod)
frame = {
  "_type": "sl::mapTileset",
  "name": os.path.basename(args.file_name),
  "date": int(mod),
  "importFileId": file_upload_uuid,
  "tilesetId": job_id,
  "_id": str(uuid.uuid4()),
  "_rev": str(uuid.uuid4()), # The unique instance of this chunk of data in RDM. It is never correct to duplicate this.
  "_at": int(round(time.time() * 1000))
}

logging.debug(json.dumps(frame, indent=4))

data_encoded_json = {"data_b64": base64.b64encode(json.dumps(frame).encode('utf-8')).decode('utf-8')}
response = session.post(url, headers=headers, data=json.dumps(data_encoded_json))
logging.debug(response.json())
