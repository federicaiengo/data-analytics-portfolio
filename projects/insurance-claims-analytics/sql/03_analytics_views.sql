/*
Project: Insurance Claims Analytics
File: 03_analytics_views.sql

Purpose:
Create and validate reusable PostgreSQL views for business analysis,
reporting and future dashboard development.

Expected Result:
Provide standardized analytical datasets without repeating complex SQL.

Status:
PASS
*/


/* =========================================================
   VIEW-001 — CLAIMS ENRICHED
   ========================================================= */

/*
Purpose:
Combine claim, agent and vendor data into one reusable analytical view.

Expected Result:
One row per insurance claim, enriched with agent and vendor details.

Actual Result:
10,000 records, matching the insurance_data source table.

Status:
PASS
*/

CREATE OR REPLACE VIEW vw_claims_enriched AS
SELECT
    i.transaction_id,
    i.txn_date_time,
    i.customer_id,
    i.policy_number,
    i.insurance_type,
    i.premium_amount,
    i.claim_amount,
    i.claim_status,
    i.incident_severity,
    i.risk_segmentation,
    i.police_report_available,
    i.any_injury,
    i.authority_contacted,
    i.incident_state,
    i.incident_city,
    i.incident_hour_of_the_day,
    i.agent_id,
    e.agent_name,
    i.vendor_id,
    v.vendor_name
FROM insurance_data i
LEFT JOIN employee_data e
    ON i.agent_id = e.agent_id
LEFT JOIN vendor_data v
    ON i.vendor_id = v.vendor_id;


/* =========================================================
   VIEW-002 — AGENT EXPOSURE SUMMARY
   ========================================================= */

/*
Purpose:
Create a reusable agent-level exposure summary.

Expected Result:
One row per agent containing claim volume, total exposure,
average claim amount and high-value claim count.

Actual Result:
The ranking matches BA-010.

Status:
PASS
*/

CREATE OR REPLACE VIEW vw_agent_exposure_summary AS
SELECT
    agent_id,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount,
    COUNT(*) FILTER (
        WHERE claim_amount >= 95000
    ) AS high_value_claims
FROM insurance_data
GROUP BY agent_id;


/* =========================================================
   VIEW-003 — VENDOR EXPOSURE SUMMARY
   ========================================================= */

/*
Purpose:
Create a reusable vendor-level exposure summary.

Expected Result:
One row per populated vendor containing claim volume,
total exposure, average claim amount and high-value claim count.

Actual Result:
The ranking matches BA-012.

Status:
PASS
*/

CREATE OR REPLACE VIEW vw_vendor_exposure_summary AS
SELECT
    vendor_id,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount,
    COUNT(*) FILTER (
        WHERE claim_amount >= 95000
    ) AS high_value_claims
FROM insurance_data
WHERE vendor_id IS NOT NULL
GROUP BY vendor_id;


/* =========================================================
   VALIDATION-001 — ENRICHED CLAIM RECORD COUNT
   ========================================================= */

/*
Validation Question:
Does the enriched analytical view preserve the original claim count?

Expected Result:
10,000 records.

Actual Result:
10,000 records.

Status:
PASS
*/

SELECT COUNT(*) AS enriched_claim_records
FROM vw_claims_enriched;


/* =========================================================
   VALIDATION-002 — AGENT VIEW RANKING
   ========================================================= */

/*
Validation Question:
Does the agent exposure view reproduce the BA-010 ranking?

Expected Result:
The top-agent ranking must match BA-010.

Actual Result:
The ranking matches BA-010.

Status:
PASS
*/

SELECT *
FROM vw_agent_exposure_summary
ORDER BY total_claim_amount DESC
LIMIT 10;


/* =========================================================
   VALIDATION-003 — VENDOR VIEW RANKING
   ========================================================= */

/*
Validation Question:
Does the vendor exposure view reproduce the BA-012 ranking?

Expected Result:
The top-vendor ranking must match BA-012.

Actual Result:
The ranking matches BA-012.

Status:
PASS
*/

SELECT *
FROM vw_vendor_exposure_summary
ORDER BY total_claim_amount DESC
LIMIT 10;