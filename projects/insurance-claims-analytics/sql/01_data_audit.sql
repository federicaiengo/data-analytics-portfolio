/*
Project: Insurance Claims Analytics
File: 01_data_audit.sql

Purpose:
Validate dataset imports, identifier uniqueness, completeness
and referential integrity across the three project tables.

Status:
IN PROGRESS
*/


/* =========================================================
   DA-001 — IMPORT VALIDATION
   ========================================================= */

/*
Purpose:
Verify that all three CSV datasets were imported.

Expected Result:
- insurance_data: 10,000 records
- employee_data: 1,200 records
- vendor_data: 600 records

Actual Result:
- employee_data: 1,200 records
- vendor_data: initially 0, then 600 after import correction
- insurance_data: to be confirmed

Status:
IN PROGRESS
*/

SELECT COUNT(*) AS total_claims
FROM insurance_data;

SELECT COUNT(*) AS total_agents
FROM employee_data;

SELECT COUNT(*) AS total_vendors
FROM vendor_data;


/* =========================================================
   DA-002 — MISSING RELATIONSHIP IDENTIFIERS
   ========================================================= */

/*
Purpose:
Identify claims with missing agent_id or vendor_id values.

Expected Result:
Determine whether relationship identifiers are complete.

Actual Result:
To be recorded after execution.

Status:
PENDING
*/

SELECT COUNT(*) AS missing_agent_id
FROM insurance_data
WHERE agent_id IS NULL;

SELECT COUNT(*) AS missing_vendor_id
FROM insurance_data
WHERE vendor_id IS NULL;


/* =========================================================
   DA-003 — PRIMARY KEY UNIQUENESS
   ========================================================= */

/*
Purpose:
Verify uniqueness of the primary identifiers.

Expected Result:
No duplicate identifiers.

Actual Result:
No duplicate transaction_id, agent_id or vendor_id values found.

Status:
PASS
*/

SELECT
    transaction_id,
    COUNT(*) AS occurrences
FROM insurance_data
GROUP BY transaction_id
HAVING COUNT(*) > 1;

SELECT
    agent_id,
    COUNT(*) AS occurrences
FROM employee_data
GROUP BY agent_id
HAVING COUNT(*) > 1;

SELECT
    vendor_id,
    COUNT(*) AS occurrences
FROM vendor_data
GROUP BY vendor_id
HAVING COUNT(*) > 1;


/* =========================================================
   DA-004 — REFERENTIAL INTEGRITY
   ========================================================= */

/*
Purpose:
Verify that claim records reference valid agents and vendors.

Expected Result:
- 0 orphan agent records
- 0 orphan vendor records

Actual Result:
- orphan agent records: 0
- orphan vendor records: 3,245

Status:
UNDER INVESTIGATION
*/

SELECT COUNT(*) AS orphan_agent_records
FROM insurance_data i
LEFT JOIN employee_data e
    ON i.agent_id = e.agent_id
WHERE e.agent_id IS NULL;

SELECT COUNT(*) AS orphan_vendor_records
FROM insurance_data i
LEFT JOIN vendor_data v
    ON i.vendor_id = v.vendor_id
WHERE v.vendor_id IS NULL;


/* =========================================================
   DA-004A — UNMATCHED VENDOR INVESTIGATION
   ========================================================= */

/*
Purpose:
Inspect unmatched vendor identifiers and measure how frequently
each unmatched value appears.

Expected Result:
Determine whether the 3,245 unmatched claims contain:
- NULL or blank identifiers;
- a small set of repeated codes;
- many distinct identifiers absent from vendor_data.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    i.vendor_id,
    COUNT(*) AS claim_count
FROM insurance_data i
LEFT JOIN vendor_data v
    ON i.vendor_id = v.vendor_id
WHERE v.vendor_id IS NULL
GROUP BY i.vendor_id
ORDER BY claim_count DESC
LIMIT 20;


/* =========================================================
   DA-005 — DOMAIN VALUE REVIEW
   ========================================================= */

/*
Purpose:
Inspect categorical values used in business analysis.

Expected Result:
Identify valid categories and possible inconsistencies.

Actual Result:
Pending review.

Status:
PENDING
*/

SELECT DISTINCT insurance_type
FROM insurance_data
ORDER BY insurance_type;

SELECT DISTINCT claim_status
FROM insurance_data
ORDER BY claim_status;

SELECT DISTINCT incident_severity
FROM insurance_data
ORDER BY incident_severity;
/* =========================================================
   DA-004A — UNMATCHED VENDOR ANALYSIS
   ========================================================= */

/*
Purpose:
Identify which Vendor IDs do not match the vendor master table.

Status:
IN PROGRESS
*/

SELECT
    i.vendor_id,
    COUNT(*) AS claim_count
FROM insurance_data i
LEFT JOIN vendor_data v
    ON i.vendor_id = v.vendor_id
WHERE v.vendor_id IS NULL
GROUP BY i.vendor_id
ORDER BY claim_count DESC, i.vendor_id
LIMIT 20;

-- Referential Integrity (excluding NULL Vendor IDs)

SELECT COUNT(*) AS orphan_vendor_records
FROM insurance_data i
LEFT JOIN vendor_data v
    ON i.vendor_id = v.vendor_id
WHERE i.vendor_id IS NOT NULL
  AND v.vendor_id IS NULL;
  
  