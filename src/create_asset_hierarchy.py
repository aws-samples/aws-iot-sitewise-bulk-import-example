import time
import json
import yaml
import os
import boto3

client = boto3.client('iotsitewise')
dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.dirname(dir))
config_dir = f'{root_dir}/config'
schema_dir = f'{root_dir}/schema'

# Load assets_models_configuration
with open(f'{config_dir}/assets_models.yml', 'r') as file:
    assets_models_config = yaml.safe_load(file)

def print_json(dict_obj: dict) -> None:
    print(json.dumps(dict_obj, indent=2, default=str))

def create_asset_model(model: dict) -> str:
    model_name = model["name"]
    properties_schema = []
    # file name -> stamping_press_properties.json for the model: Stamping Press
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
    child_model_name = model["child"]
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
    if child_model_name: 
        child_model_id =  [model["model_id"] for model in assets_models_config["asset_models"] if model["name"] == child_model_name][0]
        model_hierarchies.append({'name':child_model_name,'childAssetModelId':child_model_id})
    # Update model
    response = client.update_asset_model(
        assetModelId=model["model_id"],
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
        # Add asset model id to assets_models_config
        for idx, model in enumerate(assets_models_config["asset_models"]):
            if model["name"] == model_name: assets_models_config["asset_models"][idx]["model_id"] = asset_model_id

def get_asset_model_hierarchies(model_id: str) -> list[dict]:
    response = client.describe_asset_model(
    assetModelId=model_id,
    excludeProperties=True
    )
    return response["assetModelHierarchies"]

def update_asset_models(asset_models: list[dict]) -> None:
    for model in asset_models:
        model_name = model["name"]
        model_id = model["model_id"]
        # Update model with hierarchy
        update_asset_model(model)
        # Wait for asset to become ACTIVE
        while True:
            model_status = get_asset_model_status(model_id)
            if model_status == "ACTIVE": 
                # Get hierarchies
                hierarchies = get_asset_model_hierarchies(model_id)
                if len(hierarchies) > 0:
                    # Add first hierarchy id to assets_models_config
                    for idx, x in enumerate(assets_models_config["asset_models"]):
                        if x["name"] == model_name: assets_models_config["asset_models"][idx]["hierarchy_id"] = hierarchies[0]["id"]
                break
            time.sleep(1)

def create_assets(assets: list[dict]) -> None:
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
        # Add asset id to assets_models_config
        for idx, asset in enumerate(assets_models_config["assets"]):
            if asset["name"] == asset_name: assets_models_config["assets"][idx]["asset_id"] = asset_id

def create_asset(asset: dict) -> str:
    asset_name = asset["name"]
    model_name = asset["model"]
    model_id = [model["model_id"] for model in assets_models_config["asset_models"] if model["name"] == model_name][0]
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
        asset_id = asset["asset_id"]
        model_name = asset["model"]
        associated_assets = asset["associated_assets"]
        # Create associations
        if associated_assets is not None:
            for child_asset_name in associated_assets:
                hierarchy_id = [model["hierarchy_id"] for model in assets_models_config["asset_models"] if model["name"] == model_name][0]
                child_asset_id = [asset["asset_id"] for asset in assets_models_config["assets"] if asset["name"] == child_asset_name][0]
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