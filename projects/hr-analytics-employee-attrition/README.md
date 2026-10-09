# HR Analytics: Employee Attrition & Workforce Insights

## Project Overview

This project analyzes employee data to explore observed associations with employee attrition, satisfaction and selected workforce indicators.

The objective is to transform raw HR data into actionable business insights through data cleaning, SQL analysis, KPI reporting and business-oriented recommendations.

---

## Business Objectives

- Describe how observed attrition rates vary across employee groups.
- Identify departments and roles with higher turnover.
- Explore associations involving overtime, salary, education and job satisfaction without assuming causation.
- Measure workforce performance through HR KPIs.
- Improve reporting quality for management decision-making.
- Detect data quality issues before analysis.

---

## Business Questions

- Which departments experience the highest attrition?
- Which employee characteristics are associated with higher turnover?
- How does observed attrition differ between employees reporting overtime and those who do not?
- Is salary correlated with employee attrition?
- Which HR KPIs should management monitor?
- Which data quality issues can affect reporting accuracy?
- Which hypotheses and follow-up analyses could inform retention decisions?

---

## Tools

- SQL
- Microsoft Excel
- Data Cleaning
- Data Validation
- Business Reporting
- KPI Reporting
- HR Analytics

---

## Key Performance Indicators

- Attrition Rate
- Employee Count
- Active Employees
- Average Monthly Income
- Average Years at Company
- Overtime Rate
- Department Attrition
- Job Role Attrition
- Satisfaction Metrics

---

## Repository Structure

text
data/
├── raw/
└── clean/

sql/

excel/

images/

insights/


---

## Evidence and dashboard — current status

The [Excel evidence dashboard](excel/HR_Attrition_Evidence_Dashboard.xlsx) now exists in the repository as a **static workbook** built from the original public CSV. It contains a summary and descriptive group comparisons for overtime, job role, department, satisfaction and company tenure. The workbook's existence and Git blob were confirmed, but compatibility in desktop Excel has **not yet been independently verified**.

Observed counts verified directly against the source CSV: **1,470 employee rows**, **237 attritions (16.12%)**; **127/416 (30.53%)** with overtime versus **110/1,054 (10.44%)** without overtime. These are associations, not causal effects or evidence from a live employer.

A separate [28-row aggregate CSV](excel/hr_dashboard_group_metrics.csv) contains privacy-minimal grouped metrics, and [`python/build_dashboard_source.py`](python/build_dashboard_source.py) supplies the deterministic rebuild logic for that **CSV**. The [reproducibility report](reports/DASHBOARD_REPRODUCIBILITY_2026-10-09.md) documents **9 locally passing unit tests** and the remaining end-to-end QA limitations. This does not yet provide automatic XLSX regeneration.

A [cleaned 1,470-row, 32-column working dataset](data/clean/employee_attrition_clean.csv) is now available. Full-source checks found zero blanks/duplicates and identified precisely three constant columns, removed from the cleaned copy without deleting or modifying any employee record. The [quality log](data/clean/DATA_QUALITY_LOG.md) and [transformations](data/clean/CLEANING_PROTOCOL.md) document the evidence. Python source and **13/13 locally passing cleaning tests** were verified against Git blob hashes. The end-to-end 1,470-record Python rerun remains to be verified. The final Excel reproducibility and compatibility steps remain in progress.

## Deliverable inventory

- Original public dataset: **available** in `data/raw/`
- SQL audit and analysis queries: **available** in `sql/`
- Business findings: **available** in [`reports/business_findings.md`](reports/business_findings.md)
- Excel comparison/dashboard workbook: **created**, Excel application QA and full XLSX regeneration steps pending
- Privacy-minimal 28-row aggregate CSV, deterministic generation script and nine passing unit tests: **available**
- Cleaned 1,470 × 32 dataset: **created and readback-verified**, with full-source quality audit, transformation rules and unexecuted new cleaning unit tests
- Final validated recommendations and project closure: **pending**

---

## Dataset

IBM HR Analytics Employee Attrition & Performance

Public dataset used for educational and portfolio purposes.

---

## Interpretation and limitations

This is an observational analysis of a public educational dataset, not a randomized experiment or a live employer study. Differences between groups do not establish that overtime, salary or job characteristics cause attrition. Group sizes, missingness, confounding and the dataset's scope must be considered before generalizing findings or proposing interventions.

## Project Status

🚧 In Progress — cleaned CSV and static Excel workbook exist. Remaining: verify end-to-end full-data Python rebuild, validate workbook compatibility, automate workbook regeneration, complete final analytical review.
