/*
Project: Insurance Claims Analytics
File: 04_dashboard_kpis.sql

Purpose:
Create reusable executive KPIs for reporting and Power BI dashboards.

Expected Result:
Provide management-ready portfolio metrics.

Status:
IN PROGRESS
*/


/* =========================================================
   KPI-001 — EXECUTIVE PORTFOLIO SUMMARY
   ========================================================= */

/*
Business Question:
Which headline KPIs should management monitor for the overall claims portfolio?

Expected Result:
Return one summary row.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount),2) AS total_claim_amount,
    ROUND(AVG(claim_amount),2) AS average_claim_amount,
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