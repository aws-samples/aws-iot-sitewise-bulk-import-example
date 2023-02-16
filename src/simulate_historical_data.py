# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import random
import time
import json
import yaml
import csv
import os
import boto3

client = boto3.client('iotsitewise')
dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.dirname(dir))
config_dir = f'{root_dir}/config'
data_dir = f'{root_dir}/data'

# Load assets_models_configuration
with open(f'{config_dir}/assets_models.yml', 'r') as file:
    assets_models_config = yaml.safe_load(file)

# Load simulation configuration
with open(f'{config_dir}/data_simulation.yml', 'r') as file:
    data_simulation_config = yaml.safe_load(file)
date_range = data_simulation_config["date_range"]

def print_json(dict_obj: dict) -> None:
    print(json.dumps(dict_obj, indent=2, default=str))

def get_properties_list() -> list[dict]:
    properties = []
    res_models = client.list_asset_models(maxResults=100)
    models = res_models["assetModelSummaries"]
    for model in models:
        model_name = model["name"]
        model_id = model["id"]
        configured_model_names = [x["name"] for x in assets_models_config["asset_models"]]
        # Only process models from the config file
        if model_name in configured_model_names:
            # Get all assets for the model
            res_assets = client.list_assets(assetModelId=model_id,maxResults=100)
            assets = res_assets["assetSummaries"]
            # Get all properties for the model
            res_asset_model_properties = client.list_asset_model_properties(assetModelId=model_id,maxResults=100)
            asset_model_properties = res_asset_model_properties["assetModelPropertySummaries"]
            # Generate property list for each asset
            for property in asset_model_properties:
                for asset in assets:
                    properties.append({'property_id': property["id"], 'property_name': property["name"], 'asset_id': asset["id"], 'model_name': model_name})
    return properties

def generate_historical_data(properties: list[dict]) -> None:
    # open a csv file in the write mode
    f = open(f'{data_dir}/historical_data.csv', 'w', encoding='UTF8')
    # create the csv writer
    writer = csv.writer(f)
    # Configure data range
    from_epoch = int(time.mktime(time.strptime(date_range["from"], '%Y-%m-%d')))
    to_epoch = int(time.mktime(time.strptime(date_range["to"], '%Y-%m-%d')))
    # Use asset id and property id to identify a data point
    for property in properties:
        property_simulation_config = [x for x in data_simulation_config["properties"] if x["name"] == property["property_name"] and x["model"] == property["model_name"]][0]
        min = property_simulation_config["min"]
        max = property_simulation_config["max"]
        # generate data for every 1 hour
        for timestamp_seconds in range(from_epoch,to_epoch+86400,1*60*60):
            value = round(random.uniform(min, max),2)
            row = [property["asset_id"], property["property_id"], 'DOUBLE', timestamp_seconds, 0, 'GOOD', value]
            # write a row to the csv file
            writer.writerow(row)
    f.close()

def simulate_historical_data() -> None:
    print('Retrieving list of configured asset properties..')
    properties = get_properties_list()
    print(f'Retrieved asset properties: {len(properties)}')
    print(f'Generating simulated data between {date_range["from"]} and {date_range["to"]}..')
    generate_historical_data(properties)
    print(f'Data generation complete!')

def start() -> None:
    simulate_historical_data()

if __name__ == "__main__":
    start()
    print('Script execution successfully completed!!')