#!/usr/bin/python
import os
import sys
import getpass

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["utils", "get_token", "report_download", "events"]:
    exec(import_cmd(components_dir, imp))

def fetch_job(a_server_config, a_site_id, a_term, a_job_id, a_headers):
    url = "{}/reporting/v1/{}/{}/{}".format(a_server_config.to_url(), a_site_id, a_term, a_job_id)
    return json_from(requests.get(url, headers=a_headers))

def poll_job(a_server_config, a_site_id, a_report_term, a_report_job_id, a_headers):
    job = fetch_job(a_server_config, a_site_id, a_report_term, a_report_job_id, a_headers)
    status = job.get("status") or "SUBMITTED"
    while status not in ["CANCELLED", "COMPLETE", "FAILED"]:
        logging.info("Polled job {} status is {} ...".format(a_report_job_id, status))
        time.sleep(5)
        job = fetch_job(a_server_config, a_site_id, a_report_term, a_report_job_id, a_headers)
        status = job.get("status", "SUBMITTED")
    job = fetch_job(a_server_config, a_site_id, a_report_term, a_report_job_id, a_headers)
    logging.info("Polled job {} final status is {}.".format(a_report_job_id, status))    

def create_report(a_server_config, a_site_id,a_report_name, a_report_traits, a_report_term, a_headers):
    frame = {
        "site_id"    : a_site_id,
        "source"     : "API",
        "job_type"   : "rpt::{}".format(a_report_traits.report_type()),
        "issued_by"  : "{} via API".format(getpass.getuser()),
        "params": a_report_traits.job_params(a_report_name=a_report_name),
        "results": {}
    }
    url = "{}/reporting/v1/{}/{}".format(a_server_config.to_url(), a_site_id, a_report_term)
    j = json_from(requests.post(url, data=json.dumps(frame), headers=a_headers))

    return j["_id"]    

def download_urls_for_job(a_server_config, a_site_id, a_report_traits, a_report_term, a_job_id, a_headers):
    url = "{}/reporting/v1/{}/{}/{}".format(a_server_config.to_url(), a_site_id, a_report_term, a_job_id)
    result = json_from(requests.get(url, headers=a_headers))
    return a_report_traits.download_urls_from_job_results(result, a_headers)

def report_job_poll_monitor(a_server_config, a_site_id, a_report_term, report_job_id, a_headers):
    poll_job(a_server_config=a_server_config, a_site_id=a_site_id, a_report_term=a_report_term, a_report_job_id=report_job_id, a_headers=a_headers)

class ReportJobMonitorBase():
    def __init__(self, a_server_config, a_site_id, a_report_term, a_headers):
        self.m_server_config = a_server_config
        self.m_site_id = a_site_id
        self.m_report_term = a_report_term
        self.m_headers = a_headers

    def monitor_job(self, report_job_id):
        return

class ReportJobMonitorPoll(ReportJobMonitorBase):
    def __init__(self, a_server_config, a_site_id, a_report_term, a_headers):
        ReportJobMonitorBase.__init__(self, a_server_config, a_site_id, a_report_term, a_headers)

    def monitor_job(self, a_report_job_id):
        poll_job(a_server_config=self.m_server_config, a_site_id=self.m_site_id, a_report_term=self.m_report_term, a_report_job_id=a_report_job_id, a_headers=self.m_headers)


class ReportJobMonitorEvent(ReportJobMonitorBase):
    def __init__(self, a_server_config, a_site_id, a_report_term, a_headers):
        ReportJobMonitorBase.__init__(self, a_server_config, a_site_id, a_report_term, a_headers)
        self.m_event_manager = HttpEventManager(a_server_config=self.m_server_config, a_identifier=self.m_site_id, a_headers=self.m_headers, a_source=EventSource.Site)

    def monitor_job(self, a_report_job_id):

        # Event data for report jobs take the following form. Construct an expected payload to wait on. This can either be COMPLETED of FAILED
        #
        # "event": {
        #     "type": "update",
        #     "service": "spark-reporting",
        #     "url": "https://sitelink-cloudsr-edge.marathon.l4lb.thisdcos.directory:9094/spark_reports/v1/longterms",
        #     "data": {
        #         "_id": "0991b75e-6b97-11ed-9f2a-0242ac11000d",
        #         "_type": "rpt::haul_report",
        #         "source": "API",
        #         "status": "RUNNING",
        #         "urn": "urn:X-topcon:le:b3668728-bde0-4f5f-8321-84299caad3a5:owner:ce235e5e-6d87-4a84-80f2-0e56b137a132:site:d304550f-8ce2-41e7-a9a6-c33dd2fcf14e:reporting:job:0991b75e-6b97-11ed-9f2a-0242ac11000d"
        #     }
        # }    
        expected_failed_event = {
            "type": "update",
            "service": "spark-reporting",
            "data": {
                "_id": a_report_job_id,
                "source": "API",
                "status": "FAILED",

            }        
        }

        expected_completed_event = {
            "type": "update",
            "service": "spark-reporting",
            "data": {
                "_id": a_report_job_id,
                "source": "API",
                "status": "COMPLETE",

            }
        }  

        expected_event_list = [expected_failed_event, expected_completed_event]
        response = self.m_event_manager.wait_for_data({"scope":"site", "id":self.m_site_id}, "message", expected_event_list, None)
        logging.info("Event job {} response is {} ...".format(a_report_job_id, response["event"]["data"]["status"]))


def report_job_monitor_factory(a_data_method, a_server_config, a_site_id, a_report_term, a_headers):
    monitor = None
    if("poll" == a_data_method):
        monitor = ReportJobMonitorPoll(a_server_config, a_site_id, a_report_term, a_headers)
    elif("event" == a_data_method):
        monitor = ReportJobMonitorEvent(a_server_config, a_site_id, a_report_term, a_headers)

    return monitor


def create_and_download_report(a_server_config, a_site_id, a_report_name, a_report_traits, a_report_term, a_target_dir, a_job_report_monitor_callback, a_headers):
    report_job_id = create_report(a_server_config=a_server_config, a_site_id=a_site_id, a_report_name=a_report_name, a_report_traits=a_report_traits, a_report_term=a_report_term, a_headers=a_headers)
    logging.info("Submitted [{}] called [{}] with job identifier [{}]".format(a_report_traits.report_type(), a_report_name, report_job_id))
    a_job_report_monitor_callback(a_report_job_id=report_job_id)

    targets = download_urls_for_job(a_server_config=a_server_config, a_site_id=a_site_id, a_report_traits=a_report_traits, a_report_term=a_report_term, a_job_id=report_job_id, a_headers=a_headers)
    
    for target in targets:
        if None == target:
            logging.info("No results.")
        else:
            url, name = target
            logging.debug("downloading report at URL {}".format(url))
            download_report(a_report_url=url, a_headers=a_report_traits.results_header(), a_target_dir=a_target_dir, a_report_name=name) 
