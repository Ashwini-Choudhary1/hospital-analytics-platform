#!/usr/bin/env python3
"""
Hospital Analytics Platform - Demo Healthcare Data Generator
Simulates a realistic subset of MIMIC-IV style clinical hospital data.
Generates CSV files in the data/ directory:
  - departments.csv
  - patients.csv
  - admissions.csv
  - diagnoses.csv
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

# Set random seeds for reproducible data generation
Faker.seed(42)
random.seed(42)
fake = Faker()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Generate Departments
def generate_departments():
    departments = [
        {"department_id": 1, "department_name": "Intensive Care Unit (ICU)", "bed_capacity": 30, "floor": 4},
        {"department_id": 2, "department_name": "Emergency Department", "bed_capacity": 50, "floor": 1},
        {"department_id": 3, "department_name": "Cardiology", "bed_capacity": 40, "floor": 3},
        {"department_id": 4, "department_name": "General Surgery", "bed_capacity": 45, "floor": 2},
        {"department_id": 5, "department_name": "General Medicine", "bed_capacity": 60, "floor": 2},
        {"department_id": 6, "department_name": "Oncology", "bed_capacity": 25, "floor": 5},
        {"department_id": 7, "department_name": "Pediatrics", "bed_capacity": 35, "floor": 3},
        {"department_id": 8, "department_name": "Neurology", "bed_capacity": 20, "floor": 4},
        {"department_id": 9, "department_name": "Orthopedics", "bed_capacity": 30, "floor": 2},
        {"department_id": 10, "department_name": "Maternity & Obstetrics", "bed_capacity": 40, "floor": 3},
    ]
    df = pd.DataFrame(departments)
    path = os.path.join(DATA_DIR, "departments.csv")
    df.to_csv(path, index=False)
    print(f"✅ Generated {len(df)} departments -> {path}")
    return df

# 2. Generate Patients
def generate_patients(num_patients=500):
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    insurance_types = ["Medicare", "Medicaid", "Private - BlueCross", "Private - Aetna", "Self-Pay", "UnitedHealth"]
    
    patients = []
    for i in range(1, num_patients + 1):
        gender = random.choice(["M", "F"])
        first_name = fake.first_name_male() if gender == "M" else fake.first_name_female()
        last_name = fake.last_name()
        birth_date = fake.date_of_birth(minimum_age=1, maximum_age=90)
        reg_date = fake.date_between(start_date="-3y", end_date="-1y")
        
        patients.append({
            "patient_id": i,
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "blood_type": random.choice(blood_types),
            "insurance_type": random.choice(insurance_types),
            "registration_date": reg_date.strftime("%Y-%m-%d")
        })
        
    df = pd.DataFrame(patients)
    path = os.path.join(DATA_DIR, "patients.csv")
    df.to_csv(path, index=False)
    print(f"✅ Generated {len(df)} patients -> {path}")
    return df

# 3. Generate Admissions (including 30-day readmissions)
def generate_admissions(patients_df, departments_df, num_admissions=1500):
    admission_types = ["EMERGENCY", "ELECTIVE", "URGENT", "OBSERVATION"]
    dispositions = ["HOME", "HOME HEALTH CARE", "SKILLED NURSING FACILITY", "REHABILITATION", "EXPIRED"]
    disposition_weights = [0.70, 0.12, 0.08, 0.06, 0.04]
    
    admissions = []
    adm_id = 1
    
    # Give some patients multiple admissions to simulate 30-day readmissions
    patient_ids = patients_df["patient_id"].tolist()
    
    for _ in range(num_admissions):
        p_id = random.choice(patient_ids)
        # Choose a random admission date in the last 2 years
        adm_date = fake.date_time_between(start_date="-2y", end_date="now")
        
        # Length of stay between 1 and 25 days (exponential decay for realism)
        los_days = max(1, int(random.expovariate(1/4)))
        dis_date = adm_date + timedelta(days=los_days, hours=random.randint(1, 12))
        
        # Don't exceed current time
        if dis_date > datetime.now():
            dis_date = datetime.now()
            
        dept_id = random.choice(departments_df["department_id"].tolist())
        adm_type = random.choice(admission_types)
        if dept_id in [1, 2]: # ICU / ER are mostly EMERGENCY
            adm_type = "EMERGENCY"
            
        disposition = random.choices(dispositions, weights=disposition_weights)[0]
        cost = round(random.uniform(1500.0, 45000.0) + (los_days * 1200.0), 2)
        
        admissions.append({
            "admission_id": adm_id,
            "patient_id": p_id,
            "admission_date": adm_date.strftime("%Y-%m-%d %H:%M:%S"),
            "discharge_date": dis_date.strftime("%Y-%m-%d %H:%M:%S"),
            "admission_type": adm_type,
            "department_id": dept_id,
            "discharge_disposition": disposition,
            "hospital_cost": cost
        })
        adm_id += 1
        
        # 18% chance of a 30-day readmission for the same patient
        if random.random() < 0.18 and disposition != "EXPIRED":
            readm_gap = random.randint(2, 28)
            readm_date = dis_date + timedelta(days=readm_gap)
            if readm_date < datetime.now():
                readm_los = max(1, int(random.expovariate(1/5)))
                readm_dis = readm_date + timedelta(days=readm_los)
                if readm_dis > datetime.now():
                    readm_dis = datetime.now()
                
                admissions.append({
                    "admission_id": adm_id,
                    "patient_id": p_id,
                    "admission_date": readm_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "discharge_date": readm_dis.strftime("%Y-%m-%d %H:%M:%S"),
                    "admission_type": "EMERGENCY",
                    "department_id": random.choice([1, 2, 3, 5]), # Urgent readmission departments
                    "discharge_disposition": random.choices(dispositions, weights=disposition_weights)[0],
                    "hospital_cost": round(random.uniform(3000.0, 35000.0) + (readm_los * 1400.0), 2)
                })
                adm_id += 1
                
    df = pd.DataFrame(admissions)
    # Sort by admission date
    df = df.sort_values("admission_date").reset_index(drop=True)
    df["admission_id"] = range(1, len(df) + 1)
    
    path = os.path.join(DATA_DIR, "admissions.csv")
    df.to_csv(path, index=False)
    print(f"✅ Generated {len(df)} admissions -> {path}")
    return df

# 4. Generate Diagnoses
def generate_diagnoses(admissions_df):
    icd10_catalog = [
        {"code": "I10", "desc": "Essential (primary) hypertension"},
        {"code": "E11", "desc": "Type 2 diabetes mellitus"},
        {"code": "J18", "desc": "Pneumonia, unspecified organism"},
        {"code": "I21", "desc": "Acute myocardial infarction"},
        {"code": "J44", "desc": "Chronic obstructive pulmonary disease"},
        {"code": "N18", "desc": "Chronic kidney disease"},
        {"code": "I50", "desc": "Heart failure"},
        {"code": "S72", "desc": "Fracture of femur"},
        {"code": "K80", "desc": "Cholelithiasis"},
        {"code": "A41", "desc": "Other sepsis"},
        {"code": "N39", "desc": "Urinary tract infection, site not specified"},
        {"code": "E78", "desc": "Disorders of lipoprotein metabolism and other lipidemias"},
        {"code": "F32", "desc": "Major depressive disorder, single episode"},
        {"code": "G30", "desc": "Alzheimer's disease"},
        {"code": "K21", "desc": "Gastro-esophageal reflux disease"},
    ]
    
    diagnoses = []
    diag_id = 1
    
    for adm_id in admissions_df["admission_id"]:
        # Each admission gets 1 primary diagnosis and 0 to 3 secondary diagnoses
        num_diags = random.randint(1, 4)
        selected_diags = random.sample(icd10_catalog, num_diags)
        
        for idx, item in enumerate(selected_diags):
            diagnoses.append({
                "diagnosis_id": diag_id,
                "admission_id": adm_id,
                "icd10_code": item["code"],
                "diagnosis_description": item["desc"],
                "is_primary": (idx == 0)
            })
            diag_id += 1
            
    df = pd.DataFrame(diagnoses)
    path = os.path.join(DATA_DIR, "diagnoses.csv")
    df.to_csv(path, index=False)
    print(f"✅ Generated {len(df)} diagnoses -> {path}")
    return df

def main():
    print("🏥 Starting Hospital Analytics Demo Data Generation...")
    depts_df = generate_departments()
    pts_df = generate_patients(num_patients=600)
    adms_df = generate_admissions(pts_df, depts_df, num_admissions=1800)
    generate_diagnoses(adms_df)
    print("🎉 All healthcare demonstration data successfully generated in ./data/ directory!")

if __name__ == "__main__":
    main()
