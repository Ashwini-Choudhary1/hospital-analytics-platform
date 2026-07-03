# 🏥 Hospital Analytics Platform

An end-to-end healthcare analytics platform that transforms raw hospital data into business-ready insights using modern data analytics tools.

This project simulates a real-world analytics environment where hospital data is ingested, transformed, modeled, and visualized to support operational and clinical decision-making.

> **Project Status:** 🚧 In Development

---

# 📖 Project Overview

Healthcare organizations generate large volumes of data from patient admissions, diagnoses, transfers, laboratory results, and clinical events. Turning this data into meaningful insights requires more than writing SQL queries—it requires a complete analytics workflow.

This project demonstrates how to build that workflow from end to end using PostgreSQL, Python, dbt, Airflow, and Metabase.

The platform is designed to answer questions such as:

* What is the average patient length of stay?
* What are the hospital readmission rates?
* Which diagnoses are most common?
* How has patient admission volume changed over time?
* Which departments experience the highest patient load?
* What operational KPIs should hospital management monitor?

---

# 🎯 Project Goals

* Build an end-to-end analytics platform from raw data to dashboards.
* Practice advanced SQL using realistic healthcare data.
* Design a modern analytical data warehouse.
* Automate data ingestion and transformation.
* Create interactive dashboards for business users.
* Apply data modeling best practices.
* Demonstrate a production-style analytics workflow suitable for a professional portfolio.

---

# 🛠️ Tech Stack

| Category               | Technology              |
| ---------------------- | ----------------------- |
| Programming            | Python                  |
| Database               | PostgreSQL              |
| SQL Transformation     | dbt Core                |
| Workflow Orchestration | Apache Airflow          |
| Business Intelligence  | Metabase                |
| Storage                | MinIO                   |
| Containerization       | Docker & Docker Compose |
| Version Control        | Git & GitHub            |
| Development            | VS Code                 |

---

# 🏗️ Planned Architecture

```text
                 Data Sources
         ┌─────────────────────────┐
         │ MIMIC-IV Dataset        │
         │ CSV Files               │
         │ Public APIs (Optional)  │
         └─────────────┬───────────┘
                       │
                  Python ETL
                       │
                    Airflow
                       │
                 PostgreSQL
                       │
                      dbt
      Bronze → Silver → Gold Models
                       │
                   Metabase
                       │
             Analytics Dashboards
```

---

# 📂 Project Structure

```text
hospital-analytics-platform/
├── airflow/
├── data/
├── dbt/
├── docs/
├── metabase/
├── minio/
├── python/
├── scripts/
├── sql/
├── tests/
├── README.md
├── docker-compose.yml
└── requirements.txt
```

---

# 📊 Planned Dashboards

### Executive Dashboard

* Total Admissions
* Average Length of Stay
* Readmission Rate
* ICU Utilization
* Patient Demographics

### Operations Dashboard

* Daily Admissions
* Bed Occupancy
* Department Workload
* Waiting Times
* Patient Flow

### Clinical Dashboard

* Common Diagnoses
* Patient Outcomes
* Mortality Trends
* Readmission Analysis

---

# 🗂️ Data Model

The project follows a Medallion Architecture.

### Bronze

Raw data loaded without transformation.

### Silver

Cleaned and standardized datasets ready for analysis.

### Gold

Business-ready fact and dimension tables powering dashboards.

---

# 🚀 Development Roadmap

* [x] Repository Initialization
* [x] Project Structure
* [ ] Docker Environment
* [ ] PostgreSQL Setup
* [ ] Load MIMIC-IV Dataset
* [ ] Bronze Layer
* [ ] Silver Layer
* [ ] Gold Layer
* [ ] Advanced SQL Analytics
* [ ] dbt Models
* [ ] Airflow Pipelines
* [ ] Metabase Dashboards
* [ ] Data Quality Tests
* [ ] Documentation
* [ ] CI/CD

---

# 📚 Dataset

This project uses the **MIMIC-IV Demo** dataset during development and is designed to scale to the full MIMIC-IV dataset.

---

# 🎓 Learning Objectives

This project demonstrates skills in:

* Advanced SQL
* Data Modeling
* Data Warehousing
* ETL Development
* Analytics Engineering
* Dashboard Development
* Workflow Automation
* Healthcare Analytics
* Git & GitHub
* Docker

---

# 📌 Disclaimer

This project is intended for educational and portfolio purposes. It uses publicly available healthcare datasets and does not contain real patient-identifiable information.
