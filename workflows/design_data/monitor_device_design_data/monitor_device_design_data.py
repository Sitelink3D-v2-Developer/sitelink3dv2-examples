#!/usr/bin/python

# This example demonstrates the ability to download design data surveyed on machine control clients via the Design File service in response to
# event data. Unlike the "download_device_design_data_as_landxml" example which simply downloads all existing device design data at the specified
# site, this example will download only device design data that is sent to sitelink3D v2 once it has started running. That is to say that this 
# example subscribes to Sitelink3D's event service and responds to RDM service updates by polling the "v_sl_deviceDesignObject_by_deviceURN" view
# to look for changes of interest.

import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "site_detail", "get_token", "file_download", "file_list", "file_features", "rdm_list", "events"]:
    exec(import_cmd(components_dir, imp))
 
session = requests.Session()

def particular_from_design_type(a_design_type):
    if(a_design_type == "Lines"):
        return "LN3"
    elif(a_design_type == "Planes"):
        return "PL3"
    elif(a_design_type == "Points"):
        return "PT3"
    elif(a_design_type == "Roads"):
        return "RD3"
    elif(a_design_type == "Surfaces"):
        return "TN3"
    else:
        return "Invalid"

def main():

    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_pagination_page_limit, arg_pagination_start])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id,
                                        a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)


    # First we cache the existing device design data by querying RDM. This enables us to determine what may have changed when we 
    # later handle update events. We don't download existing device design data, just record the identifying details to seed the example.
    page_traits = RdmViewPaginationTraits(a_page_size=args.page_limit, a_start=args.start)
    device_design_object_list = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink",
                                                              a_view="v_sl_deviceDesignObject_by_deviceURN", a_headers=headers, a_params=page_traits.params())["items"]

    logging.info("Found {} initial device design objects".format(len(device_design_object_list)))
    for fi in device_design_object_list:
        logging.debug(json.dumps(fi, sort_keys=True, indent=4))

    device_design_object_dict = {

    }

    for fi in device_design_object_list:
        device_design_object = {
            "rev" : fi["value"]["_rev"],
            "at" : fi["value"]["_at"],
        }
        device_design_object_dict[fi["value"]["_id"]] = device_design_object

    site_event_manager = HttpEventManager(a_server_config=server, a_identifier=args.site_id, a_headers=headers, a_source=EventSource.Site)
    
    output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_target_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)

    while True:

        event = site_event_manager.wait_for_site_scope_rdm_update(a_timeout_seconds=5)
        if event:
            logging.info("Received RDM event.")
            logging.debug(json.dumps(event, indent=4))

            # We again query the v_sl_deviceDesignObject_by_deviceURN and compare to the cached items in device_design_object_dict to 
            # determine whether there's anything new to download. This is because RDM could have been updated for any reason so we 
            # check to see that the event is relevant to us.
            page_traits = RdmViewPaginationTraits(a_page_size=args.page_limit, a_start=args.start)
            device_design_object_list = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink",
                                                                    a_view="v_sl_deviceDesignObject_by_deviceURN", a_headers=headers, a_params=page_traits.params())["items"]

            for fi in device_design_object_list:
                update_this_design_object = False
                try:
                    cached_design_object = device_design_object_dict[fi["value"]["_id"]]
                    if cached_design_object["rev"] != fi["value"]["_rev"]:
                        # we've found a new version. Only apply if it's newer than what we have cached
                        if cached_design_object["at"] != fi["value"]["_at"]:
                            device_design_object = {
                                "rev" : fi["value"]["_rev"],
                                "at" : fi["value"]["_at"],
                            }
                            device_design_object_dict[fi["value"]["_id"]] = device_design_object
                            logging.info("New version of object '{}' available.".format(fi["value"]["name"]))
                            update_this_design_object = True

                except KeyError:
                    # This is a brand new device design object. We add it to the cache and download it as landxml.
                    device_design_object = {
                        "rev" : fi["value"]["_rev"],
                        "at" : fi["value"]["_at"],
                    }
                    logging.info("New object '{}' available.".format(fi["value"]["name"]))
                    device_design_object_dict[fi["value"]["_id"]] = device_design_object
                    update_this_design_object = True
                    
                if update_this_design_object:
                    logging.info("Downloading LANDXML.")
                    # Either as a result of an update to an existing device design object or the creation of a new one, we download now
                    current_dir = os.path.dirname(os.path.realpath(__file__))
                    device_output_dir = os.path.join(output_dir, fi["value"]["deviceURN"].replace(':', "-"))
                    original_dir = os.path.join(device_output_dir, "original")
                    converted_dir = os.path.join(device_output_dir, "converted")
                    rdm_file_name = fi["value"]["name"]

                    os.makedirs(original_dir, exist_ok=True)
                    os.makedirs(converted_dir, exist_ok=True)

                    particular = particular_from_design_type(fi["value"]["designType"])
                    base = "{}/designfile/v1/sites/{}/design_files/{}?design_type={}&particular=".format(
                        server.to_url(), args.site_id, fi["value"]["doFileUUID"], fi["value"]["designType"])
                    url_original = ["{}{}".format(base, particular), particular.lower(), original_dir]
                    url_landxml = ["{}LANDXML".format(base), "xml", converted_dir]
                    for url, ext, target in [url_original, url_landxml]:
                        response = session.get(url, headers=headers, stream=True)
                        response.raise_for_status()

                        output_file = os.path.join(target, "{}.{}".format(
                            os.path.splitext(rdm_file_name)[0], ext))
                        with open(output_file, "wb") as handle:
                            for data in tqdm(response.iter_content()):
                                handle.write(data)

if __name__ == "__main__":
    main()
