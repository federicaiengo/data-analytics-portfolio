/*
Project: Insurance Claims Analytics
File: 02_business_analysis.sql

Purpose:
Answer business-oriented questions using PostgreSQL analysis.

Expected Result:
Generate reproducible business findings, supporting analyses and rejected hypotheses.

Status:
CURRENT
*/

/* BA-001 — CLAIM AMOUNT BY INSURANCE TYPE */
SELECT insurance_type, COUNT(*) AS total_claims,
       ROUND(SUM(claim_amount), 2) AS total_claim_amount,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount
FROM insurance_data
GROUP BY insurance_type
ORDER BY total_claim_amount DESC;

/* BA-002 — CLAIM AMOUNT BY INCIDENT SEVERITY | RF-001 */
SELECT incident_severity, COUNT(*) AS total_claims,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount,
       ROUND(MAX(claim_amount), 2) AS maximum_claim_amount,
       ROUND(MIN(claim_amount), 2) AS minimum_claim_amount
FROM insurance_data
GROUP BY incident_severity
ORDER BY average_claim_amount DESC;

/* BA-003 — CLAIM STATUS IMPACT | RF-002 */
SELECT claim_status, COUNT(*) AS total_claims,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount,
       ROUND(SUM(claim_amount), 2) AS total_claim_amount,
       ROUND(MAX(claim_amount), 2) AS maximum_claim_amount
FROM insurance_data
GROUP BY claim_status
ORDER BY average_claim_amount DESC;

/* BA-004 — CLAIM AMOUNT BY RISK SEGMENTATION | RF-003 */
SELECT risk_segmentation, COUNT(*) AS total_claims,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount,
       ROUND(SUM(claim_amount), 2) AS total_claim_amount
FROM insurance_data
GROUP BY risk_segmentation
ORDER BY average_claim_amount DESC;

/* BA-005 — INSURANCE TYPE × INCIDENT SEVERITY | SA-001 */
SELECT insurance_type, incident_severity, COUNT(*) AS total_claims,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount
FROM insurance_data
GROUP BY insurance_type, incident_severity
ORDER BY insurance_type, average_claim_amount DESC;

/* BA-006 — CLAIM AMOUNT BY POLICE REPORT | RF-004 */
SELECT police_report_available, COUNT(*) AS total_claims,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount,
       ROUND(SUM(claim_amount), 2) AS total_claim_amount
FROM insurance_data
GROUP BY police_report_available
ORDER BY average_claim_amount DESC;

/* BA-007 — TOP 20 HIGHEST CLAIMS | BF-002 SUPPORT */
SELECT transaction_id, insurance_type, claim_status, incident_severity,
       risk_segmentation, claim_amount
FROM insurance_data
ORDER BY claim_amount DESC
LIMIT 20;

/* BA-008 — HIGH-END CLAIM AMOUNT DISTRIBUTION | BF-002 SUPPORT */
SELECT claim_amount, COUNT(*) AS occurrences
FROM insurance_data
WHERE claim_amount >= 95000
GROUP BY claim_amount
ORDER BY claim_amount DESC;

/* BA-009 — HIGH-VALUE CLAIMS BY INSURANCE TYPE | BF-002 */
SELECT insurance_type, COUNT(*) AS high_value_claims,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount
FROM insurance_data
WHERE claim_amount >= 95000
GROUP BY insurance_type
ORDER BY high_value_claims DESC;

/* BA-010 — AGENT FINANCIAL EXPOSURE | BF-003 SUPPORT */
SELECT agent_id, COUNT(*) AS total_claims,
       ROUND(SUM(claim_amount), 2) AS total_claim_amount,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount
FROM insurance_data
GROUP BY agent_id
ORDER BY total_claim_amount DESC
LIMIT 20;

/* BA-011 — AGENT CLAIM PROFILE | BF-003 */
SELECT agent_id, insurance_type, COUNT(*) AS total_claims,
       ROUND(SUM(claim_amount), 2) AS total_claim_amount,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount
FROM insurance_data
WHERE agent_id IN ('AGENT00807','AGENT00679','AGENT00771','AGENT00125','AGENT00789')
GROUP BY agent_id, insurance_type
ORDER BY agent_id, total_claim_amount DESC;

/* BA-012 — VENDOR FINANCIAL EXPOSURE | BF-004 SUPPORT */
SELECT i.vendor_id, v.vendor_name, COUNT(*) AS total_claims,
       ROUND(SUM(i.claim_amount), 2) AS total_claim_amount,
       ROUND(AVG(i.claim_amount), 2) AS average_claim_amount
FROM insurance_data i
JOIN vendor_data v ON i.vendor_id = v.vendor_id
GROUP BY i.vendor_id, v.vendor_name
ORDER BY total_claim_amount DESC
LIMIT 20;

/* BA-013 — VENDOR CLAIM PROFILE | BF-004 */
SELECT i.vendor_id, v.vendor_name, i.insurance_type,
       COUNT(*) AS total_claims,
       ROUND(SUM(i.claim_amount), 2) AS total_claim_amount,
       ROUND(AVG(i.claim_amount), 2) AS average_claim_amount
FROM insurance_data i
JOIN vendor_data v ON i.vendor_id = v.vendor_id
WHERE i.vendor_id IN ('VNDR00445','VNDR00453','VNDR00031','VNDR00591','VNDR00138')
GROUP BY i.vendor_id, v.vendor_name, i.insurance_type
ORDER BY i.vendor_id, total_claim_amount DESC;

/* BA-014 — LIFE INSURANCE CONCENTRATION BY AGENT | RF-005 */
SELECT agent_id, COUNT(*) AS life_claims,
       ROUND(SUM(claim_amount), 2) AS total_life_claim_amount,
       ROUND(AVG(claim_amount), 2) AS average_life_claim_amount
FROM insurance_data
WHERE insurance_type = 'Life'
GROUP BY agent_id
ORDER BY total_life_claim_amount DESC
LIMIT 20;

/* BA-015 — TOP 10 AGENTS WITHIN EACH INSURANCE TYPE | SA-002 */
WITH ranked_agents AS (
    SELECT insurance_type, agent_id, COUNT(*) AS total_claims,
           SUM(claim_amount) AS total_claim_amount,
           AVG(claim_amount) AS average_claim_amount,
           ROW_NUMBER() OVER (PARTITION BY insurance_type ORDER BY SUM(claim_amount) DESC) AS ranking
    FROM insurance_data
    GROUP BY insurance_type, agent_id
)
SELECT insurance_type, ranking, agent_id, total_claims,
       ROUND(total_claim_amount::numeric, 2) AS total_claim_amount,
       ROUND(average_claim_amount::numeric, 2) AS average_claim_amount
FROM ranked_agents
WHERE ranking <= 10
ORDER BY insurance_type, ranking;

/* BA-016 — TOP 10 VENDORS WITHIN EACH INSURANCE TYPE | SA-003 */
WITH ranked_vendors AS (
    SELECT insurance_type, vendor_id, COUNT(*) AS total_claims,
           SUM(claim_amount) AS total_claim_amount,
           AVG(claim_amount) AS average_claim_amount,
           ROW_NUMBER() OVER (PARTITION BY insurance_type ORDER BY SUM(claim_amount) DESC) AS ranking
    FROM insurance_data
    WHERE vendor_id IS NOT NULL
    GROUP BY insurance_type, vendor_id
)
SELECT insurance_type, ranking, vendor_id, total_claims,
       ROUND(total_claim_amount::numeric, 2) AS total_claim_amount,
       ROUND(average_claim_amount::numeric, 2) AS average_claim_amount
FROM ranked_vendors
WHERE ranking <= 10
ORDER BY insurance_type, ranking;
