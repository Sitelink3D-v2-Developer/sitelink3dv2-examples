#!/usr/bin/python
import logging

class ReportPaginationTraits():

    def __init__(self, a_page_size, a_start):
        self.m_page_size = a_page_size
        self.m_start_value = a_start
        self.m_page_number = 0

    def more_data(self, a_json):
        more = a_json is not None and a_json["next_index"] is not None
        self.m_page_number += 1
        if more:
            self.m_start_value = a_json["next_index"]
            logging.debug("start key found: {}".format(self.m_start_value))
        return more

    def params(self):
        params = {}
        if len(self.m_page_size) > 0:
            params["limit"] = self.m_page_size
        if len(str(self.m_start_value)) > 0:
            logging.debug("start key sepcified: {}".format(self.m_start_value))
            params["offset"] = self.m_start_value
        return params

    def page_number(self):
        return self.m_page_number
