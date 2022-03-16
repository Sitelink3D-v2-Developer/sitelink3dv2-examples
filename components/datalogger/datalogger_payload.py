#!/usr/bin/python
import json
import logging
import urllib.parse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "mfk"))

from mfk import *

class DataloggerPayload(object):

    def payload_factory(a_object_value, a_asset_name_lookup_func, a_replicate_data_lookup_func):

        try:
            if a_object_value["type"] == "mfk::Replicate":
                rc_uuid = a_object_value['data']['rc_uuid']
                return DataloggerPayloadReplicate(a_object_value, rc_uuid, a_asset_name_lookup_func, a_replicate_data_lookup_func)
            
            elif a_object_value["type"] == "sitelink::State":
                return DataloggerPayloadState(a_object_value, a_asset_name_lookup_func)

            elif a_object_value["type"] == "sitelink::Event":
                if a_object_value["data"]["type"] == "load":
                    return DataloggerPayloadLoadEvent(a_object_value, a_asset_name_lookup_func)
                elif a_object_value["data"]["type"] == "obw_clear":
                    return DataloggerPayloadOnBoardWeighingClear(a_object_value, a_asset_name_lookup_func)
                elif a_object_value["data"]["type"] == "obw_open":
                    return DataloggerPayloadOnBoardWeighingOpen(a_object_value, a_asset_name_lookup_func)
                elif a_object_value["data"]["type"] == "obw_load":
                    return DataloggerPayloadOnBoardWeighingLoad(a_object_value, a_asset_name_lookup_func)
                elif a_object_value["data"]["type"] == "obw_lift":
                    return DataloggerPayloadOnBoardWeighingLift(a_object_value, a_asset_name_lookup_func)
                elif a_object_value["data"]["type"] == "close":
                    return DataloggerPayloadCloseEvent(a_object_value, a_asset_name_lookup_func)               
            
        except TypeError as err:
            logging.debug("TypeError {}".format(err))
        except KeyError as err:
            logging.debug("KeyError {}".format(err))

    traits_factory = staticmethod(payload_factory)

class DataloggerPayloadBase():
    def __init__(self, a_json):
        self.m_json = a_json
        
    def payload_type(self):
        return self.m_json["type"]
        
    def data_type(self):
        return self.m_json["data"]["type"]

# DataloggerPayloadReplicate processes payloads of the form
#
# {
#     "at": 1646961457485,
#     "type": "mfk::Replicate",
#     "ttl": 55,
#     "data": {
#         "ac_uuid": "082d1c79-1725-41a1-9d35-5f4f652b2f1b",
#         "rc_uuid": "d990a890-4510-11e7-a919-92ebcb67fe33",
#         "beacon": true,
#         "local_bounds": {
#             "type": "none"
#         },
#         "manifest": [
#             "EhlM6UetO8DfkZONMyZjQAAAAAAAAAhAAAAAAA=="
#         ]
#     }
# }
class DataloggerPayloadReplicate(DataloggerPayloadBase):
    def __init__(self, a_json, a_rc_uuid, a_asset_name_lookup_func, a_replicate_data_lookup_func):
        DataloggerPayloadBase.__init__(self, a_json)
        self.m_rc_uuid = a_rc_uuid
        self.m_asset_name_lookup_func = a_asset_name_lookup_func
        self.m_replicate_data_lookup_func = a_replicate_data_lookup_func

    def data_type(self):
        return "manifest"

    def manifest(self):
        return self.m_json["data"]["manifest"]

    def format(self):
        machine_name = self.m_asset_name_lookup_func(self.m_json["data"]["ac_uuid"])
        vals = self.m_replicate_data_lookup_func(self.m_rc_uuid)
        return "{}, machine '{}' sent replicate '{}'".format(self.m_json["at"], machine_name, vals)

# DataloggerPayloadState processes payloads of the form
#
# {
#     "at": 1646961609316,
#     "type": "sitelink::State",
#     "ttl": 120,
#     "data": {
#         "ac_uuid": "7e7f50a4-340a-41f8-a2d1-a7c5a8ce4f2a",
#         "ns": "topcon.task",
#         "state": "name",
#         "value": "Excavate & Haul Sand"
#     }
# }
class DataloggerPayloadState(DataloggerPayloadBase):
    def __init__(self, a_json, a_asset_name_lookup_func):
        DataloggerPayloadBase.__init__(self, a_json)
        self.m_asset_name_lookup_func = a_asset_name_lookup_func

    def data_type(self):
        return self.m_json["data"]["ns"]

    def format(self):
        machine_name = self.m_asset_name_lookup_func(self.m_json["data"]["ac_uuid"])
        ret = ""
        if len(self.m_json["data"]["value"]) > 0:
            ret = "{}, machine '{}' updated state {} {} to '{}'"\
                .format(self.m_json["at"], machine_name, self.m_json["data"]["ns"], self.m_json["data"]["state"], self.m_json["data"]["value"])
        else:
            ret = "{}, machine '{}' cleared state {} {}"\
                .format(self.m_json["at"], machine_name, self.m_json["data"]["ns"], self.m_json["data"]["state"])
        return ret

