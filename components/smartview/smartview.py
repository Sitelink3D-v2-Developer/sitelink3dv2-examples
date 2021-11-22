#!/usr/bin/env python

import base64
import requests
import logging

def b64(x): return base64.urlsafe_b64encode(x.encode("utf-8")).decode("utf-8").replace("=","",4)

class SmartView(object):
    def __init__(self, app):
        self.app_b64 = b64(app)

    def configure(self, base_url, site, token):
        self.url = "{}/smart_view/v2/sites/{}/apps/{}".format(base_url, site, self.app_b64)
        self.headers = token
        return self

    def stream_data(self, args):
        start_b64 = b64("{\"from\":\"continuous\"}")
        url = "{}/start/{}".format(self.url, start_b64)
        logging.info("subscribing to {}".format(url))
        response = requests.get(url, stream=True, headers=self.headers, params=args)
        response.raise_for_status()
        for text_line in response.iter_lines():
            yield text_line.strip().decode("utf-8")