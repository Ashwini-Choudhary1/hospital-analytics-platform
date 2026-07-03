-- ====================================================================
-- Hospital Analytics Platform - Database Initialization
-- ====================================================================
-- This script runs automatically when the PostgreSQL container starts
-- for the first time. It creates databases for Airflow metadata and
-- Metabase application data alongside the main hospital_analytics DB.
-- ====================================================================

-- Create Airflow metadata database
CREATE DATABASE airflow;

-- Create Metabase application database (optional, for persistent BI settings)
CREATE DATABASE metabase;

-- Connect to hospital_analytics and create initial schemas
\c hospital_analytics;

-- Create Medallion Architecture schemas
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE hospital_analytics TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA bronze TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA silver TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA gold TO postgres;
