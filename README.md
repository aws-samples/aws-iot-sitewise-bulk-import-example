# AWS IoT SiteWise Bulk Import Example

## About this Repo
This repo provides code samples to test the IoT SiteWise BulkImportJob API. Using this repo, you can easily create a sample asset hiearchy for an automobile manufacturer, simulate historical data for a selected period of time, and then import the data into AWS IoT SiteWise.

## How to use
### 1) Configure
Review and update the configuration in the following files as needed, under the `/config` and `/schema` directories.

`assets_models.yml` - asset models, assets and hierarchy details

`data_simulation.yml` - data and date range setting for each configured property

`bulk_import.yml` - job and history details

`stamping_press_properties.json` - model properties schema for IoT SiteWise

#### Important
- Ensure the necessary Amazon S3 buckets are available before proceeding
- Avoid using existing asset model and asset names in your IoT SiteWise environment

### 2) Create a sample asset hierarchy

Run `create_asset_hierarchy.py` to automatically create asset models, hierarchy definitions, assets, asset associations

Sample output for asset model creation:

    Creating asset models..
        Created name: Enterprise, id: 604bf134-5f99-4532-96cf-a2da531f5d6a
                status: ACTIVE
        Created name: Site, id: 57df9fb1-8e0d-40a2-9a0f-12a9f48f6622
                status: ACTIVE
        Created name: Area, id: f3782220-3100-4fd5-bd62-ba6162a8513a
                status: ACTIVE
        Created name: Production Line, id: bedc329d-6ffa-4931-9aa3-c59369014674
                status: ACTIVE
        Created name: Stamping Press, id: 5a1b42a3-5eaa-4e5c-8e08-4f1df7b85c0c
                status: ACTIVE
    All asset models created!

Sample output for hierarchy definitions:

    Updating asset models with hierarchy definitions..
    All asset models updated!

Sample output for asset creation:

    Creating assets..
        Created name: Octank Motor, id: 508d7b0a-5dca-4f11-aadc-8da47e689971
                status: ACTIVE
        Created name: Arlington, id: a4853fab-ac1b-4fd6-a9ab-070f108addf2
                status: ACTIVE
        Created name: Chicago, id: 65241b35-5eef-4512-b43b-0fb720c73a27
                status: ACTIVE
        Created name: Georgetown, id: 42be3ef5-814b-4504-837e-26ccfc2f5efe
                status: ACTIVE
        Created name: Indianapolis, id: 3d84a03b-690d-4cee-8699-a82012838498
                status: ACTIVE
        Created name: Stamping, id: 07ed3cdc-11c2-4b7f-8919-d8d4778c0bdd
                status: ACTIVE
        Created name: Welding, id: a05958a3-bd41-4dae-880b-8d8ee83bf271
                status: ACTIVE
        Created name: Painting, id: d796f2b5-95f3-45b7-8ab4-444cf743518e
                status: ACTIVE
        Created name: Powertrain, id: 66e48fb0-6bf9-4027-b61d-2a891a7c4d50
                status: ACTIVE
        Created name: Line 1, id: f62b5401-1e38-43c3-b156-16b2588e71ec
                status: ACTIVE
        Created name: Line 2, id: a14a1e24-7abe-4e3e-9960-210badeb4047
                status: ACTIVE
        Created name: Stamping Press A, id: 55254f01-4d9b-40b6-9347-635ffc6ec9c5
                status: ACTIVE
        Created name: Stamping Press B, id: ae9cb134-bbeb-412b-82fb-2a49a0e3b91f
                status: ACTIVE
        Created name: Stamping Press C, id: 0540d862-f8d7-4a3f-8710-e1b0f823f03e
                status: ACTIVE
        Created name: Stamping Press D, id: 17b306f4-77b2-47df-a0dd-22d7ca1de04c
                status: ACTIVE
    All assets created!

Sample output for asset associations:

    Updating assets with asset associations..
    All assets updated!


### 3) Simulate historical data

Run `simulate_historical_data.py` to generate simulated historical data for the time period configured in `data_simulation.yml`

Sample output:

    Retrieving list of configured asset properties..
    Retrieved asset properties: 8
    Generating simulated data between 2022-01-01 and 2022-12-31..
    Data generation complete!
   

### 4) Upload historical data to S3

Run `upload_to_s3.py` to upload the historical data into a S3 bucket configured in `bulk_import.yml`

Sample output.

    Successfully uploaded historical data to S3!

### 5) Create a job to import data into IoT SiteWise

Run `create_bulk_import_job.py` to import the historical data from the S3 bucket into IoT SiteWise as per the configuration in `bulk_import.yml`

Sample output.

    Created job: 8f466ae3-78d0-4f06-bf92-8cff70aee5c4
    Checking job status every 5 secs until done
    Job status: COMPLETED

## Clean up
Navigate to [AWS IoT SiteWise](https://aws.amazon.com/iotsitewise/home) and perform the following
1.	Choose **Assets** and pick an asset
2.	Remove all **Associated assets** from the asset, and then delete the asset
3.	Repeat the process for all the assets
4.	Choose **Models** and remove **Hierarchy definitions** from all the models
5.	Delete all models
6.	Choose **Portals** and delete the portal

        
Navigate to [Amazon S3](https://s3.console.aws.amazon.com/s3/home) and perform the following
1.	Delete the `S3 bucket location` configured under the **Storage** section of AWS IoT SiteWise
2.	Delete the data and error buckets configured in the `/config/bulk_import.yml` of Git repo
