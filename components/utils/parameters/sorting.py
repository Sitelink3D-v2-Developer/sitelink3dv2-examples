#!/usr/bin/python
import logging
import base64
import json

class SortTraits():
    def __init__(self, a_sort_field, a_sort_order):
        self.m_sort_field = a_sort_field
        self.m_sort_order = a_sort_order

    def params(self, a_params):
        if len(self.m_sort_field) > 0:
            a_params["order"] = self.m_sort_order + self.m_sort_field
        return a_params

