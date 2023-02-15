import yaml
import os
import boto3

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
    local_file_path = f'{data_dir}/historical_data.csv'
    s3_key = bulk_import_config["data"]["key"]
    s3_client.upload_file(local_file_path, s3_bucket, s3_key)
    print(f'Successfully uploaded historical data to S3!')

def start() -> None:
    upload_history_to_s3()

if __name__ == "__main__":
    start()
    print('Script execution successfully completed!!')