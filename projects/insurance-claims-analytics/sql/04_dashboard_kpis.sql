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

/* =========================================================
   KPI-003 — CLAIM STATUS DASHBOARD
   ========================================================= */

/*
Business Question:
How is the claims portfolio distributed across claim statuses?

Expected Result:
Provide executive KPIs by claim status.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    claim_status,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount),2) AS total_claim_amount,
    ROUND(AVG(claim_amount),2) AS average_claim_amount,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS portfolio_share_pct
FROM insurance_data
GROUP BY claim_status
ORDER BY total_claim_amount DESC;

/* =========================================================
   KPI-004 — INCIDENT SEVERITY DASHBOARD
   ========================================================= */

/*
Business Question:
How is financial exposure distributed across incident severity?

Expected Result:
Provide executive KPIs by incident severity.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    incident_severity,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount),2) AS total_claim_amount,
    ROUND(AVG(claim_amount),2) AS average_claim_amount,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS portfolio_share_pct
FROM insurance_data
GROUP BY incident_severity
ORDER BY total_claim_amount DESC;

/* =========================================================
   KPI-005 — RISK SEGMENTATION DASHBOARD
   ========================================================= */

/*
Business Question:
How is financial exposure distributed across customer risk segments?

Expected Result:
Provide executive KPIs by risk segment.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    risk_segmentation,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount),2) AS total_claim_amount,
    ROUND(AVG(claim_amount),2) AS average_claim_amount,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS portfolio_share_pct
FROM insurance_data
GROUP BY risk_segmentation
ORDER BY total_claim_amount DESC;

/* =========================================================
   KPI-006 — VENDOR COVERAGE BY INSURANCE TYPE
   ========================================================= */

/*
Business Question:
How frequently is a vendor assigned within each insurance product?

Expected Result:
Measure vendor assignment coverage by insurance type.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    insurance_type,
    COUNT(*) AS total_claims,
    COUNT(vendor_id) AS claims_with_vendor,
    COUNT(*) - COUNT(vendor_id) AS claims_without_vendor,
    ROUND(
        100.0 * COUNT(vendor_id) / COUNT(*),
        2
    ) AS vendor_assignment_rate_pct
FROM insurance_data
GROUP BY insurance_type
ORDER BY vendor_assignment_rate_pct DESC;

/* =========================================================
   KPI-007 — HIGH-VALUE CLAIM RATE BY INSURANCE TYPE
   ========================================================= */

/*
Business Question:
Which insurance products generate the highest proportion of
high-value claims (>= 95,000)?

Expected Result:
Measure the incidence of high-value claims by insurance product.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    insurance_type,
    COUNT(*) AS total_claims,
    COUNT(*) FILTER (
        WHERE claim_amount >= 95000
    ) AS high_value_claims,
    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE claim_amount >= 95000)
        / COUNT(*),
        2
    ) AS high_value_rate_pct
FROM insurance_data
GROUP BY insurance_type
ORDER BY high_value_rate_pct DESC;

/* =========================================================
   KPI-008 — CLAIM AMOUNT QUARTILES
   ========================================================= */

/*
Business Question:
How is the claim amount distributed across the portfolio?

Expected Result:
Calculate the main quartiles of claim amounts to support
executive reporting and future dashboards.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    MIN(claim_amount) AS minimum_claim,
    PERCENTILE_CONT(0.25)
        WITHIN GROUP (ORDER BY claim_amount) AS q1,
    PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY claim_amount) AS median,
    PERCENTILE_CONT(0.75)
        WITHIN GROUP (ORDER BY claim_amount) AS q3,
    MAX(claim_amount) AS maximum_claim
FROM insurance_data;

/* =========================================================
   KPI-009 — CLAIM AMOUNT BANDS
   ========================================================= */

/*
Business Question:
How are claims distributed across operational value bands?

Expected Result:
Create management-friendly claim amount categories for reporting
and dashboard segmentation.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    CASE
        WHEN claim_amount <= 2000 THEN 'Low (<= 2,000)'
        WHEN claim_amount <= 7000 THEN 'Medium-Low (2,001–7,000)'
        WHEN claim_amount <= 21000 THEN 'Medium-High (7,001–21,000)'
        WHEN claim_amount < 95000 THEN 'High (21,001–94,999)'
        ELSE 'Very High (>= 95,000)'
    END AS claim_amount_band,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount,
    ROUND(AVG(claim_amount), 2) AS average_claim_amount,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS portfolio_share_pct
FROM insurance_data
GROUP BY claim_amount_band
ORDER BY MIN(claim_amount);

/* =========================================================
   KPI-010 — CUMULATIVE FINANCIAL EXPOSURE BY CLAIM BAND
   ========================================================= */

