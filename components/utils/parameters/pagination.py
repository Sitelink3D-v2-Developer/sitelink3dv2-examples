#!/usr/bin/python
import logging
import json

class PaginationTraitsBase():

    def __init__(self, a_page_size, a_page_start, a_fetch_size_key_field, a_start_key_field, a_next_key_field):
        self.m_page_size = a_page_size
        self.m_page_start_value = a_page_start
        self.m_page_number = 0
        self.m_fetch_size_key_field = a_fetch_size_key_field
        self.m_start_key_field = a_start_key_field
        self.m_next_key_field = a_next_key_field

    def more_data(self, a_json):
        more = a_json is not None and a_json[self.m_next_key_field] is not None
        
        if(type(a_json[self.m_next_key_field]) == str):
            more = more and (len(a_json[self.m_next_key_field]) > 0)
            
        self.m_page_number += 1
        if more:
            self.m_page_start_value = a_json[self.m_next_key_field]
            logging.debug("{} found: {}".format(self.m_start_key_field, self.m_page_start_value))
        return more

    def params_page(self, a_params={}):
        if len(self.m_page_size) > 0:
            a_params[self.m_fetch_size_key_field] = self.m_page_size
        return a_params

    def params_start(self, a_params={}):
        if len(str(self.m_page_start_value)) > 0:
            logging.debug("{} sepcified: {}".format(self.m_start_key_field, self.m_page_start_value))
            a_params[self.m_start_key_field] = self.m_page_start_value
        return a_params

    def params(self, a_params={}):
        a_params = self.params_page(a_params)
        a_params = self.params_start(a_params)
        return a_params

    def page_number(self):
        return self.m_page_number

def process_pages(a_page_traits, a_page_query):
        more_data = True
        cnt = 0
        while more_data:
            params=a_page_traits.params({})
            data_page = a_page_query.query(a_params=params)
            more_data = a_page_traits.more_data(data_page)
            logging.info ("Found {} items {}".format(len(data_page["items"]), "({})".format("unpaginated" if a_page_traits.page_number() == 1 else "last page") if not more_data else "(page {})".format(a_page_traits.page_number())))
            for da in data_page["items"]:
                cnt+=1
                a_page_query.result(da)
                logging.debug (json.dumps(da, sort_keys=True, indent=4))
                
        logging.info ("Found {} total items".format(cnt))