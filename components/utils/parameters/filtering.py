#!/usr/bin/python
import logging
import base64
import json

def add_filter_term(a_filter, a_field_name, a_operation, a_value):
    verified = True
    if type(a_value) == str: 
        if len(a_value) == 0:
            verified = False
    if type(a_value) == list and len(a_value) == 1 and len(a_value[0]) == 0:
        verified = False
    if verified:
        a_filter[a_field_name] = {"op": a_operation, "val": a_value}
    return a_filter

def filter_params(a_params, a_filters):
    a_params["filter"] = base64.urlsafe_b64encode(json.dumps(a_filters).encode('utf-8')).decode('utf-8').rstrip("=")
    return a_params