/*
Business Question:
How much of the total financial exposure is generated by each
claim amount band?

Expected Result:
Measure the contribution of each operational band to the total
portfolio exposure.

Actual Result:
Pending execution.

Status:
PENDING
*/

WITH claim_bands AS (
    SELECT
        CASE
            WHEN claim_amount <= 2000 THEN 'Low (<= 2,000)'
            WHEN claim_amount <= 7000 THEN 'Medium-Low (2,001–7,000)'
            WHEN claim_amount <= 21000 THEN 'Medium-High (7,001–21,000)'
            WHEN claim_amount < 95000 THEN 'High (21,001–94,999)'
            ELSE 'Very High (>= 95,000)'
        END AS claim_amount_band,
        claim_amount
    FROM insurance_data
)
SELECT
    claim_amount_band,
    ROUND(SUM(claim_amount),2) AS total_claim_amount,
    ROUND(
        100.0 * SUM(claim_amount)
        / SUM(SUM(claim_amount)) OVER (),
        2
    ) AS financial_exposure_share_pct
FROM claim_bands
GROUP BY claim_amount_band
ORDER BY MIN(claim_amount);

/* =========================================================
   KPI-011 — CUMULATIVE PARETO ANALYSIS
   ========================================================= */

/*
Business Question:
How concentrated is financial exposure across claim amount bands?

Expected Result:
Calculate cumulative financial exposure to support Pareto analysis.

Actual Result:
Pending execution.

Status:
PENDING
*/

WITH claim_bands AS (
    SELECT
        CASE
            WHEN claim_amount <= 2000 THEN 'Low (<= 2,000)'
            WHEN claim_amount <= 7000 THEN 'Medium-Low (2,001–7,000)'
            WHEN claim_amount <= 21000 THEN 'Medium-High (7,001–21,000)'
            WHEN claim_amount < 95000 THEN 'High (21,001–94,999)'
            ELSE 'Very High (>= 95,000)'
        END AS claim_amount_band,
        claim_amount
    FROM insurance_data
),
band_summary AS (
    SELECT
        claim_amount_band,
        SUM(claim_amount) AS total_claim_amount
    FROM claim_bands
    GROUP BY claim_amount_band
)
SELECT
    claim_amount_band,
    ROUND(total_claim_amount,2) AS total_claim_amount,
    ROUND(
        100.0 * total_claim_amount /
        SUM(total_claim_amount) OVER (),
        2
    ) AS exposure_pct,
    ROUND(
        SUM(total_claim_amount) OVER (
            ORDER BY total_claim_amount DESC
        ) * 100.0 /
        SUM(total_claim_amount) OVER (),
        2
    ) AS cumulative_exposure_pct
FROM band_summary
ORDER BY total_claim_amount DESC;

/* =========================================================
   KPI-012 — EXECUTIVE PORTFOLIO RISK MATRIX
   ========================================================= */

/*
Business Question:
Which insurance products combine the highest financial exposure
with the highest concentration of high-value claims?

Expected Result:
Provide an executive risk matrix for portfolio prioritization.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    insurance_type,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount),2) AS total_claim_amount,
    COUNT(*) FILTER (
        WHERE claim_amount >= 95000
    ) AS high_value_claims,
    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE claim_amount >= 95000)
        / COUNT(*),
        2
    ) AS high_value_rate_pct,
    ROUND(
        SUM(claim_amount)
        / COUNT(*),
        2
    ) AS average_claim_amount
FROM insurance_data
GROUP BY insurance_type
ORDER BY
    total_claim_amount DESC,
    high_value_rate_pct DESC;
	
	/* =========================================================
   KPI-013 — EXECUTIVE CLAIM STATUS & PRODUCT MATRIX
   ========================================================= */

