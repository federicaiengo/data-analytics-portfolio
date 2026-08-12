# Insurance Claims Analytics – Risk, Exposure & Performance Analysis

## Project Overview

This project analyzes a relational insurance claims dataset using PostgreSQL, SQL and Tableau to evaluate financial exposure, claims performance, data quality and operational risk.

The project demonstrates an end-to-end analytics workflow: raw data is audited and validated before business analysis, analytical findings are tested against the available evidence, and validated results are translated into an executive Tableau dashboard and documented business recommendations.

The repository is structured as a client-ready portfolio project with an emphasis on reproducibility, analytical traceability and decision-oriented reporting.

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
