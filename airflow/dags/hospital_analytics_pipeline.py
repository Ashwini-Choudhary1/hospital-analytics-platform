from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Default arguments for the DAG
default_args = {
    "owner": "analytics_team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

# Environment variables mapping Docker internal network endpoints
docker_env_vars = {
    "POSTGRES_HOST": "postgres",
    "POSTGRES_PORT": "5432",
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "postgres",
    "POSTGRES_DB": "hospital_analytics",
    "MINIO_ENDPOINT": "minio:9000",
    "MINIO_ACCESS_KEY": "minioadmin",
    "MINIO_SECRET_KEY": "minioadmin",
    "DBT_PROFILES_DIR": "/opt/airflow/dbt",
}

with DAG(
    dag_id="hospital_analytics_pipeline",
    default_args=default_args,
    description="End-to-End Medallion Architecture Pipeline (Raw -> Bronze -> Silver -> Gold -> Dashboards)",
    schedule_interval="@daily",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["medallion", "dbt", "healthcare", "mimic-iv"],
) as dag:

    # Task 1: Simulate daily clinical hospital records arrival
    generate_daily_data = BashOperator(
        task_id="generate_daily_data",
        bash_command="python3 /opt/airflow/scripts/generate_demo_data.py",
        cwd="/opt/airflow",
        env=docker_env_vars,
    )

    # Task 2: Ingest raw CSVs into MinIO S3 cloud storage & PostgreSQL Bronze layer
    ingest_bronze_layer = BashOperator(
        task_id="ingest_bronze_layer",
        bash_command="python3 /opt/airflow/scripts/load_bronze_layer.py",
        cwd="/opt/airflow",
        env=docker_env_vars,
    )

    # Task 3: Execute dbt transformations (build Silver staging views & Gold analytical marts)
    dbt_run_silver_gold = BashOperator(
        task_id="dbt_run_silver_gold",
        bash_command="export PATH=$PATH:/home/airflow/.local/bin && dbt run --profiles-dir /opt/airflow/dbt --project-dir /opt/airflow/dbt",
        cwd="/opt/airflow",
        env=docker_env_vars,
    )

    # Task 4: Execute dbt data quality tests (100% verification before dashboard refresh)
    dbt_test_quality = BashOperator(
        task_id="dbt_test_quality",
        bash_command="export PATH=$PATH:/home/airflow/.local/bin && dbt test --profiles-dir /opt/airflow/dbt --project-dir /opt/airflow/dbt",
        cwd="/opt/airflow",
        env=docker_env_vars,
    )

    # Define sequential dependency chain: Raw -> Bronze -> Silver/Gold -> Quality Assurance
    generate_daily_data >> ingest_bronze_layer >> dbt_run_silver_gold >> dbt_test_quality
