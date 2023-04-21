# AWS IoT SiteWise Bulk Import Example

## About this Repo
This repo provides code samples to test the IoT SiteWise BulkImportJob API. Using this repo, you can easily create a sample asset hiearchy for an automobile manufacturer, simulate historical data for a selected period of time, and then import the data into AWS IoT SiteWise.

## Pre-requisities
1. An active AWS account
2. Supported region for AWS IoT SiteWise
3. Active cold tier storage (*Settings* -> *Storage*)
   - Map `S3 bucket location` to a temporary S3 bucket which can be deleted later
4. IAM user with administrator access to Amazon S3 and AWS IoT SiteWise

## How to use
### 1) Configure
Review and update the configuration in the following files, under the `/config` and `/schema` directories.

`assets_models.yml` - asset models, assets and hierarchy details

`data_simulation.yml` - data and date range setting for each configured property

`bulk_import.yml` - job and history details

`stamping_press_properties.json` - model properties schema for IoT SiteWise

### 2) Create a sample asset hierarchy

Run `create_asset_hierarchy.py` to automatically create asset models, hierarchy definitions, assets, asset associations

Sample output for asset model creation:

    Creating asset models..
        Created name: Sample_Enterprise, id: 27f9afaf-46ec-4c0a-9fe9-d0b97bef4a9b
                status: ACTIVE
        Created name: Sample_Site, id: c7921f03-1692-49b5-937f-2264bc6cc029
                status: ACTIVE
        Created name: Sample_Area, id: 00baeec4-d3fd-4a5d-ba2e-f9b062311a34
                status: ACTIVE
        Created name: Sample_Production Line, id: d1adbde3-f681-4bee-b654-60cdeb73629c
                status: ACTIVE
        Created name: Sample_Stamping Press, id: d48436a5-1114-4f4b-a3ad-7567b65a3d9d
                status: ACTIVE
    All asset models created!

Sample output for hierarchy definitions:

    Updating asset models with hierarchy definitions..
    All asset models updated!

Sample output for asset creation:

     Creating assets..
        Created name: AnyCompany_Motor, id: 33bfa3c1-2e62-4791-a502-0cca2f32af75
                status: ACTIVE
        Created name: Sample_Arlington, id: 22938200-731b-456a-85ce-d22b9c8afa1d
                status: ACTIVE
        Created name: Sample_Chicago, id: b733d9e7-7b13-46fe-98f7-7a8f25378a1c
                status: ACTIVE
        Created name: Sample_Georgetown, id: fe02d71b-3bbc-427a-962c-25c749181e46
                status: ACTIVE
        Created name: Sample_Indianapolis, id: 4997f9da-805e-451d-8b6a-2a6457c34513
                status: ACTIVE
        Created name: Sample_Stamping, id: 52c3ce58-7b13-42e8-b903-f024436db34e
                status: ACTIVE
        Created name: Sample_Welding, id: b83d70b5-878d-4151-9b35-2a48a2b66bc4
                status: ACTIVE
        Created name: Sample_Painting, id: ee9b7f6b-097e-4ee5-a6da-abaf95b5f623
                status: ACTIVE
        Created name: Sample_Powertrain, id: 24ab8dc9-6c65-459e-a156-f4883af2f192
                status: ACTIVE
        Created name: Sample_Line 1, id: a2456a4e-c201-465b-8188-38417c36dc94
                status: ACTIVE
        Created name: Sample_Line 2, id: ad9d55bf-d07a-439e-84a2-9dd0d72d82c5
                status: ACTIVE
        Created name: Sample_Stamping Press A, id: eb4303b5-d587-475d-8898-46dc2be19975
                status: ACTIVE
        Created name: Sample_Stamping Press B, id: 34ff64ab-6727-4a79-8845-73187db3a583
                status: ACTIVE
        Created name: Sample_Stamping Press C, id: c73e18c6-d2d2-4d93-ba24-3472988f8676
                status: ACTIVE
        Created name: Sample_Stamping Press D, id: 1f61b123-8a0d-4846-8ab1-33b090865649
                status: ACTIVE
    All assets created!

Sample output for asset associations:

    Updating assets with asset associations..
    All assets updated!


### 3) Simulate historical data

Run `simulate_historical_data.py` to generate simulated historical data for the time period configured in `data_simulation.yml`. If the total rows exceed `rows_per_job` (as configured in `bulk_import.yml`), multiple files are created to support parallel processing while importing data into AWS IoT SiteWise.

Sample output:

    Generating simulated data between 2022-11-01 and 2022-12-31..
        historical_data_1.csv file created
        historical_data_2.csv file created
        historical_data_3.csv file created
        historical_data_4.csv file created
    Data generation complete!

### 4) Upload historical data to S3

Run `upload_to_s3.py` to create the S3 bucket configured in `bulk_import.yml` and upload the historical data. Ensure the S3 buckets provided in `bulk_import.yml` are already created.

Sample output.

    Uploading historical data files into Amazon S3..
    Successfully uploaded historical data to S3!

### 5) Create a job to import data into IoT SiteWise

> **Note**
> Ensure that the cold tier storage is activated for AWS IoT SiteWise.

Run `create_bulk_import_job.py` to import the historical data from the S3 bucket into IoT SiteWise as per the configuration in `bulk_import.yml`

Sample output.

    Total S3 objects: ['data/historical_data_1.csv', 'data/historical_data_2.csv', 'data/historical_data_3.csv', 'data/historical_data_4.csv']
    Number of bulk import jobs to create: 4
        Created job: 7f8f071e-5bb4-44b4-b04e-8adf01095b2f for importing data from data/historical_data_1.csv S3 object
        Created job: 34f6fb60-384e-4a49-a793-d3a0824d451a for importing data from data/historical_data_2.csv S3 object
        Created job: 6984318e-473e-4b4f-8b53-ab920e876728 for importing data from data/historical_data_3.csv S3 object
        Created job: b3672808-0ecd-4c81-8759-45c418b7f72d for importing data from data/historical_data_4.csv S3 object
    Checking job status every 5 secs until completion..
        Job id: 7f8f071e-5bb4-44b4-b04e-8adf01095b2f, status: COMPLETED_WITH_FAILURES
        Job id: b3672808-0ecd-4c81-8759-45c418b7f72d, status: COMPLETED
        Job id: 34f6fb60-384e-4a49-a793-d3a0824d451a, status: COMPLETED
        Job id: 6984318e-473e-4b4f-8b53-ab920e876728, status: COMPLETED_WITH_FAILURES
    Script execution successfully completed!!

## Clean up
Run `clean_up.py` to remove the following resources created for the sample
1. Asset associations
2. Assets
3. Hierarchy definitions from asset models
4. Asset models
        
Navigate to [Amazon S3](https://s3.console.aws.amazon.com/s3/home) and perform the following
1.	Delete the temporary S3 bucket configured for `S3 bucket location` under the **Storage** section of AWS IoT SiteWise
2.	Delete the data and error buckets configured in the `/config/bulk_import.yml`
