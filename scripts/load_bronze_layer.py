#!/usr/bin/env python3
"""
Hospital Analytics Platform - Bronze Layer Loader
Loads raw CSV data from the ./data/ directory into:
  1. Local Cloud Storage (MinIO S3 bucket: 'hospital-raw-data')
  2. Local Data Warehouse (PostgreSQL schema: 'bronze')
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from minio import Minio
from minio.error import S3Error

# Ensure current directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import generate_demo_data
except ImportError:
    generate_demo_data = None

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Environment configurations with fallback to Docker defaults
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5434")
POSTGRES_DB = os.getenv("POSTGRES_DB", "hospital_analytics")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET = "hospital-raw-data"

def check_and_generate_data():
    required_files = ["departments.csv", "patients.csv", "admissions.csv", "diagnoses.csv"]
    missing = [f for f in required_files if not os.path.exists(os.path.join(DATA_DIR, f))]
    
    if missing:
        print(f"ℹ️ Missing CSV data files: {missing}. Generating synthetic healthcare data now...")
        if generate_demo_data:
            generate_demo_data.main()
        else:
            print("❌ Error: generate_demo_data module not found!")
            sys.exit(1)

def load_to_minio():
    print(f"📦 Attempting upload to MinIO S3 ({MINIO_ENDPOINT})...")
    try:
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        
        # Check / create bucket
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)
            print(f"✅ Created MinIO bucket '{MINIO_BUCKET}'")
            
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".csv"):
                file_path = os.path.join(DATA_DIR, filename)
                object_name = f"raw/{filename}"
                client.fput_object(MINIO_BUCKET, object_name, file_path)
                print(f"  ☁️ Uploaded {filename} -> s3://{MINIO_BUCKET}/{object_name}")
        print("🎉 Successfully uploaded all raw files to MinIO Cloud Data Lake!")
    except Exception as e:
        print(f"⚠️ Notice: MinIO upload skipped ({e}). Ensure MinIO Docker container is running if you want S3 storage simulation.")

def load_to_postgres():
    print(f"🐘 Connecting to PostgreSQL ({POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB})...")
    db_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(db_url)
    
    with engine.begin() as conn:
        # Ensure bronze schema exists
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS bronze;"))
        
    for filename in ["departments.csv", "patients.csv", "admissions.csv", "diagnoses.csv"]:
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(file_path):
            table_name = filename.replace(".csv", "")
            print(f"  📊 Ingesting {filename} into PostgreSQL [bronze.{table_name}]...")
            df = pd.read_csv(file_path)
            
            # Truncate existing table if it exists so dependent Silver views don't break
            try:
                with engine.begin() as conn:
                    conn.execute(text(f"TRUNCATE TABLE bronze.{table_name} CASCADE;"))
            except Exception as e:
                print(f"    ⚠️ Notice: Could not truncate bronze.{table_name} ({e})")
            
            # Load into Postgres bronze schema
            df.to_sql(
                name=table_name,
                con=engine,
                schema="bronze",
                if_exists="append",
                index=False
            )
            print(f"    ✅ Ingested {len(df)} records into bronze.{table_name}")
            
    print("🎉 Successfully loaded all datasets into PostgreSQL Bronze Medallion Layer!")

def main():
    print("🏥 Starting Bronze Layer Data Ingestion...")
    check_and_generate_data()
    load_to_minio()
    load_to_postgres()
    print("✨ Bronze Layer Data Ingestion Completed!")

if __name__ == "__main__":
    main()
