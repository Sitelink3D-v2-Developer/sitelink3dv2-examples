#!/usr/bin/python
import re

class ReportTraitsBase():
    def __init__(self, a_results_header, a_report_type, a_result_targets):
        self.m_results_header = a_results_header
        self.m_report_type = a_report_type
        self.m_result_targerts = a_result_targets

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

    def download_urls_from_job_results(self, a_job_results):
        download_urls = []

        for result_target in self.m_result_targerts:
            key, formats = result_target
            for format in formats:
                if key in a_job_results["results"] and format in a_job_results["results"][key]:
                    download_urls.append([a_job_results["results"][key][format], re.sub(r'[^0-9_-a-zA-z]', '_', a_job_results["params"]["name"]) + "." + key + "." + format])
        return download_urls

class HaulReportTraits(ReportTraitsBase):
    def __init__(self, a_report_subtype, a_results_header):
        ReportTraitsBase.__init__(self, a_results_header, "haul_report", [["hauls", ["xlsx","url"]], ["trails",["url"]]])
        self.report_subtype = a_report_subtype

    def job_params(self, a_report_name, a_start_unix_time_millis, a_end_unix_time_millis):
        params = ReportTraitsBase.job_params(self, a_report_name, a_start_unix_time_millis, a_end_unix_time_millis)
        params["subtype"] = self.report_subtype
        return params       

class DelayReportTraits(ReportTraitsBase):
    def __init__(self, a_results_header):
        ReportTraitsBase.__init__(self, a_results_header, "delay_report", [["delays", ["xlsx","url"]]])

class WeightReportTraits(ReportTraitsBase):
    def __init__(self ):
        ReportTraitsBase.__init__(self, {'content-type': 'application/json'}, "weight_report", [["weights", ["xlsx","json","url"]]])

class ActivityReportTraits(ReportTraitsBase):
    def __init__(self ):
        ReportTraitsBase.__init__(self, {'content-type': 'application/json'}, "activity_report", [["activity", ["csv","jsonl"]]])
