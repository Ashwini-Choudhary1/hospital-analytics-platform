-- ==============================================================================
-- Hospital Analytics Platform - Metabase BI Dashboard Query Reference
-- ==============================================================================
-- This file contains the standardized SQL queries used to power the 6 executive
-- cards on the "🏥 Hospital Operations & Clinical Executive Dashboard" in Metabase.
-- All queries execute against our Gold Medallion analytical tables.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Card 1: Total Patient Admissions (KPI Number)
-- ------------------------------------------------------------------------------
-- Description: Total volume of clinical admissions processed in the warehouse.
-- Visualization Suggestion: Number / KPI Card
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_admissions
FROM gold.fct_admissions;


-- ------------------------------------------------------------------------------
-- Card 2: Average Length of Stay (KPI Number)
-- ------------------------------------------------------------------------------
-- Description: Average duration (in days) patients spend hospitalized across departments.
-- Visualization Suggestion: Number / KPI Card
-- ------------------------------------------------------------------------------
SELECT 
    ROUND(AVG(length_of_stay_days), 1) AS avg_los_days
FROM gold.fct_admissions;


-- ------------------------------------------------------------------------------
-- Card 3: Overall 30-Day Readmission Rate (KPI Percentage)
-- ------------------------------------------------------------------------------
-- Description: Hospital-wide percentage of patients readmitted within 30 days of discharge.
-- Visualization Suggestion: Number / KPI Card (with % formatting)
-- ------------------------------------------------------------------------------
SELECT 
    ROUND(AVG(readmission_rate_pct), 2) AS overall_readmission_rate_pct
FROM gold.mart_readmission_rates;


-- ------------------------------------------------------------------------------
-- Card 4: Department Workload & Financial Analysis (Column / Bar Chart)
-- ------------------------------------------------------------------------------
-- Description: Total admissions, average stay duration, and total billing cost per department.
-- Visualization Suggestion: Column Chart (X: department_name, Y: total_admissions)
-- ------------------------------------------------------------------------------
SELECT 
    department_name,
    total_admissions,
    avg_length_of_stay_days,
    ROUND(total_hospital_cost, 2) AS total_hospital_cost
FROM gold.mart_department_workload
ORDER BY total_admissions DESC;


-- ------------------------------------------------------------------------------
-- Card 5: Top 10 Clinical Diagnoses (Horizontal Bar Chart)
-- ------------------------------------------------------------------------------
-- Description: Most frequent primary ICD-10 clinical diagnoses treated across the hospital.
-- Visualization Suggestion: Horizontal Bar Chart (X: total_cases, Y: diagnosis_description)
-- ------------------------------------------------------------------------------
SELECT 
    diagnosis_description,
    total_cases,
    ROUND(avg_cost_per_case, 2) AS avg_cost_per_case
FROM gold.mart_clinical_diagnoses
WHERE diagnosis_description != 'No Primary Diagnosis Recorded'
ORDER BY total_cases DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- Card 6: 30-Day Readmission Risk Breakdown (Data Table / Heatmap)
-- ------------------------------------------------------------------------------
-- Description: Comparative clinical risk analysis of readmission rates by department.
-- Visualization Suggestion: Table with conditional formatting on readmission_rate_pct
-- ------------------------------------------------------------------------------
SELECT 
    department_name,
    total_discharges,
    readmitted_30_days_count,
    readmission_rate_pct,
    avg_los_days,
    high_risk_readmissions
FROM gold.mart_readmission_rates
ORDER BY readmission_rate_pct DESC;
