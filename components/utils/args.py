#!/usr/bin/env python

import argparse
import uuid
import logging

def handle_arguments(a_description, a_arg_list=[], a_arg_filter_list=[]):
    arg_parser = argparse.ArgumentParser(description=a_description)
    # All scripts require these basic arguments
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_logging(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    # Some scripts require specific arguments
    [arg_parser.add_argument(i["arg"], default=i["default"], help=i["help"], required=i["required"]) for i in a_arg_list]
    
    # Generate any bespoke filtering arguments 
    add_arguments_filtering(arg_parser,a_arg_filter_list)

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    return args

def add_arguments_environment(a_arg_parser):
    a_arg_parser.add_argument("--env", default="", help="deploy env (which determines server location)")
    a_arg_parser.add_argument("--dc", default="qa")
    return a_arg_parser

def add_arguments_logging(a_arg_parser):
    a_arg_parser.add_argument("--log_format", default='> %(asctime)-15s %(module)s %(levelname)s %(funcName)s:   %(message)s')
    return a_arg_parser

def add_arguments_site(a_arg_parser):
    a_arg_parser.add_argument("--site_id", default="", help="Site Identifier")
    return a_arg_parser

def add_arguments_smartview(a_arg_parser, a_app):
    a_arg_parser.add_argument("--app"  , help="the SmartApp required", default=a_app)
    a_arg_parser.add_argument("--args" , help="""extra arguments passed to the SmartApp. String of the form "a=1&b=2&b=3".""")
    return a_arg_parser

def add_arguments_auth(a_arg_parser):
    a_arg_parser.add_argument("--jwt", default="", help="jwt")
    a_arg_parser.add_argument("--oauth_id", default="", help="oauth_id")
    a_arg_parser.add_argument("--oauth_secret", default="", help="oauth_secret")
    a_arg_parser.add_argument("--oauth_scope", default="", help="oauth_scope")
    return a_arg_parser

def add_arguments_pagination(a_arg_parser):
    a_arg_parser.add_argument("--page_limit", default="", help="the max size a result list can be prior to being split into pages.")
    a_arg_parser.add_argument("--start", help="the starting item offset for the return of results.")
    return a_arg_parser

def add_arguments_sorting(a_arg_parser):
    a_arg_parser.add_argument("--sort_field", default="", help="The optional column to sort the resulting list by.")
    a_arg_parser.add_argument("--sort_order", default="+", help="The direction to sort the results by.")
    return a_arg_parser

def add_arguments_filtering(a_arg_parser, a_filter_list):
    [a_arg_parser.add_argument("--filter_" + i) for i in a_filter_list]
    return a_arg_parser

# Result sorting related arguments
arg_sort_field = {
        "arg" : "--sort_field",
        "default" : "",
        "help" : "The optional column name to sort a query result list by.",
        "required" : False
    }

arg_sort_order = {
        "arg" : "--sort_order",
        "default" : "+",
        "help" : "The optional direction to sort a query result list by.",
        "required" : False
    }

# File and folder related arguments. Both files and folders are represented in the same way but different parameter names
# are provided so as to improve code comprehension.
arg_file_name = {
        "arg" : "--file_name",
        "default" : str(uuid.uuid4()),
        "help" : "The name of the file in the file system.",
        "required" : True
    }

arg_file_uuid = {
        "arg" : "--file_uuid",
        "default" : str(uuid.uuid4()),
        "help" : "The UUID of the file as a string.",
        "required" : True
    }

arg_file_id = {
        "arg" : "--file_id",
        "default" : "",
        "help" : "The RDM ID of the file as a string.",
        "required" : True
    }

arg_file_rev = {
        "arg" : "--file_rev",
        "default" : "",
        "help" : "The RDM revision of the file as a string.",
        "required" : True
    }    

arg_file_parent_uuid = {
        "arg" : "--file_parent_uuid",
        "default" : None,
        "help" : "The UUID of the file's parent (if avaialble) as a string. This represents a containing folder.",
        "required" : False
    }

arg_folder_name = {
        "arg" : "--folder_name",
        "default" : str(uuid.uuid4()),
        "help" : "The name of the folder in the file system.",
        "required" : True
    }

arg_folder_uuid = {
        "arg" : "--folder_uuid",
        "default" : str(uuid.uuid4()),
        "help" : "The UUID of the folder as a string.",
        "required" : True
    }

arg_folder_parent_uuid = {
        "arg" : "--folder_parent_uuid",
        "default" : None,
        "help" : "The UUID of the folder's parent (if avaialble) as a string. This represents a containing folder.",
        "required" : False
    }

# Site and organization related arguments
arg_site_name = {
        "arg" : "--site_name",
        "default" : "Site",
        "help" : "A name to refer to the site. This name is visible to operators for selection on client software and in the web portal map.",
        "required" : True
    }

arg_site_id = {
        "arg" : "--site_id",
        "default" : "",
        "help" : "64 character site identifier.",
        "required" : True
    }

arg_site_latitude = {
        "arg" : "--site_latitude",
        "default" : "",
        "help" : "The latitude of an arbitrary point to locate the site on a map.",
        "required" : True
    }

arg_site_longitude = {
        "arg" : "--site_longitude",
        "default" : "",
        "help" : "The longitude of an arbitrary point to locate the site on a map.",
        "required" : True
    }

arg_site_timezone = {
        "arg" : "--site_timezone",
        "default" : "",
        "help" : "The IANA timezone that the site is located in (eg. 'Australia/Brisbane') for the purpose of localizing dates and times in reports and other areas.",
        "required" : True
    }

arg_site_contact_name = {
        "arg" : "--site_contact_name",
        "default" : "",
        "help" : "The optional name of someone who can be contacted about this site. This name is visible to operators on client software usually to provide assistance with connecting software to a site.",
        "required" : False
    }

arg_site_contact_email = {
        "arg" : "--site_contact_email",
        "default" : "",
        "help" : "The optional email of someone who can be contacted about this site. This email is visible to operators on client software usually to provide assistance with connecting software to a site.",
        "required" : False
    }

arg_site_contact_phone = {
        "arg" : "--site_contact_phone",
        "default" : "",
        "help" : "The optional phone number of someone who can be contacted about this site as a string. This number is visible to operators on client software usually to provide assistance with connecting software to a site.",
        "required" : False
    }

arg_site_owner_uuid = {
        "arg" : "--site_owner_uuid",
        "default" : "",
        "help" : "The UUID representing an organization, the entity capable of owning sites.",
        "required" : False
    }

arg_site_auth_code = {
    "arg" : "--site_auth_code",
    "default" : "",
    "help" : "A numeric code used by clients to get access to the site. Must be between 6 and 18 digits.",
    "required" : True
}

# Output logging
arg_log_level = {
    "arg" : "--log_level",
    "default" : 20,
    "help" : "CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10.",
    "required" : False
}

# Pagination related arguments
arg_pagination_page_limit = {
        "arg" : "--page_limit",
        "default" : "",
        "help" : "The max size a result list can be prior to being split into pages.",
        "required" : False
}

arg_pagination_start = {
        "arg" : "--start",
        "default" : "",
        "help" : "The starting item offset for the return of results.",
        "required" : False
}

# Report related arguments
arg_report_name = {
        "arg" : "--report_name",
        "default" : "",
        "help" : "A name for a report.",
        "required" : True
}

# Report related arguments
arg_report_issued_by = {
        "arg" : "--report_issued_by",
        "default" : "",
        "help" : "A name for a the source of the report.",
        "required" : False
}

arg_report_url = {
        "arg" : "--report_url",
        "default" : "",
        "help" : "The unique location at which the report data can be downloaded from.",
        "required" : True
}

arg_report_term = {
        "arg" : "--report_term",
        "default" : "longterms",
        "help" : "The duration partition that the report is stored under. Persistent reports are of term 'longterms'.",
        "required" : False
}

arg_report_iso_date_time_start = {
        "arg" : "--report_iso_date_time_start",
        "default" : "",
        "help" : "Start date and time epoch that commences a period of time usually specified when creating a report. ISO format.",
        "required" : True
}

arg_report_iso_date_time_end = {
        "arg" : "--report_iso_date_time_end",
        "default" : "",
        "help" : "End date and time epoch that terminates a period of time usually specified when creating a report. ISO format.",
        "required" : True
}

arg_time_start_ms = {
        "arg" : "--time_start_ms",
        "default" : "",
        "help" : "The ms since epoch that data is to be queried from.",
        "required" : True
}

arg_time_end_ms = {
        "arg" : "--time_end_ms",
        "default" : "",
        "help" : "The ms since epoch that data is to be queried to.",
        "required" : True
}

arg_report_mask_region_uuid = {
    "arg" : "--report_mask_region_uuid",
    "default" : "",
    "help" : "The RDM UUID representing the region that can be used to optionally bound the physical area that Height Map (AsBuilt) reports are generated over.",
    "required" : False
}

arg_report_task_uuid = {
    "arg" : "--report_task_uuid",
    "default" : "",
    "help" : "The RDM UUID representing the task that can be used to optionally filter Height Map (AsBuilt) reports.",
    "required" : False
}

arg_report_sequence_instance = {
    "arg" : "--report_sequence_instance",
    "default" : "",
    "help" : "The sequence (sometimes called lift) that can be used to optionally filter Height Map (AsBuilt) reports. For level sequences: index formatted '%08d'; for shift sequences: 'YYYY-MM-DD`T`{startTime}' in site-local time.",
    "required" : False
}

# Datalogger related arguments
arg_datalogger_start_ms = {
    "arg" : "--datalogger_start_ms",
    "default" : "",
    "help" : "The ms since epoch that datalogger data is to be queried from.",
    "required" : True
}

arg_datalogger_end_ms = {
    "arg" : "--datalogger_end_ms",
    "default" : "",
    "help" : "The ms since epoch that datalogger data is to be queried to.",
    "required" : True
}

arg_datalogger_output_file_name = {
    "arg" : "--datalogger_output_file_name",
    "default" : "",
    "help" : "The file name that datalogger data is to be written to.",
    "required" : True
}

arg_datalogger_output_folder = {
    "arg" : "--datalogger_output_folder",
    "default" : ".",
    "help" : "The target location in the file system that the output file(s) will be written to.",
    "required" : True
}

# Transform related arguments
arg_transform_local_position_points_file = {
    "arg" : "--transform_local_position_points_file",
    "default" : "",
    "help" : "A file containing local points to be transformed.",
    "required" : True
}

# Output control
arg_output_verbosity = {
    "arg" : "--output_verbosity",
    "default" : "basic",
    "help" : "basic or advanced.",
    "required" : False
}

# Smartview related arguments
arg_smartview_args = {
    "arg" : "--smartview_args",
    "default" : "",
    "help" : """extra arguments passed to the SmartApp. String of the form "a=1&b=2&b=3".""",
    "required" : False
}

# RDM related arguments
arg_rdm_object_uuid = {
        "arg" : "--rdm_object_uuid",
        "default" : "",
        "help" : "The UUID of a particular object in RDM represented as a string.",
        "required" : True
}

arg_rdm_view_name = {
        "arg" : "--rdm_view",
        "default" : "",
        "help" : "The view to query RDM by",
        "required" : True
}

arg_rdm_domain_default_sitelink = {
        "arg" : "--rdm_domain",
        "default" : "sitelink",
        "help" : "The partition within RDM that contains data and associated views. Defaults to the main sitelink domain.",
        "required" : False
}

arg_rdm_domain_default_filesystem = {
        "arg" : "--rdm_domain",
        "default" : "file_system",
        "help" : "The partition within RDM that contains data and associated views. Defaults to the storage of file and folder objects.",
        "required" : False
}

arg_rdm_delay_name = {
        "arg" : "--rdm_delay_name",
        "default" : "Delay",
        "help" : "A name that represents the cause of disruptions at a site. This name is visible to operators for selection on client software and in reports.",
        "required" : True
}

arg_rdm_delay_code = {
        "arg" : "--rdm_delay_code",
        "default" : "",
        "help" : "An optional code to describe a delay.",
        "required" : False
}

arg_rdm_material_name = {
        "arg" : "--rdm_material_name",
        "default" : "Material",
        "help" : "A name that represents a physical substance that can be hauled, compacted or otherwise worked at a site. This name is visible to operators for selection on client software and in reports.",
        "required" : True
}

arg_rdm_road_truck_name = {
        "arg" : "--rdm_road_truck_name",
        "default" : "",
        "help" : "A name for a road truck interacting with load-weighing systems.",
        "required" : True
}

arg_rdm_road_truck_code = {
        "arg" : "--rdm_road_truck_code",
        "default" : "",
        "help" : "An optional code to describe a road truck interacting with load-weighing systems.",
        "required" : False
}

arg_rdm_road_truck_tare = {
        "arg" : "--rdm_road_truck_tare",
        "default" : "",
        "help" : "The unladen mass of a road truck interacting with load-weighing systems.",
        "required" : False
}

arg_rdm_road_truck_target = {
        "arg" : "--rdm_road_truck_target",
        "default" : "",
        "help" : "The legal weight limit of the truck.",
        "required" : True
}

arg_rdm_road_trailer_name = {
        "arg" : "--rdm_road_trailer_name",
        "default" : "",
        "help" : "A name for a road trailer interacting with load-weighing systems.",
        "required" : True
}

arg_rdm_road_trailer_code = {
        "arg" : "--rdm_road_trailer_code",
        "default" : "",
        "help" : "An optional code to describe a road trailer interacting with load-weighing systems.",
        "required" : False
}

arg_rdm_road_trailer_tare = {
        "arg" : "--rdm_road_trailer_tare",
        "default" : "",
        "help" : "The unladen mass of a road trailer interacting with load-weighing systems.",
        "required" : False
}

arg_rdm_road_trailer_target = {
        "arg" : "--rdm_road_trailer_target",
        "default" : "",
        "help" : "The legal weight limit of the trailer.",
        "required" : True
}

arg_rdm_road_truck_target_update = {
        "arg" : "--rdm_road_truck_target_update",
        "default" : "",
        "help" : "An update to an existing truck's legal weight limit.",
        "required" : True
}

arg_rdm_operator_code = {
        "arg" : "--rdm_operator_code",
        "default" : "",
        "help" : "An optional code to describe an operator.",
        "required" : False
}

arg_rdm_operator_first_name = {
        "arg" : "--rdm_operator_first_name",
        "default" : "",
        "help" : "An operators Christian name.",
        "required" : True
}

arg_rdm_operator_second_name = {
        "arg" : "--rdm_operator_second_name",
        "default" : "",
        "help" : "An operators surname.",
        "required" : True
}

arg_rdm_region_name = {
        "arg" : "--rdm_region_name",
        "default" : "Region",
        "help" : "A name that represents a geographical region at a site. This name is visible to operators for selection on client software and in reports.",
        "required" : True
}

arg_rdm_region_verticies_file = {
        "arg" : "--rdm_region_verticies_file",
        "default" : "",
        "help" : "A file containing points outlining a region.",
        "required" : True
}

arg_rdm_region_discovery_verticies_file = {
        "arg" : "--rdm_region_discovery_verticies_file",
        "default" : "",
        "help" : "A file containing points outlining a region used for site discovery.",
        "required" : True
}

arg_rdm_region_load_verticies_file = {
        "arg" : "--rdm_region_load_verticies_file",
        "default" : "",
        "help" : "A file containing points outlining a region used for auto loading haul trucks.",
        "required" : True
}

arg_rdm_region_dump_verticies_file = {
        "arg" : "--rdm_region_dump_verticies_file",
        "default" : "",
        "help" : "A file containing points outlining a region used for auto dumping haul trucks.",
        "required" : True
}

# State related artuments 
arg_operation = {
        "arg" : "--operation",
        "default" : "",
        "help" : "An optional string to direct the execution of an example. This could mean 'archive' or 'restore' for RDM or site related archival contexts for example.",
        "required" : False
}

# Data update related arguments
arg_data_update_method = {
        "arg" : "--data_update_method",
        "default" : "event",
        "help" : "A required field that specifies whether data updates (for example the status of reporting jobs) should be polled for or accessed using an event subscription and callback. Options are 'poll' or 'event'.",
        "required" : True
}

# Live data writing
arg_machine_resource_configuration_file = {
        "arg" : "--machine_resource_configuration_file",
        "default" : "",
        "help" : "The relative path to a json file defining the resource configuration for a machine.",
        "required" : True
}