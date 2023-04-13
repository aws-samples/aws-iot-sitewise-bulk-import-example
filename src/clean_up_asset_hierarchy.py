# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import time
import json
import csv
import yaml
import os
from typing import List, Dict
import boto3
import glob

PROFILE_NAME = 'default'
boto3.setup_default_session(profile_name=PROFILE_NAME)
client = boto3.client('iotsitewise')
dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.dirname(dir))
config_dir = f'{root_dir}/config'
data_dir = f'{root_dir}/data'
tmp_dir = f'{root_dir}/tmp'

# Load assets_models_configuration
with open(f'{config_dir}/assets_models.yml', 'r') as file:
    assets_models_config = yaml.safe_load(file)

def print_json(dict_obj: Dict) -> None:
    print(json.dumps(dict_obj, indent=2, default=str))

def get_model_id_by_name(asset_model_name) -> str:
    with open(f'{tmp_dir}/asset_models.csv', 'r') as f:
        models = csv.DictReader(f)
        for model in models:
            # condition to match
            if model['asset_model_name'] == asset_model_name:
                return model['asset_model_id']

def get_asset_id_by_name(asset_name) -> str:
    with open(f'{tmp_dir}/assets.csv', 'r') as f:
        assets = csv.DictReader(f)
        for asset in assets:
            # condition to match
            if asset['asset_name'] == asset_name:
                return asset['asset_id']

def get_hierarchy_id(asset_model_name, child_asset_model_id) -> str:
    with open(f'{tmp_dir}/hierarchies.csv', 'r') as f:
        hierarchies = csv.DictReader(f)
        for hierarchy in hierarchies:
            # condition to match
            if hierarchy['asset_model_name'] == asset_model_name and hierarchy['child_asset_model_id'] == child_asset_model_id: 
                return hierarchy['hierarchy_id']

def get_asset_model_status(asset_model_id: str) -> str:
    response = client.describe_asset_model(
        assetModelId=asset_model_id
    )
    return response["assetModelStatus"]["state"]

def disassociate_assets(assets: List[Dict]) -> None:
    for asset in assets:
        asset_id = get_asset_id_by_name(asset["name"])
        model_name = asset["model"]
        associated_assets = asset["associated_assets"]
        # Create associations
        if associated_assets is not None:
            for child_asset_name in associated_assets:
                child_asset_model_name = [asset["model"] for asset in assets_models_config["assets"] if asset["name"] == child_asset_name][0]
                child_asset_model_id = get_model_id_by_name(child_asset_model_name)
                hierarchy_id = get_hierarchy_id(model_name, child_asset_model_id)
                child_asset_id = get_asset_id_by_name(child_asset_name)
                client.disassociate_assets(assetId=asset_id, hierarchyId=hierarchy_id, childAssetId=child_asset_id)

def delete_assets(assets: List[Dict]) -> None:
    for asset in assets:
        asset_name = asset["name"]
        asset_id = get_asset_id_by_name(asset_name)
        client.delete_asset(assetId=asset_id)
    time.sleep(5)

def remove_hierarchies(asset_models: List[Dict]) -> None:
    for model in asset_models:
        model_name = model["name"]
        model_id = get_model_id_by_name(model_name)
        client.update_asset_model(assetModelId=model_id, assetModelName=model_name)
        while True:
            model_status = get_asset_model_status(model_id)
            if model_status == "ACTIVE": 
                break
            time.sleep(1)

def delete_asset_models(asset_models: List[Dict]) -> None:
    for model in asset_models:
        model_name = model["name"]
        model_id = get_model_id_by_name(model_name)
        client.delete_asset_model(assetModelId=model_id)
        time.sleep(5)

def cleanup_filesystem():
    data_files = glob.glob(os.path.join(data_dir, "*"))
    for f in data_files: os.remove(f)
    tmp_files = glob.glob(os.path.join(tmp_dir, "*"))
    for f in tmp_files: os.remove(f)

def delete_asset_hierarchy() -> None:
    print('Removing asset associations..')
    disassociate_assets(assets_models_config["assets"])
    print('All assets updated!')
    print('Deleting assets..')
    delete_assets(assets_models_config["assets"])
    print('All assets deleted!')
    print('Removing hierarchy definitions from models..')
    remove_hierarchies(assets_models_config["asset_models"])
    print('All hierarchy definitions removed!')
    print('Deleting asset models..')
    delete_asset_models(assets_models_config["asset_models"])
    print('All asset models deleted!')

def start() -> None:
    delete_asset_hierarchy() 
    print('Cleaning up the filesystem..')
    cleanup_filesystem()
    print('Data and temporary files removed!')

if __name__ == "__main__":
    start()
    print('Script execution successfully completed!!')