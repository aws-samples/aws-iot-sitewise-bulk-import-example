import boto3
from datetime import datetime
import time


PROFILE_NAME = 'bulkimport'
boto3.setup_default_session(profile_name=PROFILE_NAME)
client = boto3.client('iotsitewise')

def list_bulk_import_jobs():
    response = client.list_bulk_import_jobs(
        maxResults=100
    )
    return response

print(list_bulk_import_jobs()["jobSummaries"])