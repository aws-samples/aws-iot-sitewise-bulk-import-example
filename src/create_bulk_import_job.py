import yaml
import os
import boto3
from datetime import datetime
import time

client = boto3.client('iotsitewise')
s3_client = boto3.client('s3')

dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.dirname(dir))
config_dir = f'{root_dir}/config'
data_dir = f'{root_dir}/data'

# Load bulk import configuration
with open(f'{config_dir}/bulk_import.yml', 'r') as file:
    bulk_import_config = yaml.safe_load(file)

script_start_timestamp = int(datetime.now().timestamp())

def create_job():
    response = client.create_bulk_import_job(
        jobName= str(script_start_timestamp),
        jobRoleArn=bulk_import_config["job"]["role_arn"],
        files=[
            {
                'bucket': bulk_import_config["data"]["bucket"],
                'key': bulk_import_config["data"]["key"]
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

def list_bulk_import_jobs():
    response = client.list_bulk_import_jobs(
        maxResults=100
    )
    return response

def job_status(job_id):
    status = None
    for job in list_bulk_import_jobs()["jobSummaries"]:
        if job['id'] == job_id: status = job["status"] 
    return status

def start() -> None:
    job_id = create_job()['jobId']
    print(f'Created job: {job_id}')
    SLEEP_SECS = 5
    print(f'Checking job status every {SLEEP_SECS} secs until done..')

    while True:
        status=job_status(job_id)
        if status not in ['PENDING','RUNNING']:
            print(f'Job status: {status}')
            break
        time.sleep(SLEEP_SECS)

if __name__ == "__main__":
    start()
    print('Script execution successfully completed!!')