#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "road_truck_create", "rdm_query_object", "rdm_pagination_traits"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_rdm_road_truck_name, arg_rdm_road_truck_code, arg_rdm_road_truck_tare, arg_rdm_road_truck_target, arg_rdm_road_truck_target_update])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=int(args.log_level))
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    
    truck_name = args.rdm_road_truck_name

    logging.info("Listing all road trucks currently known at site before creating truck {}.".format(truck_name))
    objects = query_rdm_object_properties_in_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink", a_view="v_sl_truck_by_name", a_headers=headers, a_page_traits=RdmViewPaginationTraits(a_page_size="100", a_start=""), a_callback=lambda a_item : True)
    [logging.info(json.dumps(obj, indent=4)) for obj in objects] 
    
    logging.info("Creating truck with name:{}, tare:{}, target weight:{} and code:{}.".format(truck_name, args.rdm_road_truck_tare, args.rdm_road_truck_target, args.rdm_road_truck_code))
    creation_success, truck_id = create_road_truck(a_site_id=args.site_id, a_server_config=server, a_name=truck_name, a_tare=args.rdm_road_truck_tare, a_target=args.rdm_road_truck_target, a_code=args.rdm_road_truck_code, a_headers=headers)

    if not creation_success:
        logging.info("Couldn't create truck")
        return

    logging.info("Listing road trucks at site by name {}. This may produce duplicates as names are not required to be unique.".format(truck_name))
    objects = query_rdm_object_properties_in_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink", a_view="v_sl_truck_by_name", a_headers=headers, a_page_traits=RdmViewPaginationTraits(a_page_size="100",  a_start=""), a_callback=lambda a_item : a_item["value"]["name"] == truck_name)
    [logging.info(json.dumps(obj, indent=4)) for obj in objects] 

    logging.info("Listing road trucks at site by unique identifier {}. This will not produce duplicates.".format(truck_name))
    objects = query_rdm_object_properties_in_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink", a_view="v_sl_truck_by_name", a_headers=headers, a_page_traits=RdmViewPaginationTraits(a_page_size="100",  a_start=[truck_name], a_end=[truck_name, None]), a_callback=lambda a_item : a_item["id"] == truck_id)
    [logging.info(json.dumps(obj, indent=4)) for obj in objects] 

    # Update the target weight of the newly created truck. This is done by posting the object to RDM with the same _id but a new _rev (revision) identifier
    logging.info("Updating newly created truck to set new target weight:{}.".format(args.rdm_road_truck_target_update))
    update_success = update_road_truck(a_site_id=args.site_id, a_server_config=server, a_id=truck_id, a_name=truck_name, a_tare=args.rdm_road_truck_tare, a_target=args.rdm_road_truck_target_update, a_code=args.rdm_road_truck_code, a_headers=headers)

    if not update_success:
        logging.info("Couldn't update truck")
        return 

    logging.info("Listing road trucks at site by unique identifier to confirm the truck {} was updated with a new revision. This will not produce duplicates.".format(truck_name))
    objects = query_rdm_object_properties_in_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink", a_view="v_sl_truck_by_name", a_headers=headers, a_page_traits=RdmViewPaginationTraits(a_page_size="100",  a_start=[truck_name], a_end=[truck_name, None]), a_callback=lambda a_item : a_item["id"] == truck_id)
    [logging.info(json.dumps(obj, indent=4)) for obj in objects] 

if __name__ == "__main__":
    main()    
