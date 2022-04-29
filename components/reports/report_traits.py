#!/usr/bin/python
import re
import requests

session = requests.Session()

class ReportTraitsBase():
    def __init__(self, a_results_header, a_start_unix_time_millis, a_end_unix_time_millis, a_report_type, a_result_targets):
        self.m_results_header = a_results_header
        self.m_report_type = a_report_type
        self.m_start_unix_time_millis = a_start_unix_time_millis
        self.m_end_unix_time_millis = a_end_unix_time_millis
        self.m_result_targets = a_result_targets

    def results_header(self):
        return self.m_results_header

    def report_type(self):
        return self.m_report_type

    def job_params(self, a_report_name):
        params = {}
        ReportTraitsBase.add_name_params(self, params, a_report_name)
        ReportTraitsBase.add_time_range_params(self, params, self.m_start_unix_time_millis, self.m_end_unix_time_millis)
        return params
        
    def add_name_params(self, a_params, a_report_name):
        a_params["name"] = a_report_name
     
    def add_time_range_params(self, a_params, a_start_unix_time_millis, a_end_unix_time_millis):
        a_params["from"] = a_start_unix_time_millis
        a_params["to"] = a_end_unix_time_millis   

    def add_time_epoch_params(self, a_params, a_date_unix_time_millis):
        a_params["date"] = a_date_unix_time_millis

    def download_urls_from_job_results(self, a_job_results, a_headers):
        download_urls = []
        for result_target in self.m_result_targets:
            key, formats = result_target
            for format in formats:
                if key in a_job_results["results"] and format in a_job_results["results"][key]:
                    download_urls.append([a_job_results["results"][key][format], re.sub(r'[^0-9_-a-zA-z]', '_', a_job_results["params"]["name"]) + "." + key + "." + format])
        return download_urls

class HaulReportTraits(ReportTraitsBase):
    def __init__(self, a_haul_states, a_start_unix_time_millis, a_end_unix_time_millis, a_results_header):
        ReportTraitsBase.__init__(self, a_results_header, a_start_unix_time_millis, a_end_unix_time_millis, "haul_report", [["hauls",["xlsx","json"]], ["trails",["json", "jsonl"]], ["aggregates-dump_region-average",["json"]], ["aggregates-dump_region-total",["json"]], ["aggregates-load_region-average",["json"]], ["aggregates-load_region-total",["json"]], ["aggregates-machine-average",["json"]], ["aggregates-machine-total",["json"]], ["aggregates-material-average",["json"]], ["aggregates-material-total",["json"]], ["aggregates-operator-average",["json"]], ["aggregates-operator-total",["json"]]])
        self.haul_states = a_haul_states

    def job_params(self, a_report_name):
        params = {}
        ReportTraitsBase.add_name_params(self, params, a_report_name)
        ReportTraitsBase.add_time_range_params(self, params, self.m_start_unix_time_millis, self.m_end_unix_time_millis)
        params["status"] = self.haul_states
        return params       

class DelayReportTraits(ReportTraitsBase):
    def __init__(self, a_start_unix_time_millis, a_end_unix_time_millis, a_results_header):
        ReportTraitsBase.__init__(self, a_results_header, a_start_unix_time_millis, a_end_unix_time_millis, "delay_report", [["delays", ["xlsx","json"]]])

class WeightReportTraits(ReportTraitsBase):
    def __init__(self, a_start_unix_time_millis, a_end_unix_time_millis, a_results_header):
        ReportTraitsBase.__init__(self, a_results_header, a_start_unix_time_millis, a_end_unix_time_millis, "weight_report", [["weights", ["xlsx","json"]], ["tracks", ["json"]], ["lifts", ["json"]], ["aggregates-truck-total", ["json"]], ["aggregates-truck-material", ["json"]], ["aggregates-operator-total", ["json"]], ["aggregates-operator-material", ["json"]], ["aggregates-note-total", ["json"]], ["aggregates-mix-total", ["json"]], ["aggregates-material-total", ["json"]], ["aggregates-material-material", ["json"]], ["aggregates-machine-total", ["json"]], ["aggregates-machine-material", ["json"]], ["aggregates-location-total", ["json"]], ["aggregates-location-material", ["json"]], ["aggregates-load_region-total", ["json"]], ["aggregates-load_region-material", ["json"]], ["aggregates-haulier-total", ["json"]], ["aggregates-haulier-material", ["json"]], ["aggregates-haul-total", ["json"]], ["aggregates-haul-material", ["json"]], ["aggregates-dump_region-total", ["json"]], ["aggregates-dump_region-material", ["json"]], ["aggregates-destination-total", ["json"]], ["aggregates-destination-material", ["json"]], ["aggregates-customer-total", ["json"]], ["aggregates-customer-material", ["json"]]])

