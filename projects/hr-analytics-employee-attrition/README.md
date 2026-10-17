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

A separate [28-row aggregate CSV](excel/hr_dashboard_group_metrics.csv) contains privacy-minimal grouped metrics, and [`python/build_dashboard_source.py`](python/build_dashboard_source.py) supplies the deterministic rebuild logic for that **CSV**. The [reproducibility report](reports/DASHBOARD_REPRODUCIBILITY_2026-10-09.md) preserves historical fixture-only QA and the newer **32/32 Python tests passing in GitHub Actions**, including 28/28 XLSX group checks. This does not yet provide automatic XLSX regeneration.

A [cleaned 1,470-row, 32-column working dataset](data/clean/employee_attrition_clean.csv) is now available. Full-source checks found zero blanks/duplicates and identified precisely three constant columns, removed from the cleaned copy without deleting or modifying any employee record. The [quality log](data/clean/DATA_QUALITY_LOG.md) and [transformations](data/clean/CLEANING_PROTOCOL.md) document the evidence. Python source and **13/13 locally passing cleaning tests** were verified against Git blob hashes. An [independent full-source reconciliation (2026-10-13)](reports/FULL_SOURCE_RECONCILIATION_2026-10-13.md) matched the 1,470-row cleaned dataset **byte for byte**, and separately matched all 28 grouped metrics across seven dimensions. The production Python cleaner and aggregate generator have now been run end-to-end in the [manual full-source QA workflow](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/38336050248): **24/24 tests PASS**, including both full-source regression tests. Both regenerated CSV artifacts matched the tracked references **byte for byte**. The verification used Python 3.12 and temporary output paths; the original CSV remained unchanged. The Excel workbook is still static: application compatibility and automatic XLSX regeneration are not yet verified.

The [manual HR QA run on 2026-10-13](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/38406517149) additionally **passed read-only structural checks on the committed seven-sheet XLSX** (ZIP/XML, worksheet relationships, no cached error cells). The file stores no formulas. This is **not** a cell-by-cell comparison against the aggregate CSV and **does not** verify rendering in desktop Excel. See the [reproducibility report](reports/DASHBOARD_REPRODUCIBILITY_2026-10-09.md).

[Static workbook 28/28 reconciliation](reports/WORKBOOK_PARITY_2026-10-13.md): an independent read-only check found all 28 source group counts, attritions and displayed rates consistent with the XLSX, with rounding tolerance and recorded provenance. The new Python parity gate and eight mutation-oriented tests **passed in the manually triggered [GitHub Actions run 38411506600](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/38411506600)**: **32/32 Python tests PASS**, with **28/28 XLSX groups and seven Dashboard mirrors reconciled**, plus source-provenance checks. An [optional template-based XLSX refresher](python/refresh_workbook_snapshot.py) is now available for separate output paths; its full real-workbook execution and visual fidelity remain unverified.

### Workbook refresh safety (17 October 2026)

The optional [workbook refresh script](python/refresh_workbook_snapshot.py) refuses to overwrite the original workbook, any source CSV or an existing output file. It also rejects unknown templates and symbolic-link output paths. Six fixture-only safety regressions in [test_refresh_workbook_safety.py](tests/test_refresh_workbook_safety.py) **passed locally (6/6)** on exact GitHub-matched source and test blobs. Unrelated aggregation and parity imports were isolated with explicit failing placeholders to exercise only these early input-protection paths.

**Still pending:** importing and regenerating the real committed XLSX, all-source verification in the same run, Microsoft Excel compatibility and visual fidelity. The passing safety tests are not a completed workbook rebuild or a new GitHub Actions CI run.

## Deliverable inventory

- Original public dataset: **available** in `data/raw/`
- SQL audit and analysis queries: **available** in `sql/`
- Business findings: **available** in [`reports/business_findings.md`](reports/business_findings.md)
- Excel comparison/dashboard workbook: **created**, Excel application QA and full XLSX regeneration steps pending
- Privacy-minimal 28-row aggregate CSV, deterministic generation script and nine passing unit tests: **available**
- Cleaned 1,470 × 32 dataset: **created, audited, independently reconciled and reproducibly rebuilt** from the tracked source
- Independent full-source artifact reconciliation: **PASS** (JavaScript-based audit of tracked CSVs, not Python pipeline execution)
- Full-source Python cleaner and aggregate-generator regression gates: **PASS**, alongside 22 fixture-based tests (24/24 total); [verified workflow run](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/38336050248)
- Final descriptive analytical review: **complete**, see [the evidence-linked conclusion](reports/FINAL_ANALYTICAL_REVIEW_2026-10-13.md); full spreadsheet-deliverable closure still awaits desktop Excel QA and verified XLSX regeneration.

---

## Dataset

IBM HR Analytics Employee Attrition & Performance

Public dataset used for educational and portfolio purposes.

---

## Interpretation and limitations

The [final analytical review](reports/FINAL_ANALYTICAL_REVIEW_2026-10-13.md) rechecked source figures, including department-stratified overtime comparisons, and distinguishes observational findings from causal claims or intervention outcomes. It completes the interpretation/recommendation review, not the remaining Excel-specific gates.


This is an observational analysis of a public educational dataset, not a randomized experiment or a live employer study. Differences between groups do not establish that overtime, salary or job characteristics cause attrition. Group sizes, missingness, confounding and the dataset's scope must be considered before generalizing findings or proposing interventions.

## Project Status

🚧 In Progress — source cleaning, aggregate CSV regeneration and read-only XLSX-to-source parity are verified in GitHub Actions (**32/32 Python tests PASS**, 28/28 aggregate groups matched). Remaining: validate desktop Excel workbook compatibility and verify real-workbook XLSX regeneration without design regressions. The final descriptive analytical review is complete.
