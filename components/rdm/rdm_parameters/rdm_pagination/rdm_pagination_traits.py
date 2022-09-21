#!/usr/bin/python
import logging
import base64
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "utils", "parameters"))
from pagination import *

class RdmPaginationTraitsBase(PaginationTraitsBase):

    def __init__(self, a_page_size, a_page_start, a_start_key_field, a_next_key_field, a_data_page_key_field, a_next_key_field_offset):
        PaginationTraitsBase.__init__(self, a_page_size=a_page_size, a_page_start=a_page_start, a_fetch_size_key_field="limit", a_start_key_field=a_start_key_field, a_next_key_field=a_next_key_field, a_data_page_key_field=a_data_page_key_field)
        self.m_next_key_field_offset = a_next_key_field_offset

    def more_data(self, a_json):
        more = a_json is not None and a_json[self.m_next_key_field] is not None
        
        if(type(a_json[self.m_next_key_field]) == str):
            more = more and (len(a_json[self.m_next_key_field]) > 0)
            
        self.m_page_number += 1
        if more:
            self.m_page_start_value = a_json[self.m_next_key_field][self.m_next_key_field_offset] if len(self.m_next_key_field_offset) > 0 else a_json[self.m_next_key_field]
            logging.debug("{} found: {}".format(self.m_start_key_field, self.m_page_start_value))
        return more

class RdmViewPaginationTraits(RdmPaginationTraitsBase):

    def __init__(self, a_page_size, a_start, a_end=""):
        RdmPaginationTraitsBase.__init__(self, a_page_size=a_page_size, a_page_start=a_start, a_start_key_field="start", a_next_key_field="last_excl", a_data_page_key_field="items", a_next_key_field_offset="key")
        self.m_end_value = a_end

    def params(self, a_params={}):
        PaginationTraitsBase.params_page(self, a_params)
        if len(self.m_page_start_value) > 0:
            logging.debug("start key sepcified: {}".format(self.m_page_start_value))
            a_params[self.m_start_key_field] = base64.urlsafe_b64encode(json.dumps(self.m_page_start_value).encode('utf-8')).decode('utf-8').rstrip("=")            
        if len(self.m_end_value) > 0:
            logging.debug("end key sepcified: {}".format(self.m_end_value))
            a_params["end"] = base64.urlsafe_b64encode(json.dumps(self.m_end_value).encode('utf-8')).decode('utf-8').rstrip("=")
        return a_params

class RdmLogProjectionPaginationTraits(RdmPaginationTraitsBase):

    def __init__(self, a_page_size, a_start, a_end=""):
        RdmPaginationTraitsBase.__init__(self, a_page_size=a_page_size, a_page_start=a_start, a_start_key_field="from_cursor_excl", a_next_key_field="cursor_incl", a_data_page_key_field="events", a_next_key_field_offset="")
        self.m_end_value = a_end

    def params(self, a_params={}):
        PaginationTraitsBase.params_page(self, a_params)
        # A start key is required for RDM log projection
        logging.debug("start key sepcified: {}".format(self.m_page_start_value))
        a_params[self.m_start_key_field] = self.m_page_start_value       
        if len(self.m_end_value) > 0:
            logging.debug("end key sepcified: {}".format(self.m_end_value))
            a_params["end"] = base64.urlsafe_b64encode(json.dumps(self.m_end_value).encode('utf-8')).decode('utf-8').rstrip("=")
        return a_params
