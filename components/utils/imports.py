#!/usr/bin/python
import os
import sys

import_targets = { 
    "get_token": ["tokens"],
    "utils":        ["utils"],
    "rdm_pagination" : ["metadata", "rdm_parameters", "rdm_pagination"],
    "pagination" : ["utils", "parameters", "pagination"],
    "rdm_pagination_traits" : ["metadata", "rdm_parameters", "rdm_pagination"],
    "folder_create" : ["files", "folder_create"],
    "file_upload" : ["files", "file_upload"],
    "file_features" : ["files", "file_features"],
    "file_list" : ["files", "file_list"],
    "file_download" : ["files", "file_download"],
    "metadata_traits" : ["metadata"],
    "metadata_list" : ["metadata", "metadata_list"],
    "delay_create" : ["metadata", "metadata_create", "delay_create"],
    "material_create" : ["metadata", "metadata_create", "material_create"],
    "region_create" : ["metadata", "metadata_create", "region_create"],
    "task_create" : ["metadata", "metadata_create", "task_create"],
    "auth_code_create" : ["metadata", "metadata_create", "auth_code_create"],
    "args" : ["utils"],
    "sorting" : ["utils", "parameters"],
    "filtering" : ["utils", "parameters"],
    "site_pagination_traits" : ["sites"],
    "site_create" : ["sites", "site_create"],
    "report_download" : ["reports", "report_download"],
    "report_pagination_traits" : ["reports"],
    "report_traits" : ["reports"],
    "report_convert" : ["reports"],
    "report_create" : ["reports", "report_create"],
    "mfk" :["mfk"],
    "datalogger_payload" : ["datalogger"],
    "datalogger_utils" : ["datalogger"],
    "events" : ["utils"],
    "smartview" : ["smartview"]
}

def import_cmd(a_component_root, a_target):
    sys.path.append(os.path.join(a_component_root, *import_targets[a_target]))
    return "from {} import *".format(a_target)
