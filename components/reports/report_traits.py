#!/usr/bin/python
import re

class HaulReportTraits():
    def __init__(self, a_report_subtype, a_results_header):
        self.report_subtype = a_report_subtype
        self.header = a_results_header

    def report_type(self):
        return "haul_report"

    def job_params(self, a_report_name, a_start_unix_time_millis, a_end_unix_time_millis):
        return {
            "subtype" : self.report_subtype,
            "name": a_report_name,
            "from": a_start_unix_time_millis,
            "to":   a_end_unix_time_millis
        }

    def download_url_from_job_results(self, a_job_results):
        if "hauls" in a_job_results["results"] and "xlsx" in a_job_results["results"]["hauls"]:
            return [a_job_results["results"]["hauls"]["xlsx"], re.sub(r'[^0-9_-a-zA-z]', '_', a_job_results["params"]["name"]) + ".xlsx"]
        
    def results_header(self):
        return self.header

class DelayReportTraits():
    def __init__(self, a_results_header):
        self.header = a_results_header

    def report_type(self):
        return "delay_report"

    def job_params(self, a_report_name, a_start_unix_time_millis, a_end_unix_time_millis):
        return {
            "name": a_report_name,
            "from": a_start_unix_time_millis,
            "to":   a_end_unix_time_millis
        }
        
    def results_header(self):
        return self.header   

    def download_url_from_job_results(self, a_job_results):
        if "delays" in a_job_results["results"] and "xlsx" in a_job_results["results"]["delays"]:
            return [a_job_results["results"]["delays"]["xlsx"], re.sub(r'[^0-9_-a-zA-z]', '_', a_job_results["params"]["name"]) + ".xlsx"]

class WeightReportTraits():
    def report_type(self):
        return "weight_report"

    def job_params(self, a_report_name, a_start_unix_time_millis, a_end_unix_time_millis):
        return {
            "name": a_report_name,
            "from": a_start_unix_time_millis,
            "to":   a_end_unix_time_millis
        }
        
    def results_header(self):
        return {'content-type': 'application/json'}

    def download_url_from_job_results(self, a_job_results):
        if "weights" in a_job_results["results"] and "xlsx" in a_job_results["results"]["weights"]:
            return [a_job_results["results"]["weights"]["xlsx"], re.sub(r'[^0-9_-a-zA-z]', '_', a_job_results["params"]["name"]) + ".xlsx"]