class ActivityReportTraits(ReportTraitsBase):
    def __init__(self, a_start_unix_time_millis, a_end_unix_time_millis, a_results_header):
        ReportTraitsBase.__init__(self, a_results_header, a_start_unix_time_millis, a_end_unix_time_millis, "activity_report", [["activity", ["csv","jsonl"]]])

class HeightMapReportTraitsBase():
    def __init__(self, a_server_config, a_site_id, a_date_unix_time_millis, a_report_type, a_result_target, a_results_header, a_mask_region_uuid=None, a_task_uuid=None, a_seqence_instance=None):
        self.m_server_config = a_server_config
        self.m_site_id = a_site_id
        self.m_results_header = a_results_header
        self.m_date_unix_time_millis = a_date_unix_time_millis
        self.m_report_type = a_report_type
        self.m_result_target = a_result_target
        self.m_mask_region_uuid = a_mask_region_uuid
        self.m_task_uuid = a_task_uuid
        self.m_sequence_instance = a_seqence_instance

    def results_header(self):
        return self.m_results_header

    def report_type(self):
        return self.m_report_type

    def job_params(self, a_report_name):
        params = {}
        ReportTraitsBase.add_name_params(self, params, a_report_name)
        ReportTraitsBase.add_time_epoch_params(self, params, self.m_date_unix_time_millis)

        if self.m_mask_region_uuid is not None:
            if len(self.m_mask_region_uuid) > 0:
                params["mask_region"] = self.m_mask_region_uuid
        
        if self.m_task_uuid is not None:
            if len(self.m_task_uuid) > 0:
                params["sequence"] = self.m_task_uuid + ":" + self.m_sequence_instance

        params["tileConfig"] = {
            "cellTemplate": "default",
            "default": {
                "cellSize": "512",
                "additionalMeasure": "pass"
            }
        }
        
        return params   

    def download_urls_from_job_results(self, a_job_results, a_headers):
        download_urls = []

        if self.m_result_target in a_job_results["results"]:
            report_uuid = a_job_results["results"][self.m_result_target]
       
            url = "{0}/reporting/v1/sites/{1}/files/{2}/requests".format(self.m_server_config.to_url(), self.m_site_id, report_uuid)

            response = session.post(url, headers=a_headers, data={})
            report_key = response.json()["message"]
            download_url = "{0}/reporting/v1/files/{1}".format(self.m_server_config.to_url(), report_key)
            download_urls.append([download_url, re.sub(r'[^0-9_-a-zA-z]', '_', a_job_results["params"]["name"]) + "." + self.m_result_target])
            
        return download_urls               

class PlyHeightMapReportTraits(HeightMapReportTraitsBase):
    def __init__(self, a_server_config, a_site_id, a_date_unix_time_millis, a_mask_region_uuid=None, a_task_uuid=None, a_seqence_instance=None):
        HeightMapReportTraitsBase.__init__(self, a_server_config, a_site_id, a_date_unix_time_millis, "height_map", "points.ply", {'content-type': 'application/json'}, a_mask_region_uuid=a_mask_region_uuid, a_task_uuid=a_task_uuid, a_seqence_instance=a_seqence_instance) 

    def job_params(self, a_report_name):
        params = HeightMapReportTraitsBase.job_params(self, a_report_name)
        params["format"] = "ply"
        return params  

class XyzHeightMapReportTraits(HeightMapReportTraitsBase):
    def __init__(self, a_server_config, a_site_id, a_date_unix_time_millis, a_mask_region_uuid=None, a_task_uuid=None, a_seqence_instance=None):
        HeightMapReportTraitsBase.__init__(self, a_server_config, a_site_id, a_date_unix_time_millis, "height_map", "points.xyz", {'content-type': 'application/json'}, a_mask_region_uuid=a_mask_region_uuid, a_task_uuid=a_task_uuid, a_seqence_instance=a_seqence_instance) 

    def job_params(self, a_report_name):
        params = HeightMapReportTraitsBase.job_params(self, a_report_name)
        params["format"] = "xyz"
        return params  