# DataloggerPayloadLoadEvent processes payloads of the form
#
# {
#     "at": 1646961993886,
#     "type": "sitelink::Event",
#     "ttl": 0,
#     "data": {
#         "material_axis": "weight",
#         "material_uuid": "bd13a747-3c5c-4f71-abc5-ec1f6d268022",
#         "loader_id": "urn:X-topcon:machine:ac:excavator:oem::model::sn::id:X-53x",
#         "loader_ref": "d1c51421-b2a1-4169-bf18-fa09ea6556d9",
#         "bin_urn": "urn:X-topcon:machine:ac:truck:oem::model::sn::id:HTR001",
#         "material_state": "Default",
#         "bin": "truck",
#         "region_uuid": "f8d3fd4c-046b-49b4-9bec-9633b84039ab",
#         "uuid": "e43dbe71-c59f-4ab9-b338-039f20303cf8",
#         "material_unit": "metric_tons",
#         "quantity": 2,
#         "ac_uuid": "c5fbbba2-613d-473f-99c4-be8fba712b0c",
#         "ns": "topcon.haul",
#         "type": "load"
#     }
# }  
class DataloggerPayloadLoadEvent(DataloggerPayloadBase):
    def __init__(self, a_json, a_asset_name_lookup_func):
        DataloggerPayloadBase.__init__(self, a_json)
        self.m_asset_name_lookup_func = a_asset_name_lookup_func

    def format(self):
        region_uuid = ""
        try:
            region_uuid = self.m_json["data"]["region_uuid"]
        except KeyError:
            logging.debug("No region detected in Load Event payload.")

        loader_name = ""
        try:
            loader_id = self.m_json["data"]["loader_id"]
            if loader_id is not None:
                loader_name = loader_id.split(":")[-1]
        except KeyError:
            logging.debug("No load assignment detected in Load Event payload.")

        machine_name = self.m_asset_name_lookup_func(self.m_json["data"]["ac_uuid"])
        log = "{}, machine '{}' confirmed load of {} {} of material '{}' in state '{}' into bin '{}'"\
            .format(self.m_json["at"],urllib.parse.unquote(machine_name),self.m_json["data"]["quantity"],self.m_json["data"]["material_unit"], self.m_json["data"]["material_uuid"], self.m_json["data"]["material_state"], self.m_json["data"]["bin"])

        if(len(region_uuid) > 0):
            log += " in region '{}'".format(region_uuid)
        if(len(loader_name) > 0):
            log += " (loaded by machine {})".format(urllib.parse.unquote(loader_name))
        return log

# DataloggerPayloadCloseEvent processes payloads of the form
#
# {
#     "at": 1646962558698,
#     "type": "sitelink::Event",
#     "ttl": 0,
#     "data": {
#         "uuid": "e43dbe71-c59f-4ab9-b338-039f20303cf8",
#         "ac_uuid": "c5fbbba2-613d-473f-99c4-be8fba712b0c",
#         "ns": "topcon.haul",
#         "type": "close"
#     }
# }
class DataloggerPayloadCloseEvent(DataloggerPayloadBase):
    def __init__(self, a_json, a_asset_name_lookup_func):
        DataloggerPayloadBase.__init__(self, a_json)
        self.m_asset_name_lookup_func = a_asset_name_lookup_func

    def format(self):
        machine_name = self.m_asset_name_lookup_func(self.m_json["data"]["ac_uuid"])
        return "{}, machine '{}' closed haul {}"\
            .format(self.m_json["at"], machine_name, self.m_json["data"]["uuid"])

