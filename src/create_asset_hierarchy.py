# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import time
import json
import csv
import yaml
import os
import boto3

PROFILE_NAME = 'default'
boto3.setup_default_session(profile_name=PROFILE_NAME)
client = boto3.client('iotsitewise')
dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.dirname(dir))
config_dir = f'{root_dir}/config'
schema_dir = f'{root_dir}/schema'
tmp_dir = f'{root_dir}/tmp'

# Create tmp directory if doesn't exist
if not os.path.exists(tmp_dir): os.makedirs(tmp_dir)

# Load assets_models_configuration
with open(f'{config_dir}/assets_models.yml', 'r') as file:
    assets_models_config = yaml.safe_load(file)

def print_json(dict_obj: dict) -> None:
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
            
def create_asset_model(model: dict) -> str:
    model_name = model["name"]
    properties_schema = []
    # file name -> sample_stamping_press_properties.json for the model: Sample_Stamping Press
    properties_schema_file_name = '_'.join(model_name.lower().split())+"_properties.json"
    properties_schema_file_path = f'{schema_dir}/{properties_schema_file_name}'
    # Load schema if existing
    if os.path.exists(properties_schema_file_path):
        with open(properties_schema_file_path, 'r') as file:
            properties_schema = json.load(file)
    response = client.create_asset_model(
        assetModelName= model_name,
        assetModelProperties = properties_schema
    )
    asset_model_id = response["assetModelId"]
    print(f"\tCreated name: {model_name}, id: {asset_model_id}")
    return asset_model_id

def update_asset_model(model: dict) -> None:
    model_name = model["name"]
    model_id = get_model_id_by_name(model_name)
    #child_model_name = model["child"]
    child_model_names = model["children"]
    model_hierarchies = []
    properties_schema = []
    # file name -> stamping_press_properties.json for the model: Stamping Press
    properties_schema_file_name = '_'.join(model_name.lower().split())+"_properties.json"
    properties_schema_file_path = f'{schema_dir}/{properties_schema_file_name}'
    # Load schema if existing
    if os.path.exists(properties_schema_file_path):
        with open(properties_schema_file_path, 'r') as file:
            properties_schema = json.load(file)
    # Prepare model hierarchy
    if child_model_names is not None:
        for child_model_name in child_model_names:
            child_model_id = get_model_id_by_name(child_model_name)
            model_hierarchies.append({'name':child_model_name,'childAssetModelId':child_model_id})
    # Update model
    client.update_asset_model(
        assetModelId=model_id,
        assetModelName=model_name,
        assetModelProperties=properties_schema,
        assetModelHierarchies=model_hierarchies
    )

def get_asset_model_status(asset_model_id: str) -> str:
    response = client.describe_asset_model(
        assetModelId=asset_model_id
    )
    return response["assetModelStatus"]["state"]

def create_asset_models(asset_models: list[dict]) -> None:
    f = open(f'{tmp_dir}/asset_models.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(['asset_model_name', 'asset_model_id'])
    for model in asset_models:
        model_name = model["name"]
        asset_model_id = create_asset_model(model)
        # Wait for asset to become ACTIVE
        while True:
            model_status = get_asset_model_status(asset_model_id)
            if model_status == "ACTIVE":
                print(f"\t\tstatus: {model_status}")
                break
            time.sleep(1)
        # Store the asset model id for reference
        writer.writerow([model_name, asset_model_id])
    f.close()

def get_asset_model_hierarchies(model_id: str) -> list[dict]:
    response = client.describe_asset_model(
    assetModelId=model_id,
    excludeProperties=True
    )
    return response["assetModelHierarchies"]

def update_asset_models(asset_models: list[dict]) -> None:
    f = open(f'{tmp_dir}/hierarchies.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(['asset_model_name', 'child_asset_model_id', 'hierarchy_id'])
    for model in asset_models:
        model_name = model["name"]
        model_id = get_model_id_by_name(model_name)
        # Update model with hierarchy
        update_asset_model(model)
        # Wait for asset to become ACTIVE
        while True:
            model_status = get_asset_model_status(model_id)
            if model_status == "ACTIVE": 
                # Get hierarchies
                hierarchies = get_asset_model_hierarchies(model_id)
                for hierarchy in hierarchies:
                    # Store hierarchy ids for reference
                    writer.writerow([model_name, hierarchy["childAssetModelId"], hierarchy["id"]])
                break
            time.sleep(1)
    f.close()

def create_assets(assets: list[dict]) -> None:
    f = open(f'{tmp_dir}/assets.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(['asset_name', 'asset_id'])
    for asset in assets:
        asset_name = asset["name"]
        asset_id = create_asset(asset)
        # Wait for asset to become ACTIVE
        while True:
            asset_status = get_asset_status(asset_id)
            if asset_status == "ACTIVE":
                print(f"\t\tstatus: {asset_status}")
                break
            time.sleep(1)
        # Store the asset model id for reference
        writer.writerow([asset_name, asset_id])
    f.close()

def create_asset(asset: dict) -> str:
    asset_name = asset["name"]
    model_name = asset["model"]
    model_id = get_model_id_by_name(model_name)
    response = client.create_asset(
    assetName=asset_name,
    assetModelId=model_id,
    )
    asset_id = response["assetId"]
    print(f"\tCreated name: {asset_name}, id: {asset_id}")
    return asset_id

def get_asset_status(asset_id: str) -> str:
    response = client.describe_asset(
        assetId=asset_id
    )
    return response["assetStatus"]["state"]

def associate_assets(assets: list[dict]) -> None:
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
                client.associate_assets(assetId=asset_id, hierarchyId=hierarchy_id, childAssetId=child_asset_id)

def create_asset_hierarchy() -> None:
    print('Creating asset models..')
    create_asset_models(assets_models_config["asset_models"])
    print('All asset models created!')
    print('Updating asset models with hierarchy definitions..')
    update_asset_models(assets_models_config["asset_models"])
    print('All asset models updated!')
    print('Creating assets..')
    create_assets(assets_models_config["assets"])
    print('All assets created!')
    print('Updating assets with asset associations..')
    associate_assets(assets_models_config["assets"])
    print('All assets updated!')

def start() -> None:
    create_asset_hierarchy() 

if __name__ == "__main__":
    start()
    print('Script execution successfully completed!!')