/*
Business Question:
How are claim statuses distributed within each insurance product?

Expected Result:
Support executive monitoring of operational status by product.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    insurance_type,
    claim_status,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount),2) AS total_claim_amount,
    ROUND(AVG(claim_amount),2) AS average_claim_amount
FROM insurance_data
GROUP BY
    insurance_type,
    claim_status
ORDER BY
    insurance_type,
    claim_status;
	
	/* =========================================================
   KPI-014 — TOP 10 AGENTS BY HIGH-VALUE CLAIMS
   ========================================================= */

/*
Business Question:
Which agents manage the highest number of high-value claims
(claim_amount >= 95,000)?

Expected Result:
Identify the agents requiring the greatest executive attention
for catastrophic claims.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    agent_id,
    COUNT(*) AS high_value_claims,
    ROUND(SUM(claim_amount),2) AS total_high_value_amount,
    ROUND(AVG(claim_amount),2) AS average_high_value_amount
FROM insurance_data
WHERE claim_amount >= 95000
GROUP BY agent_id
ORDER BY
    high_value_claims DESC,
    total_high_value_amount DESC
LIMIT 10;

/* =========================================================
   KPI-015 — TOP VENDORS MANAGING HIGH-VALUE CLAIMS
   ========================================================= */

/*
Business Question:
Which vendors are associated with the highest number of high-value
claims (claim_amount >= 95,000)?

Expected Result:
Identify vendors requiring executive monitoring for catastrophic claims.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    vendor_id,
    COUNT(*) AS high_value_claims,
    ROUND(SUM(claim_amount),2) AS total_high_value_amount,
    ROUND(AVG(claim_amount),2) AS average_high_value_amount
FROM insurance_data
WHERE claim_amount >= 95000
  AND vendor_id IS NOT NULL
GROUP BY vendor_id
ORDER BY
    high_value_claims DESC,
    total_high_value_amount DESC
LIMIT 10;

/* =========================================================
   KPI-016 — AGENT VS VENDOR CONCENTRATION MATRIX
   ========================================================= */

/*
Business Question:
Is catastrophic financial exposure more concentrated among agents
or among vendors?

Expected Result:
Compare the concentration of high-value claims handled by the
top agents and top vendors.

Actual Result:
Pending execution.

Status:
PENDING
*/

WITH top_agents AS (
    SELECT
        'Agent' AS entity_type,
        agent_id AS entity,
        COUNT(*) AS high_value_claims,
        SUM(claim_amount) AS total_amount
    FROM insurance_data
    WHERE claim_amount >= 95000
    GROUP BY agent_id

    UNION ALL

    SELECT
        'Vendor',
        vendor_id,
        COUNT(*),
        SUM(claim_amount)
    FROM insurance_data
    WHERE claim_amount >= 95000
      AND vendor_id IS NOT NULL
    GROUP BY vendor_id
)
SELECT
    entity_type,
    COUNT(*) AS entities,
    MAX(high_value_claims) AS max_high_value_claims,
    ROUND(AVG(high_value_claims),2) AS average_high_value_claims,
    ROUND(MAX(total_amount),2) AS maximum_financial_exposure
FROM top_agents
GROUP BY entity_type;

/* =========================================================
   KPI-017 — EXECUTIVE PORTFOLIO CONCENTRATION INDEX
   ========================================================= */

/*
Business Question:
How concentrated is financial exposure among insurance products?

Expected Result:
Measure portfolio concentration using cumulative financial exposure.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    insurance_type,
    ROUND(SUM(claim_amount),2) AS total_claim_amount,
    ROUND(
        100.0 * SUM(claim_amount)
        / SUM(SUM(claim_amount)) OVER (),
        2
    ) AS exposure_share_pct,
    ROUND(
        SUM(
            100.0 * SUM(claim_amount)
            / SUM(SUM(claim_amount)) OVER ()
        ) OVER (
            ORDER BY SUM(claim_amount) DESC
        ),
        2
    ) AS cumulative_exposure_pct
FROM insurance_data
GROUP BY insurance_type
ORDER BY total_claim_amount DESC;

/* =========================================================
   KPI-017A — EXECUTIVE PORTFOLIO CONCENTRATION INDEX
   CORRECTED VERSION
   ========================================================= */

/*
Business Question:
How concentrated is financial exposure among insurance products?

Initial Result:
FAIL — PostgreSQL does not allow nested window functions.

Corrective Action:
Calculate product exposure and portfolio shares in separate CTEs
before applying the cumulative window function.

Actual Result:
Pending execution.

Status:
PENDING
*/

