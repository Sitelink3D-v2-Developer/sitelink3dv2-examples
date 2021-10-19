#!/usr/bin/python
import logging
import base64
import json

class MetadataPaginationTraits():
    def __init__(self, a_page_size, a_start, a_end=""):
        self.m_page_size = a_page_size
        self.m_start_value = a_start
        self.m_end_value = a_end
        self.m_page_number = 0

    def more_data(self, a_json):
        more = a_json["last_excl"] is not None
        self.m_page_number += 1
        if more:
            self.m_start_value = a_json["last_excl"]["key"]
            logging.debug("start key found: {}".format(self.m_start_value))
        return more

    def params(self):
        params = {}
        if len(self.m_page_size) > 0:
            params["limit"] = self.m_page_size
        if len(self.m_start_value) > 0:
            logging.debug("start key sepcified: {}".format(self.m_start_value))
            params["start"] = base64.urlsafe_b64encode(json.dumps(self.m_start_value).encode('utf-8')).decode('utf-8').rstrip("=")            
        if len(self.m_end_value) > 0:
            logging.debug("end key sepcified: {}".format(self.m_end_value))
            params["end"] = base64.urlsafe_b64encode(json.dumps(self.m_end_value).encode('utf-8')).decode('utf-8').rstrip("=")
        return params

    def page_number(self):
        return self.m_page_number