# DataloggerPayloadOnBoardWeighingClear processes payloads of the form
#
# {
#     "at": 1646961987311,
#     "type": "sitelink::Event",
#     "ttl": 0,
#     "data": {
#         "hauls": {
#             "urn:X-topcon:asset:ac:trailer:oem::model::sn::id:box%20trailer": {
#                 "weight": 1
#             },
#             "urn:X-topcon:machine:ac:truck:oem::model::sn::id:HTR001": {
#                 "weight": 2
#             }
#         },
#         "job_num": 1,
#         "legal_trade": false,
#         "ticket_num": 0,
#         "job_uuid": "d1c51421-b2a1-4169-bf18-fa09ea6556d9",
#         "ac_uuid": "18b3c63b-8944-4abb-90ab-dda182464f5c",
#         "ns": "topcon.obw",
#         "type": "obw_clear"
#     }
# }
class DataloggerPayloadOnBoardWeighingClear(DataloggerPayloadBase):
    def __init__(self, a_json, a_asset_name_lookup_func):
        DataloggerPayloadBase.__init__(self, a_json)
        self.m_asset_name_lookup_func = a_asset_name_lookup_func

    def format(self):
        machine_name = self.m_asset_name_lookup_func(self.m_json["data"]["ac_uuid"])
        target_bins = {}
        keys = self.m_json["data"]["hauls"].keys()
        for i, val in enumerate(keys):
            target_bin_name = urllib.parse.unquote(val.split(":")[-1])
            target_bins[target_bin_name] = self.m_json["data"]["hauls"][val]["weight"]
        
        target_string = ""
        for target in target_bins.keys():
            if len(target_string) != 0:
                target_string += ","
            target_string += "{} [units] to '{}'".format(target_bins[target],target)
        return "{}, machine '{}' cleared weighing job '{}' consisting of {}"\
            .format(self.m_json["at"], machine_name, self.m_json["data"]["job_num"], target_string)
   
# DataloggerPayloadOnBoardWeighingLoad processes payloads of the form
#
# {
#     "at": 1646961987307,
#     "type": "sitelink::Event",
#     "ttl": 0,
#     "data": {
#         "region_uuid": "f8d3fd4c-046b-49b4-9bec-9633b84039ab",
#         "job_uuid": "d1c51421-b2a1-4169-bf18-fa09ea6556d9",
#         "ac_uuid": "18b3c63b-8944-4abb-90ab-dda182464f5c",
#         "ns": "topcon.obw",
#         "type": "obw_load"
#     }
# }
class DataloggerPayloadOnBoardWeighingLoad(DataloggerPayloadBase):
    def __init__(self, a_json, a_asset_name_lookup_func):
        DataloggerPayloadBase.__init__(self, a_json)
        self.m_asset_name_lookup_func = a_asset_name_lookup_func

    def format(self):
        machine_name = self.m_asset_name_lookup_func(self.m_json["data"]["ac_uuid"])
        return "{}, machine '{}' loaded weighing job {}"\
            .format(self.m_json["at"], machine_name, self.m_json["data"]["job_uuid"])

# DataloggerPayloadOnBoardWeighingLift processes payloads of the form
#
# {
#     "at": 1646961987308,
#     "type": "sitelink::Event",
#     "ttl": 0,
#     "data": {
#         "material_axis": "weight",
#         "material_state": "Default",
#         "material_unit": "metric_tons",
#         "material_uuid": "bd13a747-3c5c-4f71-abc5-ec1f6d268022",
#         "preset_tare": 0,
#         "start": true,
#         "weight": 2,
#         "job_uuid": "d1c51421-b2a1-4169-bf18-fa09ea6556d9",
#         "ac_uuid": "18b3c63b-8944-4abb-90ab-dda182464f5c",
#         "ns": "topcon.obw",
#         "type": "obw_lift"
#     }
# }
class DataloggerPayloadOnBoardWeighingLift(DataloggerPayloadBase):
    def __init__(self, a_json, a_asset_name_lookup_func):
        DataloggerPayloadBase.__init__(self, a_json)
        self.m_asset_name_lookup_func = a_asset_name_lookup_func

    def format(self):
        machine_name = self.m_asset_name_lookup_func(self.m_json["data"]["ac_uuid"])
        return "{}, machine '{}' lifted {} [units] for job {}"\
            .format(self.m_json["at"], machine_name, self.m_json["data"]["weight"], self.m_json["data"]["job_uuid"])

# DataloggerPayloadOnBoardWeighingOpen processes payloads of the form
#
# {
#     "at": 1646961456402,
#     "type": "sitelink::Event",
#     "ttl": 0,
#     "data": {
#         "job_uuid": "76b6d301-d8dd-45a1-b9a7-d785d8dc7aca",
#         "ac_uuid": "082d1c79-1725-41a1-9d35-5f4f652b2f1b",
#         "ns": "topcon.obw",
#         "type": "obw_open"
#     }
# }
class DataloggerPayloadOnBoardWeighingOpen(DataloggerPayloadBase):
    def __init__(self, a_json, a_asset_name_lookup_func):
        DataloggerPayloadBase.__init__(self, a_json)
        self.m_asset_name_lookup_func = a_asset_name_lookup_func

    def format(self):
        machine_name = self.m_asset_name_lookup_func(self.m_json["data"]["ac_uuid"])
        return "{}, machine '{}' opened weighing job {}"\
            .format(self.m_json["at"], machine_name, self.m_json["data"]["job_uuid"])
