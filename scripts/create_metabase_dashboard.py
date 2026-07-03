#!/usr/bin/env python3
"""
Hospital Analytics Platform - Metabase Automated Dashboard Builder
Connects to the Metabase REST API (http://localhost:3000) to:
  1. Authenticate with admin credentials
  2. Detect or register the PostgreSQL 'Hospital Analytics Warehouse' database
  3. Create an Executive KPI Collection
  4. Build 6 Native SQL Cards from Gold Medallion tables
  5. Assemble and arrange them onto the Executive Dashboard
"""

import os
import sys
import json
import argparse
import getpass
import urllib.request
import urllib.error
import urllib.parse

DEFAULT_METABASE_URL = "http://localhost:3000"

# SQL Queries for Dashboard Cards
QUERIES = [
    {
        "name": "Total Patient Admissions",
        "description": "Total volume of clinical admissions processed in the warehouse.",
        "display": "scalar",
        "sql": "SELECT COUNT(*) AS total_admissions FROM gold.fct_admissions;",
        "viz_settings": {},
        "layout": {"col": 0, "row": 0, "sizeX": 6, "sizeY": 3}
    },
    {
        "name": "Average Length of Stay (Days)",
        "description": "Average duration (in days) patients spend hospitalized across departments.",
        "display": "scalar",
        "sql": "SELECT ROUND(AVG(length_of_stay_days), 1) AS avg_los_days FROM gold.fct_admissions;",
        "viz_settings": {},
        "layout": {"col": 6, "row": 0, "sizeX": 6, "sizeY": 3}
    },
    {
        "name": "Overall 30-Day Readmission Rate",
        "description": "Hospital-wide percentage of patients readmitted within 30 days of discharge.",
        "display": "scalar",
        "sql": "SELECT ROUND(AVG(readmission_rate_pct), 2) AS overall_readmission_rate_pct FROM gold.mart_readmission_rates;",
        "viz_settings": {},
        "layout": {"col": 12, "row": 0, "sizeX": 6, "sizeY": 3}
    },
    {
        "name": "Department Workload & Cost Analysis",
        "description": "Total admissions, average stay duration, and total billing cost per department.",
        "display": "bar",
        "sql": "SELECT department_name, total_admissions, avg_length_of_stay_days, ROUND(total_hospital_cost, 2) AS total_hospital_cost FROM gold.mart_department_workload ORDER BY total_admissions DESC;",
        "viz_settings": {
            "graph.dimensions": ["department_name"],
            "graph.metrics": ["total_admissions"],
            "graph.colors": ["#509EE3"]
        },
        "layout": {"col": 0, "row": 3, "sizeX": 9, "sizeY": 7}
    },
    {
        "name": "Top 10 Clinical Diagnoses",
        "description": "Most frequent primary ICD-10 clinical diagnoses treated across the hospital.",
        "display": "row",
        "sql": "SELECT diagnosis_description, total_cases, ROUND(avg_cost_per_case, 2) AS avg_cost_per_case FROM gold.mart_clinical_diagnoses WHERE diagnosis_description != 'No Primary Diagnosis Recorded' ORDER BY total_cases DESC LIMIT 10;",
        "viz_settings": {
            "graph.dimensions": ["diagnosis_description"],
            "graph.metrics": ["total_cases"],
            "graph.colors": ["#88BF4D"]
        },
        "layout": {"col": 9, "row": 3, "sizeX": 9, "sizeY": 7}
    },
    {
        "name": "30-Day Readmission Risk Breakdown",
        "description": "Comparative clinical risk analysis of readmission rates by department.",
        "display": "table",
        "sql": "SELECT department_name, total_discharges, readmitted_30_days_count, readmission_rate_pct, avg_los_days, high_risk_readmissions FROM gold.mart_readmission_rates ORDER BY readmission_rate_pct DESC;",
        "viz_settings": {},
        "layout": {"col": 0, "row": 10, "sizeX": 18, "sizeY": 7}
    }
]


