# Insurance Claims Analytics – Risk, Exposure & Performance Analysis

## Project Overview

This project analyzes a relational insurance claims dataset using PostgreSQL, SQL and Tableau to evaluate financial exposure, claims performance, data quality and operational risk.

The project demonstrates an end-to-end analytics workflow: raw data is audited and validated before business analysis, analytical findings are tested against the available evidence, and validated results are translated into an executive Tableau dashboard and documented business recommendations.

The repository is structured as a client-ready portfolio project with an emphasis on reproducibility, analytical traceability and decision-oriented reporting.

### Interactive Dashboard

[View the Insurance Claims — Executive Risk & Exposure Dashboard on Tableau Public](https://public.tableau.com/app/profile/federica.iengo/viz/insurance_claims_dashboard/Dashboard1)

---

## Dataset

The project uses three related datasets:

- `insurance_data.csv`
- `employee_data.csv`
- `vendor_data.csv`

The primary dataset contains 10,000 insurance claims linked to employee and vendor reference data.

The analysis covers:

- claim volume;
- financial exposure;
- insurance product mix;
- claim severity;
- high-value claims;
- agent exposure;
- vendor exposure;
- data quality and referential integrity.

---

## Business Objectives

- Assess insurance claims performance.
- Validate data quality before business analysis.
- Verify referential integrity across related datasets.
- Measure total and average financial exposure.
- Identify high-value and high-severity claims.
- Evaluate exposure concentration across insurance products.
- Assess how product mix affects agent and vendor exposure.
- Identify analytically defensible risk indicators.
- Produce reproducible business findings.
- Translate validated analysis into executive-level reporting.

---

## Technologies

- PostgreSQL
- pgAdmin
- SQL
- Tableau
- Relational Databases
- Data Auditing
- Data Quality
- Referential Integrity
- Exploratory Data Analysis
- Business Analysis
- KPI Design
- Data Visualization
- Business Reporting
- Git
- GitHub
- Markdown

---

## Analytical Workflow

1. Data Import
2. Data Audit
3. Data Quality Validation
4. Referential Integrity Validation
5. Business Analysis
6. Evidence Validation
7. Business Findings
8. Rejected Findings Documentation
9. KPI Development
10. Data Visualization
11. Executive Dashboard Development
12. Business Recommendations

This workflow deliberately separates exploratory analysis from validated findings so that conclusions included in the final reporting layer remain supported by reproducible evidence.

---

## Repository Structure

```text
insurance-claims-analytics/
│
├── data/
│   ├── raw/
│   └── clean/
│
├── sql/
│
├── docs/
│
├── reports/
│
└── assets/
```


---

## Current reproducibility and data availability

The original analysis and Tableau dashboard were built from three related source tables. Their 10,000-claim aggregates and selected checks are documented in the historical [source audit](reports/RAW_SOURCE_KPI_SPOT_CHECK_2026-10-09.md). **The three raw CSV files are no longer distributed on the current public branch** while their provenance and redistribution rights remain unverified. Deleting files from the current branch does not remove them from Git history, forks, caches or third-party exports.

This is a deliberate scope limitation: the historical 10,000-row calculations cannot currently be rerun using only the public branch, and the existence of a Tableau dashboard does not certify raw-data licensing or a current dashboard review. **Do not represent the three-row demo as the original source or as a fresh validation of the published 10,000-row KPIs.**

The Python audit remains executable on explicitly authorized data. To inspect its behavior without real names, addresses or financial identifiers, use the clearly fabricated three-row fixture:

```bash
python -m unittest discover -s tests -v
python python/verify_public_kpis.py --input tests/fixtures/synthetic_insurance_claims.csv
```

The 11 Python tests passed locally on 16 October 2026 using exact GitHub source blob hashes. These are fixture-level software tests, **not** a fresh validation of the historical dataset. The script reports `NOT_RUN` for the historical baseline unless `--check-historical-baseline` is explicitly specified with an authorized, comparable input. Missing raw input is reported as `SOURCE UNAVAILABLE`, not as a failed insurance claim reconciliation.

Remaining work: establish defensible data licensing/synthetic provenance, inspect any historical repository copies and Tableau/public derivative exports, and restore end-to-end reproducibility only using data approved for distribution. Avoid introducing personal-looking sample rows to solve this gap.
