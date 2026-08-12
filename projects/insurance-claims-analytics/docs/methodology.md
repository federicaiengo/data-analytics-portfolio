# Methodology

## Purpose

This document describes the analytical methodology used in the Insurance Claims Analytics project.

The workflow was designed to maintain traceability between raw data, SQL analysis, validated business findings and the final Tableau reporting layer.

---

## 1. Data Import

Three source datasets were imported into PostgreSQL:

- `insurance_data.csv`
- `employee_data.csv`
- `vendor_data.csv`

Raw source files were preserved without analytical modification.

The imported tables formed the relational foundation for subsequent data-quality validation and business analysis.

---

## 2. Data Audit

Before business analysis, the datasets were audited to identify structural and data-quality issues.

Audit checks included:

- record counts;
- null values;
- duplicate records;
- key-field validation;
- categorical-value inspection;
- numerical-range inspection;
- relational consistency.

Issues discovered during this stage were documented rather than silently corrected.

---

## 3. Referential Integrity Validation

Relationships between the claims dataset and reference tables were tested explicitly.

This included validation of:

- employee identifiers;
- agent relationships;
- vendor identifiers;
- unmatched or missing references.

Referential-integrity findings were separated from business-performance conclusions to avoid interpreting data-quality problems as operational performance.

---

## 4. Business Analysis

Business analysis was performed using reproducible SQL queries.

The analysis examined:

- claim volume;
- total financial exposure;
- average claim value;
- insurance product mix;
- high-value claims;
- claim severity;
- agent exposure;
- vendor exposure;
- portfolio concentration.

Each analysis was tied to a defined business question rather than performed solely as exploratory aggregation.

---

## 5. Evidence Validation

Analytical outputs were evaluated before being promoted to business findings.

A result was retained as a validated finding only when:

- the SQL evidence supported the conclusion;
- the result had meaningful business relevance;
- alternative explanations were considered where necessary;
- the conclusion did not exceed what the data could demonstrate.

Analyses that did not meet these criteria were retained separately as rejected findings.

This preserves analytical work while preventing unsupported conclusions from entering the final reporting layer.

---

## 6. Business Findings

Validated findings were documented using a consistent structure:

1. Title
2. Business Question
3. SQL Reference or Visual Reference
4. Finding
5. Evidence where applicable
6. Business Impact
7. Recommendation
8. Priority
9. Confidence

This structure connects technical evidence to business interpretation and recommended action.

---

## 7. KPI Development

Executive KPIs were derived from validated portfolio-level calculations.

The final dashboard includes:

- Total Claims;
- Total Financial Exposure;
- Average Claim Amount;
- Very-High-Value Exposure.

KPIs were generated from reproducible analytical outputs rather than manually estimated from visualizations.

---

## 8. Visualization Methodology

Tableau was used to translate validated analytical outputs into decision-oriented visualizations.

The final visualization set focuses on three complementary dimensions of portfolio risk:

### VIZ-001 — Lorenz Curve: Claim Financial Exposure

Used to evaluate concentration of financial exposure across the claims portfolio.

### VIZ-002 — Financial Exposure by Insurance Type

Used to compare product-level contribution to total portfolio exposure.

### VIZ-003 — Financial Exposure by Claim Severity

Used to evaluate how financial exposure is distributed across claim-value severity bands.

Supporting analyses that did not materially improve the final executive dashboard were retained outside the primary visualization layer.

---

## 9. Executive Dashboard

The final Tableau dashboard combines:

- four executive KPIs;
- financial-exposure concentration;
- product-level exposure;
- severity-level exposure.

The dashboard was designed for rapid executive interpretation rather than exhaustive exploratory analysis.

Detailed supporting evidence remains available in SQL queries and project documentation.

---

## 10. Analytical Traceability

The project maintains separation between:

- raw source data;
- data-quality validation;
- SQL business analysis;
- rejected analyses;
- validated business findings;
- visualization outputs;
- executive reporting.

This separation makes it possible to trace dashboard conclusions back to their analytical evidence.

---

## Audit Documentation Standard

All audit reports follow the same structure whenever applicable:

1. Business Question
2. SQL
3. Expected Result
4. Actual Result
5. Status
6. Root Cause (FAIL only)
7. Corrective Action (FAIL only)
8. Business Impact
9. Next Action (optional)

This standard ensures consistency, traceability and reproducibility across all data quality validations performed during the project.
