# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
from datetime import datetime
import time
from typing import List, Dict
import boto3
import yaml

PROFILE_NAME = 'default'
boto3.setup_default_session(profile_name=PROFILE_NAME)
client = boto3.client('iotsitewise')
s3_client = boto3.client('s3')

dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.dirname(dir))
config_dir = f'{root_dir}/config'
data_dir = f'{root_dir}/data'

# Load bulk import configuration
with open(f'{config_dir}/bulk_import.yml', 'r') as file:
    bulk_import_config = yaml.safe_load(file)

job_ids = []

def get_s3_keys() -> List[str]:
    response = s3_client.list_objects_v2(Bucket=bulk_import_config["data"]["bucket"], Prefix=bulk_import_config["data"]["prefix"])
    s3_keys = []
    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        content_records = response["Contents"]
        s3_keys = [record["Key"] for record in content_records]
    return s3_keys

def create_job(s3_key: str) -> Dict:
    response = client.create_bulk_import_job(
        jobName= f'job_{str(int(datetime.now().timestamp()))}',
        jobRoleArn=bulk_import_config["job"]["role_arn"],
        files=[
            {
                'bucket': bulk_import_config["data"]["bucket"],
                'key': s3_key
            },
        ],
        errorReportLocation={
            'bucket': bulk_import_config["job"]["error_bucket"],
            'prefix': bulk_import_config["job"]["error_prefix"]
        },
        jobConfiguration={
            'fileFormat': {
                'csv': {
                    'columnNames': bulk_import_config["data"]["column_names"]
                }
            }
        }
    )
    return response

def create_jobs() -> None:
    s3_keys = get_s3_keys()
    print(f'Total S3 objects: {len(s3_keys)}')
    if len(s3_keys) > 0: 
        print(f'Number of bulk import jobs to create: {len(s3_keys)}')
    else:
        print('No data found in S3!')

    for s3_key in s3_keys:
        job_id = create_job(s3_key)['jobId']
        print(f'\tCreated job: {job_id} for importing data from {s3_key} S3 object')
        job_ids.append(job_id)
        time.sleep(1)

def list_bulk_import_jobs() -> List[Dict]:
    all_jobs = []
    response = client.list_bulk_import_jobs(maxResults=250)
    all_jobs = response["jobSummaries"]
    while True:
        # If there are more jobs, get the next page of results
        if 'nextToken' in response:
            response = client.list_bulk_import_jobs(nextToken=response['nextToken'])
            all_jobs = all_jobs + response["jobSummaries"]
        else:
            break  # No more jobs, exit the loop
    return all_jobs

def job_status(job_id: str) -> str:
    status = None
    for job in list_bulk_import_jobs():
        if job['id'] == job_id: status = job["status"] 
    return status

def check_job_status() -> None:
    SLEEP_SECS = 5
    active_job_ids = job_ids.copy()
    print(f'Checking job status every {SLEEP_SECS} secs until completion..')

    while True:
        for job_id in active_job_ids:
            status=job_status(job_id)
            if status not in ['PENDING','RUNNING']:
                print(f'\tJob id: {job_id}, status: {status}')
                active_job_ids.remove(job_id)
        if len(active_job_ids) == 0: 
            break
        time.sleep(SLEEP_SECS)

def start() -> None:
    create_jobs()
    check_job_status()

if __name__ == "__main__":
    start()
    print('Script execution successfully completed!!')