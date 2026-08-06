# DATA AUDIT REPORT

Project: Insurance Claims Analytics – Claims Performance & Fraud Detection

---

# Purpose

This report documents all data audits and technical validations completed during the project.

---

# DA-001 — Dataset Import Validation

- insurance_data: 10,000
- employee_data: 1,200
- vendor_data: initially 0, then 600 after import correction

Status: PASS

---

# DA-002 — Missing Relationship Identifiers

- Missing agent_id: 0
- Missing vendor_id: 3,245

Interpretation: NULL vendor_id values are valid claims without an assigned vendor.

Status: PASS

---

# DA-003 — Primary Key Uniqueness

No duplicate transaction_id, agent_id or vendor_id values were found.

Status: PASS

---

# DA-004 — Referential Integrity

- Orphan agent references: 0
- Invalid non-null vendor references: 0

The 3,245 initially unmatched vendor records all contained vendor_id = NULL.

Status: PASS

---

# DA-005 — Domain Value Review

Reviewed insurance_type, claim_status and incident_severity values.

Status: PASS

---

# DA-006 — PostgreSQL Analytics Views Validation

## DA-006A — vw_claims_enriched

Expected: 10,000 records.

Actual: 10,000 records.

Status: PASS

## DA-006B — vw_agent_exposure_summary

Expected: reproduce BA-010 ranking.

Actual: ranking matches BA-010.

Status: PASS

## DA-006C — vw_vendor_exposure_summary

Expected: reproduce BA-012 ranking.

Actual: ranking matches BA-012.

Status: PASS

## DA-006D — vw_agent_product_ranking

Expected: reproduce BA-015 product-specific rankings.

Actual: pending execution.

Status: PENDING
