#!/usr/bin/python
import re

class ReportTraitsBase():
    def __init__(self, a_results_header, a_report_type, a_results_key, a_output_format):
        self.m_results_header = a_results_header
        self.m_report_type = a_report_type
        self.m_results_key = a_results_key
        self.m_output_format = a_output_format

    def results_header(self):
        return self.m_results_header

    def report_type(self):
        return self.m_report_type

    def job_params(self, a_report_name, a_start_unix_time_millis, a_end_unix_time_millis):
        return {
            "name": a_report_name,
            "from": a_start_unix_time_millis,
            "to":   a_end_unix_time_millis
        }        

    def download_url_from_job_results(self, a_job_results):
        if self.m_results_key in a_job_results["results"] and self.m_output_format in a_job_results["results"][self.m_results_key]:
            return [a_job_results["results"][self.m_results_key][self.m_output_format], re.sub(r'[^0-9_-a-zA-z]', '_', a_job_results["params"]["name"]) + "." + self.m_output_format]

class HaulReportTraits(ReportTraitsBase):
    def __init__(self, a_report_subtype, a_results_header):
        ReportTraitsBase.__init__(self, a_results_header, "haul_report", "hauls", "xlsx")
        self.report_subtype = a_report_subtype

    def job_params(self, a_report_name, a_start_unix_time_millis, a_end_unix_time_millis):
        params = ReportTraitsBase.job_params(self, a_report_name, a_start_unix_time_millis, a_end_unix_time_millis)
        params["subtype"] = self.report_subtype
        return params       

class DelayReportTraits(ReportTraitsBase):
    def __init__(self, a_results_header):
        ReportTraitsBase.__init__(self, a_results_header, "delay_report", "delays", "xlsx")

class WeightReportTraits(ReportTraitsBase):
    def __init__(self ):
        ReportTraitsBase.__init__(self, {'content-type': 'application/json'}, "weight_report", "weights", "xlsx")

class ActivityReportTraits(ReportTraitsBase):
    def __init__(self ):
        ReportTraitsBase.__init__(self, {'content-type': 'application/json'}, "activity_report", "activity", "csv")
