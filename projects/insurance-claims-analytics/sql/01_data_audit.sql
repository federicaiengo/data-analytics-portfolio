/*
Project: Insurance Claims Analytics
File: 01_data_audit.sql
Purpose: Validate imports, identifiers, completeness and referential integrity.
Status: COMPLETED
*/

/* DA-001 — IMPORT VALIDATION | PASS */
SELECT COUNT(*) AS total_claims FROM insurance_data;
SELECT COUNT(*) AS total_agents FROM employee_data;
SELECT COUNT(*) AS total_vendors FROM vendor_data;

/* DA-002 — MISSING RELATIONSHIP IDENTIFIERS | PASS */
SELECT COUNT(*) AS missing_agent_id FROM insurance_data WHERE agent_id IS NULL;
SELECT COUNT(*) AS missing_vendor_id FROM insurance_data WHERE vendor_id IS NULL;

/* DA-003 — PRIMARY KEY UNIQUENESS | PASS */
SELECT transaction_id, COUNT(*) AS occurrences
FROM insurance_data GROUP BY transaction_id HAVING COUNT(*) > 1;
SELECT agent_id, COUNT(*) AS occurrences
FROM employee_data GROUP BY agent_id HAVING COUNT(*) > 1;
SELECT vendor_id, COUNT(*) AS occurrences
FROM vendor_data GROUP BY vendor_id HAVING COUNT(*) > 1;

/* DA-004 — REFERENTIAL INTEGRITY | PASS */
SELECT COUNT(*) AS orphan_agent_records
FROM insurance_data i
LEFT JOIN employee_data e ON i.agent_id = e.agent_id
WHERE e.agent_id IS NULL;

SELECT COUNT(*) AS invalid_non_null_vendor_records
FROM insurance_data i
LEFT JOIN vendor_data v ON i.vendor_id = v.vendor_id
WHERE i.vendor_id IS NOT NULL AND v.vendor_id IS NULL;

/* DA-004A — NULL VENDOR INVESTIGATION | PASS */
SELECT i.vendor_id, COUNT(*) AS claim_count
FROM insurance_data i
LEFT JOIN vendor_data v ON i.vendor_id = v.vendor_id
WHERE v.vendor_id IS NULL
GROUP BY i.vendor_id
ORDER BY claim_count DESC, i.vendor_id;

/* DA-005 — DOMAIN VALUE REVIEW | COMPLETED */
SELECT DISTINCT insurance_type FROM insurance_data ORDER BY insurance_type;
SELECT DISTINCT claim_status FROM insurance_data ORDER BY claim_status;
SELECT DISTINCT incident_severity FROM insurance_data ORDER BY incident_severity;
