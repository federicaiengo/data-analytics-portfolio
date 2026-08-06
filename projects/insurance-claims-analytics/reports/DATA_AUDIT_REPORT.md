# DATA AUDIT REPORT

Project: Insurance Claims Analytics – Claims Performance & Fraud Detection

---

# Purpose

This report documents all data audits and technical validations completed during the project.

Successful checks, failures, corrective actions and validation queries are retained to preserve complete analytical traceability.

---

# DA-001 — Dataset Import Validation

## Expected Result

- `insurance_data`: 10,000 records
- `employee_data`: 1,200 records
- `vendor_data`: 600 records

## Actual Result

- `insurance_data`: 10,000
- `employee_data`: 1,200
- `vendor_data`: initially 0, then 600 after import correction

## Status

PASS

---

# DA-002 — Missing Relationship Identifiers

## Actual Result

- Missing `agent_id`: 0
- Missing `vendor_id`: 3,245

## Interpretation

NULL `vendor_id` values are valid business conditions representing claims without an assigned vendor.

## Status

PASS

---

# DA-003 — Primary Key Uniqueness

## Actual Result

No duplicate values were found for:

- `transaction_id`
- `agent_id`
- `vendor_id`

## Status

PASS

---

# DA-004 — Referential Integrity

## Actual Result

- Orphan agent references: 0
- Invalid non-null vendor references: 0

## Investigation

The initial vendor query returned 3,245 unmatched records.

Further analysis confirmed that all 3,245 records contained `vendor_id = NULL`.

## Conclusion

Vendor assignment is an optional relationship.

## Status

PASS

---

# DA-005 — Domain Value Review

## Categories Reviewed

- `insurance_type`
- `claim_status`
- `incident_severity`

## Status

PASS

---

# DA-006 — PostgreSQL Analytics Views Validation

## SQL Reference

`03_analytics_views.sql`

## DA-006A — Enriched Claims View

Expected: 10,000 records.

Actual: 10,000 records.

Status: PASS.

## DA-006B — Agent Exposure View

Expected: reproduce BA-010 ranking.

Actual: ranking matches BA-010.

Status: PASS.

## DA-006C — Vendor Exposure View

Expected: reproduce BA-012 ranking.

Actual: ranking matches BA-012.

Status: PASS.

## DA-006D — Product-Adjusted Agent Ranking View

Expected: reproduce BA-015 rankings within each insurance type.

Actual: rankings match BA-015 for Health, Life, Mobile, Motor, Property and Travel.

Status: PASS.

## DA-006E — Product-Adjusted Vendor Ranking View

Expected: reproduce BA-016 rankings within each insurance type.

Actual: pending execution.

Status: PENDING.

---

# Overall Status

PASS WITH ONE PENDING VIEW VALIDATION

All imported datasets, identifiers, relational links and four analytical views have been validated successfully.

The product-adjusted vendor ranking view requires final execution.

---

# Revision History

## Version 0.6

- Consolidated dataset audit results.
- Confirmed record preservation.
- Validated agent and vendor summary views.
- Validated product-adjusted agent ranking view.
- Added pending validation for the product-adjusted vendor ranking view.
