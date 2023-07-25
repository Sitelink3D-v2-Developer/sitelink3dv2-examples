#!/usr/bin/python
import sys
import os
import requests

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "utils", "parameters"))
from pagination import *

session = requests.Session()

class DataloggerPageQuery():
    def __init__(self, a_server_config, a_params, a_headers):
        self.m_server_config = a_server_config
        self.m_params = a_params
        self.m_headers = a_headers

    def query(self, a_params):
        params = self.m_params | a_params
        logging.debug("Using parameters:{}".format(json.dumps(params)))

        dba_url = "{}/dba/v1/machines".format(self.m_server_config.to_url())

        logging.info("get machine list from {}".format(dba_url))
        response = session.get(dba_url, headers=self.m_headers, params=params)
        response.raise_for_status()
        return response.json()

    
    @staticmethod
    def result(a_value):
        try:
            logging.info("'{}' at lat:{}, lon:{} in timezone {} ({})".format(a_value["rdm_name"], a_value["rdm_marker"]["lat"], a_value["rdm_marker"]["lon"], a_value["rdm_timezone"], "archived" if a_value["archived"] else "active")) 
        except KeyError as err:  
            pass 

class DataloggerPaginationTraits(PaginationTraitsBase):

    def __init__(self, a_page_size, a_start):
        PaginationTraitsBase.__init__(self, a_page_size=a_page_size, a_page_start=a_start, a_fetch_size_key_field="limit", a_start_key_field="continuation_token", a_next_key_field="next_continuation_token", a_data_page_key_field="items")
        
