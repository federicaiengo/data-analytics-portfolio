/*
Project: Insurance Claims Analytics
File: 02_business_analysis.sql

Purpose:
Answer business-oriented questions using PostgreSQL analysis.

Expected Result:
Generate reproducible business findings, exploratory analyses and rejected hypotheses.

Status:
IN PROGRESS
*/

/* =========================================================
   BA-001 — CLAIM AMOUNT BY INSURANCE TYPE
   ========================================================= */

/*
Business Question:
Which insurance types generate the highest total and average claim amounts?

Outcome:
Promoted to BF-001.
*/

SELECT
    insurance_type,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount
FROM insurance_data
GROUP BY insurance_type
ORDER BY total_claim_amount DESC;


/* =========================================================
   BA-002 — CLAIM AMOUNT BY INCIDENT SEVERITY
   ========================================================= */

/*
Business Question:
How does incident severity influence claim amount?

Outcome:
Rejected as a standalone finding; retained as RF-001.
*/

SELECT
    incident_severity,
    COUNT(*) AS total_claims,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount,
    ROUND(MAX(claim_amount), 2) AS maximum_claim_amount,
    ROUND(MIN(claim_amount), 2) AS minimum_claim_amount
FROM insurance_data
GROUP BY incident_severity
ORDER BY average_claim_amount DESC;


/* =========================================================
   BA-003 — CLAIM STATUS IMPACT
   ========================================================= */

/*
Business Question:
How do claim amounts differ by claim status?

Outcome:
Rejected as a standalone finding; retained as RF-002.
*/

SELECT
    claim_status,
    COUNT(*) AS total_claims,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount,
    ROUND(MAX(claim_amount), 2) AS maximum_claim_amount
FROM insurance_data
GROUP BY claim_status
ORDER BY average_claim_amount DESC;


/* =========================================================
   BA-004 — CLAIM AMOUNT BY RISK SEGMENTATION
   ========================================================= */

/*
Business Question:
Does customer risk segmentation explain claim value?

Outcome:
Rejected as a standalone finding; retained as RF-003.
*/

SELECT
    risk_segmentation,
    COUNT(*) AS total_claims,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount
FROM insurance_data
GROUP BY risk_segmentation
ORDER BY average_claim_amount DESC;


/* =========================================================
   BA-005 — INSURANCE TYPE × INCIDENT SEVERITY
   ========================================================= */

/*
Business Question:
How does incident severity affect claim amounts within each insurance type?

Outcome:
Retained as exploratory support analysis EA-001.
*/

SELECT
    insurance_type,
    incident_severity,
    COUNT(*) AS total_claims,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount
FROM insurance_data
GROUP BY insurance_type, incident_severity
ORDER BY insurance_type, average_claim_amount DESC;


/* =========================================================
   BA-006 — CLAIM AMOUNT BY POLICE REPORT
   ========================================================= */

/*
Business Question:
Does police report availability correlate with claim amount?

Outcome:
Rejected as a standalone finding; retained as RF-004.
*/

SELECT
    police_report_available,
    COUNT(*) AS total_claims,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount
FROM insurance_data
GROUP BY police_report_available
ORDER BY average_claim_amount DESC;


/* =========================================================
   BA-007 — TOP 20 HIGHEST CLAIMS
   ========================================================= */

/*
Business Question:
Which claims represent the highest financial exposure?

Outcome:
Used as evidence for BF-002.
*/

SELECT
    transaction_id,
    insurance_type,
    claim_status,
    incident_severity,
    risk_segmentation,
    claim_amount
FROM insurance_data
ORDER BY claim_amount DESC
LIMIT 20;


/* =========================================================
   BA-008 — HIGH-END CLAIM AMOUNT DISTRIBUTION
   ========================================================= */

/*
Business Question:
How frequently do claim amounts occur at the upper end of the dataset?

Note:
This query does not establish the existence of a policy limit.

Outcome:
Used as evidence for BF-002.
*/

SELECT
    claim_amount,
    COUNT(*) AS occurrences
FROM insurance_data
WHERE claim_amount >= 95000
GROUP BY claim_amount
ORDER BY claim_amount DESC;


/* =========================================================
   BA-009 — HIGH-VALUE CLAIMS BY INSURANCE TYPE
   ========================================================= */

/*
Business Question:
Which insurance types generate high-value claims (>= 95,000)?

Outcome:
Promoted to BF-002 together with BA-007 and BA-008.
*/

SELECT
    insurance_type,
    COUNT(*) AS high_value_claims,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount
FROM insurance_data
WHERE claim_amount >= 95000
GROUP BY insurance_type
ORDER BY high_value_claims DESC;