class MetabaseAPI:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session_id = None

    def _request(self, endpoint, method="GET", data=None):
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        headers = {"Content-Type": "application/json"}
        if self.session_id:
            headers["X-Metabase-Session"] = self.session_id

        payload = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=payload, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                res_data = response.read().decode("utf-8")
                return json.loads(res_data) if res_data else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise Exception(f"HTTP {e.code}: {err_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Connection Error: {e.reason}")

    def login(self, username, password):
        print(f"🔐 Authenticating with Metabase at {self.base_url}...")
        res = self._request("session", method="POST", data={"username": username, "password": password})
        self.session_id = res.get("id")
        if not self.session_id:
            raise Exception("Failed to acquire session token from Metabase.")
        print("  ✅ Successfully logged in!")

    def get_or_create_database(self):
        print("🔍 Searching for PostgreSQL Data Warehouse connection...")
        dbs = self._request("database").get("data", [])
        for db in dbs:
            if db.get("name") == "Hospital Analytics Warehouse" or db.get("details", {}).get("dbname") == "hospital_analytics":
                print(f"  ✅ Found existing database connection [ID: {db['id']}]")
                return db["id"]

        print("  ➕ Database not found. Registering new PostgreSQL connection...")
        payload = {
            "engine": "postgres",
            "name": "Hospital Analytics Warehouse",
            "details": {
                "host": "postgres",
                "port": 5432,
                "dbname": "hospital_analytics",
                "user": "postgres",
                "password": "postgres",
                "schema-filters-type": "all",
                "ssl": False
            }
        }
        res = self._request("database", method="POST", data=payload)
        db_id = res["id"]
        print(f"  ✅ Successfully registered database [ID: {db_id}]")
        return db_id

    def get_or_create_collection(self):
        print("📁 Setting up Executive BI Collection...")
        collections = self._request("collection")
        for col in collections:
            if col.get("name") == "🏥 Hospital Analytics Executive KPIs":
                print(f"  ✅ Found existing collection [ID: {col['id']}]")
                return col["id"]

        payload = {
            "name": "🏥 Hospital Analytics Executive KPIs",
            "color": "#509EE3",
            "description": "Executive KPI cards and analytical charts from Gold medallion tables."
        }
        res = self._request("collection", method="POST", data=payload)
        col_id = res["id"]
        print(f"  ✅ Created new collection [ID: {col_id}]")
        return col_id

    def create_card(self, db_id, collection_id, query_info):
        name = query_info["name"]
        print(f"  📊 Creating card: '{name}'...")
        payload = {
            "name": name,
            "description": query_info["description"],
            "collection_id": collection_id,
            "dataset_query": {
                "database": db_id,
                "type": "native",
                "native": {"query": query_info["sql"]}
            },
            "display": query_info["display"],
            "visualization_settings": query_info["viz_settings"]
        }
        res = self._request("card", method="POST", data=payload)
        return res["id"]

    def get_or_create_dashboard(self, collection_id):
        print("📈 Setting up Executive Dashboard...")
        dashboards = self._request("dashboard")
        for dash in dashboards:
            if dash.get("name") == "🏥 Hospital Operations & Clinical Executive Dashboard":
                print(f"  ✅ Found existing dashboard [ID: {dash['id']}]. Reusing...")
                return dash["id"]

        payload = {
            "name": "🏥 Hospital Operations & Clinical Executive Dashboard",
            "description": "Real-time clinical executive KPIs and department workload from Gold Medallion mart tables.",
            "collection_id": collection_id
        }
        res = self._request("dashboard", method="POST", data=payload)
        dash_id = res["id"]
        print(f"  ✅ Created new dashboard [ID: {dash_id}]")
        return dash_id

    def add_card_to_dashboard(self, dashboard_id, card_id, layout):
        payload = {
            "cardId": card_id,
            "row": layout["row"],
            "col": layout["col"],
            "sizeX": layout["sizeX"],
            "sizeY": layout["sizeY"],
            "series": [],
            "visualization_settings": {}
        }
        try:
            self._request(f"dashboard/{dashboard_id}/cards", method="POST", data=payload)
        except Exception as e:
            # If card already added or overlapping, ignore or log
            pass


def main():
    parser = argparse.ArgumentParser(description="Automate Metabase Executive Dashboard Setup")
    parser.add_argument("--url", default=os.getenv("METABASE_URL", DEFAULT_METABASE_URL), help="Metabase Base URL")
    parser.add_argument("--email", default=os.getenv("METABASE_EMAIL"), help="Metabase Admin Email")
    parser.add_argument("--password", default=os.getenv("METABASE_PASSWORD"), help="Metabase Admin Password")
    args = parser.parse_args()

    print("🏥 Starting Automated Metabase Dashboard Setup...")
    email = args.email
    password = args.password

    if not email:
        email = input("📧 Enter Metabase Admin Email: ").strip()
    if not password:
        password = getpass.getpass("🔑 Enter Metabase Admin Password: ").strip()

    if not email or not password:
        print("❌ Error: Email and password are required to authenticate with Metabase.")
        sys.exit(1)

    try:
        api = MetabaseAPI(args.url)
        api.login(email, password)
        db_id = api.get_or_create_database()
        col_id = api.get_or_create_collection()
        dash_id = api.get_or_create_dashboard(col_id)

        print("🏗️ Generating native SQL cards and pinning to dashboard...")
        for q in QUERIES:
            card_id = api.create_card(db_id, col_id, q)
            api.add_card_to_dashboard(dash_id, card_id, q["layout"])

        print("\n🎉 Successfully built Hospital Operations Executive Dashboard!")
        print(f"👉 View your dashboard live at: {args.url}/dashboard/{dash_id}")

    except Exception as e:
        print(f"\n❌ Setup Failed: {e}")
        print("💡 Ensure Metabase is running at http://localhost:3000 and your admin credentials are correct.")
        sys.exit(1)


if __name__ == "__main__":
    main()
