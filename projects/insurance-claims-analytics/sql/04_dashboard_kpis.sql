/*
Project: Insurance Claims Analytics
File: 04_dashboard_kpis.sql

Purpose:
Create reusable executive KPIs for reporting and Power BI dashboards.

Status:
IN PROGRESS
*/


/* =========================================================
   KPI-001 — EXECUTIVE PORTFOLIO SUMMARY
   ========================================================= */

/*
Business Question:
Which headline KPIs should management monitor for the overall claims portfolio?

Actual Result:
- Total Claims: 10,000
- Total Claim Amount: 165,638,300.00
- Average Claim Amount: 16,563.83
- High-Value Claims: 103
- Claims Without Vendor: 3,245
- Vendor Assignment Rate: 67.55%

Status:
PASS
*/

SELECT
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount,
    COUNT(*) FILTER (
        WHERE claim_amount >= 95000
    ) AS high_value_claims,
    COUNT(*) FILTER (
        WHERE vendor_id IS NULL
    ) AS claims_without_vendor,
    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE vendor_id IS NOT NULL)
        / COUNT(*),
        2
    ) AS vendor_assignment_rate_pct
FROM insurance_data;


/* =========================================================
   KPI-002 — PORTFOLIO SUMMARY BY INSURANCE TYPE
   ========================================================= */

/*
Business Question:
How do claim volume and financial exposure differ by insurance product?

Expected Result:
Return management KPIs for each insurance type.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    insurance_type,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount,
    COUNT(*) FILTER (
        WHERE claim_amount >= 95000
    ) AS high_value_claims,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS claim_volume_share_pct,
    ROUND(
        100.0 * SUM(claim_amount) / SUM(SUM(claim_amount)) OVER (),
        2
    ) AS financial_exposure_share_pct
FROM insurance_data
GROUP BY insurance_type
ORDER BY total_claim_amount DESC;
