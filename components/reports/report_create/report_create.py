#!/usr/bin/python
import argparse
import logging
import os
import sys
import requests
import json
import uuid
import getpass

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))

from get_token import *
from utils import *

def fetch_job(a_server_config, a_site_id, a_term, a_job_id, a_headers):
    url = "{}/reporting/v1/{}/{}/{}".format(a_server_config.to_url(), a_site_id, a_term, a_job_id)
    return json_from(requests.get(url, headers=a_headers))

def poll_job(a_server_config, a_site_id, a_term, a_job_id, a_headers):
    job = fetch_job(a_server_config, a_site_id, a_term, a_job_id, a_headers)
    status = job.get("status") or "SUBMITTED"
    while status not in ["CANCELLED", "COMPLETE", "FAILED"]:
        print("Job {} status is {} ...".format(a_job_id, status))
        time.sleep(5)
        job = fetch_job(a_server_config, a_site_id, a_term, a_job_id, a_headers)
        status = job.get("status", "SUBMITTED")
    job = fetch_job(a_server_config, a_site_id, a_term, a_job_id, a_headers)
    print("Job {} final status is {}.".format(a_job_id, status))    

def download_report(a_report_url, a_headers, a_target_dir, a_report_name):
    response = session.get(a_report_url, headers=a_headers, allow_redirects=False)
    if response.status_code in [301,302]:
        response = requests.get(response.headers['Location'])
    response.raise_for_status()
    if not os.path.exists(a_target_dir):
        os.makedirs(a_target_dir, exist_ok=True)

    output_file = os.path.join(a_target_dir, a_report_name)
    with open(output_file, "wb") as f:
        f.write(response.content)
        logging.info("Saved report {}".format(output_file))

def create_report(a_server_config, a_site_id,a_report_name, a_report_traits, a_report_term, a_headers):
    frame = {
        "_id"        : str(uuid.uuid1()),
        "site_id"    : a_site_id,
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

def create_and_download_report(a_server_config, a_site_id, a_report_name, a_report_traits, a_report_term, a_target_dir, a_headers):
    report_job_id = create_report(a_server_config=a_server_config, a_site_id=a_site_id, a_report_name=a_report_name, a_report_traits=a_report_traits, a_report_term=a_report_term, a_headers=a_headers)
    logging.info("Submitted [{}] called [{}] with job identifier [{}]".format(a_report_traits.report_type(), a_report_name, report_job_id))
    poll_job(a_server_config=a_server_config, a_site_id=a_site_id, a_term=a_report_term, a_job_id=report_job_id, a_headers=a_headers)

    targets = download_urls_for_job(a_server_config=a_server_config, a_site_id=a_site_id, a_report_traits=a_report_traits, a_report_term=a_report_term, a_job_id=report_job_id, a_headers=a_headers)
    
    for target in targets:
        if None == target:
            print("No results.")
        else:
            url, name = target
            logging.debug(url)
            download_report(a_report_url=url, a_headers=a_report_traits.results_header(), a_target_dir=a_target_dir, a_report_name=name) 
