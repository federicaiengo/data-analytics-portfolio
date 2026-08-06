/*
Project: Insurance Claims Analytics
File: 03_analytics_views.sql
Purpose: Create and validate reusable PostgreSQL views.
Status: CURRENT
*/

CREATE OR REPLACE VIEW vw_claims_enriched AS
SELECT i.transaction_id, i.txn_date_time, i.customer_id, i.policy_number,
       i.insurance_type, i.premium_amount, i.claim_amount, i.claim_status,
       i.incident_severity, i.risk_segmentation, i.police_report_available,
       i.any_injury, i.authority_contacted, i.incident_state, i.incident_city,
       i.incident_hour_of_the_day, i.agent_id, e.agent_name,
       i.vendor_id, v.vendor_name
FROM insurance_data i
LEFT JOIN employee_data e ON i.agent_id = e.agent_id
LEFT JOIN vendor_data v ON i.vendor_id = v.vendor_id;

CREATE OR REPLACE VIEW vw_agent_exposure_summary AS
SELECT agent_id, COUNT(*) AS total_claims,
       ROUND(SUM(claim_amount), 2) AS total_claim_amount,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount,
       COUNT(*) FILTER (WHERE claim_amount >= 95000) AS high_value_claims
FROM insurance_data
GROUP BY agent_id;

CREATE OR REPLACE VIEW vw_vendor_exposure_summary AS
SELECT vendor_id, COUNT(*) AS total_claims,
       ROUND(SUM(claim_amount), 2) AS total_claim_amount,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount,
       COUNT(*) FILTER (WHERE claim_amount >= 95000) AS high_value_claims
FROM insurance_data
WHERE vendor_id IS NOT NULL
GROUP BY vendor_id;

CREATE OR REPLACE VIEW vw_agent_product_ranking AS
SELECT insurance_type, agent_id, COUNT(*) AS total_claims,
       ROUND(SUM(claim_amount), 2) AS total_claim_amount,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount,
       ROW_NUMBER() OVER (
           PARTITION BY insurance_type
           ORDER BY SUM(claim_amount) DESC
       ) AS product_ranking
FROM insurance_data
GROUP BY insurance_type, agent_id;

/* VALIDATION-001 — expected 10,000; actual 10,000; PASS */
SELECT COUNT(*) AS enriched_claim_records FROM vw_claims_enriched;

/* VALIDATION-002 — ranking matches BA-010; PASS */
SELECT * FROM vw_agent_exposure_summary ORDER BY total_claim_amount DESC LIMIT 10;

/* VALIDATION-003 — ranking matches BA-012; PASS */
SELECT * FROM vw_vendor_exposure_summary ORDER BY total_claim_amount DESC LIMIT 10;

/* VALIDATION-004 — pending execution */
SELECT *
FROM vw_agent_product_ranking
WHERE product_ranking <= 10
ORDER BY insurance_type, product_ranking;
