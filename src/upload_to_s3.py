# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import yaml
import os
import boto3
import glob

PROFILE_NAME = 'bulkimport'
boto3.setup_default_session(profile_name=PROFILE_NAME)
s3_client = boto3.client('s3')

dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.dirname(dir))
config_dir = f'{root_dir}/config'
data_dir = f'{root_dir}/data'

# Load bulk import configuration
with open(f'{config_dir}/bulk_import.yml', 'r') as file:
    bulk_import_config = yaml.safe_load(file)

def upload_history_to_s3() -> None:
    s3_bucket = bulk_import_config["data"]["bucket"]
    data_files = glob.glob(os.path.join(data_dir, "*"))
    for local_file_path in data_files:
        file_name = local_file_path.split('/')[-1]
        prefix = bulk_import_config["data"]["prefix"]
        s3_key = f'{prefix}{file_name}'
        s3_client.upload_file(local_file_path, s3_bucket, s3_key)
    print(f'Successfully uploaded historical data to S3!')

def start() -> None:
    print('Uploading historical data files into Amazon S3..')
    upload_history_to_s3()

if __name__ == "__main__":
    start()
    print('Script execution successfully completed!!')