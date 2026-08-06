/*
Project: Insurance Claims Analytics
File: 03_analytics_views.sql

Purpose:
Create and validate reusable PostgreSQL views for business analysis,
reporting and future dashboard development.

Expected Result:
Provide standardized analytical datasets without repeating complex SQL.

Status:
IN PROGRESS
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
10,000 records, matching insurance_data.

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

Actual Result:
Ranking matches BA-010.

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

Actual Result:
Ranking matches BA-012.

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
   VIEW-004 — PRODUCT-ADJUSTED AGENT RANKING
   ========================================================= */

/*
Purpose:
Rank agents separately within each insurance product.

Actual Result:
The view reproduces the BA-015 rankings for all six insurance types.

Status:
PASS
*/

CREATE OR REPLACE VIEW vw_agent_product_ranking AS
SELECT
    insurance_type,
    agent_id,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount,
    ROW_NUMBER() OVER (
        PARTITION BY insurance_type
        ORDER BY SUM(claim_amount) DESC
    ) AS product_ranking
FROM insurance_data
GROUP BY insurance_type, agent_id;


/* =========================================================
   VIEW-005 — PRODUCT-ADJUSTED VENDOR RANKING
   ========================================================= */

/*
Purpose:
Rank vendors separately within each insurance product.

Expected Result:
Reproduce the BA-016 product-specific vendor rankings.

Actual Result:
Pending execution.

Status:
PENDING
*/

CREATE OR REPLACE VIEW vw_vendor_product_ranking AS
SELECT
    insurance_type,
    vendor_id,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount,
    ROW_NUMBER() OVER (
        PARTITION BY insurance_type
        ORDER BY SUM(claim_amount) DESC
    ) AS product_ranking
FROM insurance_data
WHERE vendor_id IS NOT NULL
GROUP BY insurance_type, vendor_id;


/* =========================================================
   VALIDATION-001 — ENRICHED CLAIM RECORD COUNT
   ========================================================= */

SELECT COUNT(*) AS enriched_claim_records
FROM vw_claims_enriched;


/* =========================================================
   VALIDATION-002 — AGENT VIEW RANKING
   ========================================================= */

SELECT *
FROM vw_agent_exposure_summary
ORDER BY total_claim_amount DESC
LIMIT 10;


/* =========================================================
   VALIDATION-003 — VENDOR VIEW RANKING
   ========================================================= */

SELECT *
FROM vw_vendor_exposure_summary
ORDER BY total_claim_amount DESC
LIMIT 10;


/* =========================================================
   VALIDATION-004 — PRODUCT-ADJUSTED AGENT RANKING
   ========================================================= */

SELECT *
FROM vw_agent_product_ranking
WHERE product_ranking <= 10
ORDER BY insurance_type, product_ranking;


/* =========================================================
   VALIDATION-005 — PRODUCT-ADJUSTED VENDOR RANKING
   ========================================================= */

SELECT *
FROM vw_vendor_product_ranking
WHERE product_ranking <= 10
ORDER BY insurance_type, product_ranking;
