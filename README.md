# Practice 5: Automated ETL Pipeline to AWS S3

## Description

This project implements an ETL pipeline using Python, pandas, scikit-learn, and Boto3. It extracts operational data from an AWS S3 bucket, applies feature engineering and MinMaxScaler normalization, and stores the transformed dataset in compressed Parquet format.

## Features

- CSV ingestion from Amazon S3.
- Age categorization using pandas.
- Purchase amount normalization with MinMaxScaler.
- Promotional score calculation.
- Processed data upload and verification in Amazon S3.

## Requirements

- Python 3.8+
- pandas
- scikit-learn
- Boto3
- PyArrow
- AWS Academy account with active credentials

## Installation

1. Clone this repository and navigate to the project directory.
2. Create and activate a Python virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### 1. AWS Credentials

Ensure your AWS Academy credentials are active and configured through the AWS CLI or environment variables.

For environment variable configuration, use:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"
```

Temporary AWS Academy credentials must be renewed when they expire. Never commit credentials to the repository.

### 2. Environment Variables

Set the AWS Region and S3 bucket name:

```bash
export AWS_REGION="us-east-1"
export S3_BUCKET_NAME="webserverpractices-bucket-practice5"
```

The source CSV must be available at `raw/operational_data.csv` in the S3 bucket.

## Execution

Run the ETL pipeline from the project root directory:

```bash
python scripts/etl_pipeline.py
```

The program pauses after extraction and transformation. Press Enter to continue through each stage.

## Output

The pipeline reads `raw/operational_data.csv` and uploads the transformed dataset to:

```text
processed/etl_output.parquet
```

The output contains the original columns, the age category, the normalized purchase amount, and the promotional score. The Parquet file uses Snappy compression and is generated in memory before being uploaded to S3.

A local copy named `etl_output.parquet` is also created for inspection.
