# DATA AUDIT REPORT

Project: Insurance Claims Analytics – Claims Performance & Fraud Detection

---

# Purpose

This report documents every data audit performed during the project.

All checks remain recorded to ensure complete analytical traceability.

---

# DA-001

## Audit

Employee Data Import

## Business Question

Has the employee dataset been successfully imported into PostgreSQL?

## SQL

```sql
SELECT COUNT(*) AS total_agents
FROM employee_data;
```

## Expected Result

1,200 records.

## Actual Result

1,200 records.

## Status

PASS

## Notes

The employee dataset was successfully imported.

---

# DA-002

## Audit

Vendor Data Import

## Business Question

Has the vendor dataset been successfully imported into PostgreSQL?

## SQL

```sql
SELECT COUNT(*) AS total_vendors
FROM vendor_data;
```

## Expected Result

600 records.

## Actual Result

Initial execution: 0 records.

Final validation after import: 600 records.

## Status

PASS

## Root Cause

The initial query was executed before `vendor_data.csv` had been imported.

## Corrective Action

Imported `vendor_data.csv` through pgAdmin and repeated the validation query.

## Notes

The initial failure was procedural and did not indicate a data-quality defect.

---

# DA-003

## Audit

Primary Key Uniqueness

## Business Question

Are the primary identifiers unique across all imported tables?

## SQL

```sql
SELECT transaction_id, COUNT(*)
FROM insurance_data
GROUP BY transaction_id
HAVING COUNT(*) > 1;

SELECT agent_id, COUNT(*)
FROM employee_data
GROUP BY agent_id
HAVING COUNT(*) > 1;

SELECT vendor_id, COUNT(*)
FROM vendor_data
GROUP BY vendor_id
HAVING COUNT(*) > 1;
```

## Expected Result

No duplicate identifiers returned.

## Actual Result

No duplicate `transaction_id`, `agent_id` or `vendor_id` values were found.

## Status

PASS

## Business Impact

Unique primary identifiers support reliable joins and preserve entity integrity.

---

# DA-004

## Audit

Referential Integrity

## Business Question

Are all non-null claim relationship identifiers linked to valid agents and vendors?

## SQL

```sql
SELECT COUNT(*) AS orphan_agent_records
FROM insurance_data i
LEFT JOIN employee_data e
    ON i.agent_id = e.agent_id
WHERE e.agent_id IS NULL;

SELECT COUNT(*) AS orphan_vendor_records
FROM insurance_data i
LEFT JOIN vendor_data v
    ON i.vendor_id = v.vendor_id
WHERE i.vendor_id IS NOT NULL
  AND v.vendor_id IS NULL;
```

## Expected Result

0 orphan agent records.

0 unmatched non-null vendor records.

## Actual Result

- Orphan agent records: 0
- Unmatched non-null vendor records: 0

## Status

PASS

## Investigation

The initial vendor query returned 3,245 unmatched records.

Further analysis showed that all 3,245 records contained `vendor_id = NULL`.

```sql
SELECT
    i.vendor_id,
    COUNT(*) AS claim_count
FROM insurance_data i
LEFT JOIN vendor_data v
    ON i.vendor_id = v.vendor_id
WHERE v.vendor_id IS NULL
GROUP BY i.vendor_id;
```

Result:

- `vendor_id = NULL`
- Claim count = 3,245

## Interpretation

The 3,245 records are not invalid foreign keys.

They represent claims without an assigned vendor.

Null vendor identifiers must therefore be evaluated as a completeness or business-process condition, not as a referential-integrity failure.

## Business Impact

All populated relationship identifiers are valid.

Vendor-based analyses must exclude or separately classify claims without an assigned vendor.

## Corrective Action

Updated the referential-integrity query to distinguish null identifiers from invalid non-null identifiers.

---

# Revision History

## Version 0.3

- Validated employee and vendor imports.
- Confirmed primary-key uniqueness.
- Investigated 3,245 apparently unmatched vendor records.
- Confirmed that all populated vendor identifiers are valid.
- Reclassified null vendor assignments as a separate completeness condition.

---

# DA-005

## Audit

Analytics Views Validation

## Business Question

Do the reusable PostgreSQL views reproduce the validated analytical results?

## SQL Reference

03_analytics_views.sql

## Views

- `vw_claims_enriched`
- `vw_agent_exposure_summary`
- `vw_vendor_exposure_summary`

## Vendor View Result

`vw_vendor_exposure_summary` reproduces the vendor ranking previously obtained through BA-012.

The view also calculates the number of high-value claims associated with each vendor.

## Status

PARTIAL PASS

## Pending Validation

- Confirm that `vw_claims_enriched` contains 10,000 records.
- Confirm that `vw_agent_exposure_summary` reproduces the BA-010 ranking.

## Business Impact

Validated views provide reusable datasets for reporting and future Power BI development without duplicating analytical SQL.

