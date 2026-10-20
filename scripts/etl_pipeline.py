import io

import boto3
import pandas as pd
from botocore.exceptions import BotoCoreError, ClientError
from sklearn.preprocessing import MinMaxScaler


import os

REGION_NAME = os.environ.get("AWS_REGION")
BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

SOURCE_KEY = "raw/operational_data.csv"
OUTPUT_KEY = "processed/etl_output.parquet"


def complete_etl_pipeline():
    s3_client = boto3.client(
        "s3",
        region_name=REGION_NAME
    )

    # STEP 1: EXTRACT
    print("\n=== STEP 1: EXTRACTION ===")

    try:
        response = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=SOURCE_KEY
        )

        csv_content = response["Body"].read()

        if not csv_content:
            raise ValueError("The source CSV file is empty.")

        df_raw = pd.read_csv(io.BytesIO(csv_content))

    except (ClientError, BotoCoreError) as error:
        print(f"S3 extraction failed: {error}")
        return
    except (ValueError, pd.errors.ParserError) as error:
        print(f"Source file processing failed: {error}")
        return

    required_columns = {
        "cliente",
        "edad",
        "monto_compras"
    }

    if not required_columns.issubset(df_raw.columns):
        print("Error: Required columns are missing from the CSV.")
        return

    print("Source loaded successfully from S3.")
    print(f"Dataset dimensions: {df_raw.shape}")
    print(df_raw)

    input("\nPress Enter to continue to transformation...")

    # STEP 2: TRANSFORM
    print("\n=== STEP 2: TRANSFORMATION ===")

    df_transformed = df_raw.copy()

    try:
        df_transformed["edad"] = pd.to_numeric(
            df_transformed["edad"],
            errors="raise"
        )

        df_transformed["monto_compras"] = pd.to_numeric(
            df_transformed["monto_compras"],
            errors="raise"
        )

        # Age categorization (binning)
        df_transformed["categoria_edad"] = pd.cut(
            df_transformed["edad"],
            bins=[0, 25, 50, 100],
            labels=["Young", "Adult", "Senior"],
            include_lowest=True
        )

        # Min-Max normalization
        scaler = MinMaxScaler()

        df_transformed["monto_normalizado"] = (
            scaler.fit_transform(
                df_transformed[["monto_compras"]]
            ).ravel()
        )

        # Feature engineering
        df_transformed["score_promocional"] = (
            df_transformed["monto_normalizado"] * 100
        )

    except (ValueError, TypeError) as error:
        print(f"Transformation failed: {error}")
        return

    if df_transformed.isnull().any().any():
        print("Warning: Missing values were detected.")

    print("Transformation completed successfully.")
    print("\nTransformed dataset:")
    print(df_transformed)

    print("\nColumn data types:")
    print(df_transformed.dtypes)

    input("\nPress Enter to continue to loading...")

    # STEP 3: LOAD
    print("\n=== STEP 3: LOADING ===")

    try:
        # Serialize Parquet in memory
        buffer = io.BytesIO()

        df_transformed.to_parquet(
            buffer,
            index=False,
            engine="pyarrow",
            compression="snappy"
        )

        parquet_content = buffer.getvalue()

        if not parquet_content:
            raise ValueError("The generated Parquet output is empty.")

        print(f"Generated Parquet size: {len(parquet_content)} bytes")

        # Upload Parquet to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=OUTPUT_KEY,
            Body=parquet_content,
            ContentType="application/vnd.apache.parquet"
        )

        # Verify the uploaded object
        metadata = s3_client.head_object(
            Bucket=BUCKET_NAME,
            Key=OUTPUT_KEY
        )

        print("\nUpload completed and verified.")
        print(f"S3 bucket: {BUCKET_NAME}")
        print(f"S3 object: {OUTPUT_KEY}")
        print(f"Uploaded size: {metadata['ContentLength']} bytes")

        # Save a local copy for inspection
        with open("etl_output.parquet", "wb") as output_file:
            output_file.write(parquet_content)

        print("Local copy created: etl_output.parquet")

    except (ClientError, BotoCoreError) as error:
        print(f"S3 loading or verification failed: {error}")
    except (ValueError, OSError) as error:
        print(f"Output generation failed: {error}")


if __name__ == "__main__":
    complete_etl_pipeline()