WITH product_exposure AS (
    SELECT
        insurance_type,
        SUM(claim_amount) AS total_claim_amount
    FROM insurance_data
    GROUP BY insurance_type
),
exposure_shares AS (
    SELECT
        insurance_type,
        total_claim_amount,
        100.0 * total_claim_amount
            / SUM(total_claim_amount) OVER () AS exposure_share_pct
    FROM product_exposure
)
SELECT
    insurance_type,
    ROUND(total_claim_amount, 2) AS total_claim_amount,
    ROUND(exposure_share_pct, 2) AS exposure_share_pct,
    ROUND(
        SUM(exposure_share_pct) OVER (
            ORDER BY total_claim_amount DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS cumulative_exposure_pct
FROM exposure_shares
ORDER BY total_claim_amount DESC;

/* =========================================================
   KPI-018 — TOP 20 CLAIMS SHARE OF PORTFOLIO EXPOSURE
   ========================================================= */

/*
Business Question:
What percentage of total portfolio exposure is generated by the
20 highest-value claims?

Expected Result:
Measure concentration at individual-claim level.

Actual Result:
Pending execution.

Status:
PENDING
*/

WITH top_claims AS (
    SELECT
        claim_amount
    FROM insurance_data
    ORDER BY claim_amount DESC
    LIMIT 20
)
SELECT
    ROUND(SUM(claim_amount), 2) AS top_20_claim_amount,
    ROUND(
        100.0 * SUM(claim_amount)
        / (SELECT SUM(claim_amount) FROM insurance_data),
        2
    ) AS top_20_exposure_share_pct
FROM top_claims;

/* =========================================================
   KPI-019 — TOP 1% CLAIMS FINANCIAL EXPOSURE
   ========================================================= */

/*
Business Question:
How much of the total financial exposure is generated by the
top 1% highest-value claims?

Expected Result:
Measure concentration using the top 1% of the portfolio.

Actual Result:
Pending execution.

Status:
PENDING
*/

WITH ranked_claims AS (
    SELECT
        claim_amount,
        ROW_NUMBER() OVER (ORDER BY claim_amount DESC) AS rn
    FROM insurance_data
)
SELECT
    COUNT(*) AS top_claims,
    ROUND(SUM(claim_amount),2) AS total_claim_amount,
    ROUND(
        100.0 * SUM(claim_amount)
        / (SELECT SUM(claim_amount) FROM insurance_data),
        2
    ) AS exposure_share_pct
FROM ranked_claims
WHERE rn <= (
    SELECT CEIL(COUNT(*) * 0.01)
    FROM insurance_data
);

/* =========================================================
   KPI-020 — LORENZ-STYLE PORTFOLIO SUMMARY
   ========================================================= */

/*
Business Question:
How concentrated is the portfolio when comparing claim volume
with financial exposure?

Expected Result:
Provide an executive summary comparing portfolio structure.

Actual Result:
Pending execution.

Status:
PENDING
*/

WITH portfolio AS (
    SELECT
        COUNT(*) AS total_claims,
        SUM(claim_amount) AS total_amount,
        SUM(CASE WHEN claim_amount >= 95000 THEN 1 ELSE 0 END) AS high_value_claims,
        SUM(CASE WHEN claim_amount >= 95000 THEN claim_amount ELSE 0 END) AS high_value_amount
    FROM insurance_data
)
SELECT
    total_claims,
    ROUND(total_amount,2) AS total_amount,
    high_value_claims,
    ROUND(high_value_amount,2) AS high_value_amount,
    ROUND(100.0 * high_value_claims / total_claims,2) AS high_value_claim_pct,
    ROUND(100.0 * high_value_amount / total_amount,2) AS high_value_amount_pct
FROM portfolio;

/* =========================================================
   KPI-021 — CLAIM AMOUNT DISPERSION
   ========================================================= */

/*
Business Question:
How dispersed are claim amounts across the portfolio?

Expected Result:
Measure claim variability using standard deviation.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    ROUND(AVG(claim_amount),2) AS average_claim_amount,
    ROUND(STDDEV(claim_amount),2) AS standard_deviation,
    ROUND(MIN(claim_amount),2) AS minimum_claim,
    ROUND(MAX(claim_amount),2) AS maximum_claim
FROM insurance_data;

/* =========================================================
   KPI-022 — COEFFICIENT OF VARIATION
   ========================================================= */

/*
Business Question:
How variable are claim amounts relative to the portfolio average?

Expected Result:
Measure portfolio variability using the coefficient of variation.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    ROUND(AVG(claim_amount),2) AS average_claim_amount,
    ROUND(STDDEV(claim_amount),2) AS standard_deviation,
    ROUND(
        STDDEV(claim_amount)
        / AVG(claim_amount),
        4
    ) AS coefficient_of_variation
FROM insurance_data;

/* =========================================================
   KPI-023 — COEFFICIENT OF VARIATION BY INSURANCE TYPE
   ========================================================= */

/*
Business Question:
Which insurance products exhibit the greatest relative variability
in claim amounts?

Expected Result:
Compare claim volatility across insurance products.

Actual Result:
Pending execution.

Status:
PENDING
*/

SELECT
    insurance_type,
    ROUND(AVG(claim_amount),2) AS average_claim_amount,
    ROUND(STDDEV(claim_amount),2) AS standard_deviation,
    ROUND(
        STDDEV(claim_amount)
        / AVG(claim_amount),
        4
    ) AS coefficient_of_variation
FROM insurance_data
GROUP BY insurance_type
ORDER BY coefficient_of_variation DESC;

/* =========================================================
   KPI-024 — GINI PREPARATION (DECILES)
   ========================================================= */

/*
Business Question:
How concentrated is financial exposure across claim deciles?

Expected Result:
Prepare decile-level data for Lorenz Curve and Gini coefficient
visualizations in Tableau/Power BI.

Actual Result:
Pending execution.

Status:
PENDING
*/

WITH ranked_claims AS (
    SELECT
        claim_amount,
        NTILE(10) OVER (ORDER BY claim_amount) AS decile
    FROM insurance_data
)
SELECT
    decile,
    COUNT(*) AS total_claims,
    ROUND(SUM(claim_amount),2) AS total_claim_amount,
    ROUND(AVG(claim_amount),2) AS average_claim_amount,
    ROUND(
        100.0 * SUM(claim_amount)
        / SUM(SUM(claim_amount)) OVER (),
        2
    ) AS exposure_share_pct
FROM ranked_claims
GROUP BY decile
ORDER BY decile;

/* =========================================================
   KPI-025 — LORENZ CURVE DATASET
   ========================================================= */

/*
Business Question:
Prepare cumulative portfolio shares for Lorenz Curve visualization.

Expected Result:
Generate cumulative claim population and cumulative financial
exposure percentages.

Actual Result:
Pending execution.

Status:
PENDING
*/

WITH ranked_claims AS (
    SELECT
        claim_amount,
        NTILE(10) OVER (ORDER BY claim_amount) AS decile
    FROM insurance_data
),
decile_summary AS (
    SELECT
        decile,
        COUNT(*) AS total_claims,
        SUM(claim_amount) AS total_claim_amount
    FROM ranked_claims
    GROUP BY decile
)
SELECT
    decile,
    ROUND(
        SUM(total_claims) OVER (ORDER BY decile)
        * 100.0 /
        SUM(total_claims) OVER (),
        2
    ) AS cumulative_claims_pct,
    ROUND(
        SUM(total_claim_amount) OVER (ORDER BY decile)
        * 100.0 /
        SUM(total_claim_amount) OVER (),
        2
    ) AS cumulative_exposure_pct
FROM decile_summary
ORDER BY decile;

/* =========================================================
   KPI-026 — GINI COEFFICIENT
   ========================================================= */

/*
Business Question:
What is the Gini coefficient of claim amounts?

Expected Result:
Measure inequality in financial exposure.

Actual Result:
Pending execution.

Status:
PENDING
*/

WITH ranked_claims AS (
    SELECT
        claim_amount,
        ROW_NUMBER() OVER (ORDER BY claim_amount) AS rn,
        COUNT(*) OVER () AS n,
        SUM(claim_amount) OVER () AS total_amount
    FROM insurance_data
)
SELECT
    ROUND(
        (
            2 * SUM(rn * claim_amount)
            / (MAX(n) * MAX(total_amount))
        )
        - ((MAX(n) + 1.0) / MAX(n)),
        4
    ) AS gini_coefficient
FROM ranked_claims;

