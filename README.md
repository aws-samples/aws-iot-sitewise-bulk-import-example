# IoT SiteWise Bulk Import Example

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
            Created name: Octank Motor, id: 5dc7c166-922b-4c32-b5e8-7d15a38f4fa7
                    status: ACTIVE
            Created name: Arlington, id: c580e773-98ce-442d-ac84-c72fed607094
                    status: ACTIVE
            Created name: Stamping, id: 4f413e22-3557-47c8-9a90-339c33363900
                    status: ACTIVE
            Created name: Line 1, id: 548dedd4-0658-40a3-98d0-e7ff8afb3c6f
                    status: ACTIVE
            Created name: Stamping Press A, id: 73c3b608-7ec8-43e8-b8c2-dbc62d046e15
                    status: ACTIVE
    All assets created!

Sample output for asset associations:

    Updating assets with asset associations..
    All assets updated!


### 3) Simulate historical data

Run `simulate_historical_data.py` to generate simulated historical data for the time period configured in `data_simulation.yml`

Sample output:

    Retrieving list of configured asset properties..
    Retrieved asset properties: 2
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
