# BUSINESS FINDINGS

Project: Insurance Claims Analytics – Claims Performance & Fraud Detection

---

# Purpose

This document records validated business insights supported by reproducible SQL evidence.

Only findings with sufficient business relevance and analytical support are included.

---

# BF-001

## Title

Claim Severity by Insurance Type

## Business Question

Which insurance types generate the highest financial impact?

## SQL Reference

BA-001

## Finding

Claim volume is relatively balanced across insurance types, but average claim value differs substantially.

Life Insurance generates the highest average claim amount, followed by Property and Health Insurance.

Mobile Insurance generates the lowest average claim amount.

## Evidence

| Insurance Type | Average Claim Amount |
|---|---:|
| Life | 54,386.44 |
| Property | 24,573.88 |
| Health | 10,801.18 |
| Motor | 5,503.81 |
| Travel | 2,979.64 |
| Mobile | 406.80 |

## Business Impact

Insurance products have materially different financial-exposure profiles.

A single claim-monitoring threshold would not adequately reflect the risk associated with each product.

## Recommendation

Implement insurance-type-specific claim-review thresholds and monitoring strategies.

## Priority

High

## Confidence

High

---

# BF-002

## Title

High-Value Claims Concentration in Life Insurance

## Business Question

Which insurance products generate the highest-value claims?

## SQL References

- BA-007
- BA-008
- BA-009

## Finding

All claims with values greater than or equal to 95,000 belong to Life Insurance.

The dataset contains 103 Life Insurance claims above this threshold, with an average claim value of 97,621.36.

## Business Impact

Life Insurance represents the greatest high-value financial exposure within the portfolio.

These claims may require enhanced monitoring, approval controls and fraud-review procedures.

## Recommendation

Prioritise Life Insurance claims for high-value review workflows and product-specific financial controls.

## Priority

High

## Confidence

High

---

# BF-003

## Title

Agent Exposure Is Driven by Insurance Product Mix

## Business Question

Why do certain agents manage substantially greater total claim exposure than others?

## SQL References

- BA-010
- BA-011

## Finding

Agents with the highest total claim amounts are heavily exposed to Life Insurance claims.

Their ranking is not explained only by the number of claims managed.

Examples:

| Agent | Life Claim Amount | Total Claim Amount |
|---|---:|---:|
| AGENT00807 | 412,000.00 | 528,800.00 |
| AGENT00679 | 347,000.00 | 489,000.00 |
| AGENT00125 | 369,000.00 | 400,400.00 |
| AGENT00789 | 331,000.00 | 392,900.00 |
| AGENT00771 | 269,000.00 | 422,100.00 |

The product portfolio assigned to each agent materially influences total financial exposure.

## Business Impact

Agent rankings based only on total claim amount may be misleading.

Agents assigned to Life Insurance naturally manage higher-value claims than agents managing lower-value products.

Performance reviews should separate:

- claim volume;
- claim value;
- insurance product mix;
- average claim severity.

## Recommendation

Use product-adjusted agent-performance metrics rather than raw total claim amount alone.

Management dashboards should display exposure by both agent and insurance type.

## Priority

High

## Confidence

High

---

# BF-004

## Title

Vendor Financial Exposure Is Driven by Insurance Product Mix

## Business Question

Why do certain vendors manage substantially greater financial exposure than others?

## SQL References

- BA-012
- BA-013
- BA-016

## Finding

Vendors with the highest financial exposure are strongly associated with Life Insurance claims.

Higher rankings are primarily explained by the insurance products assigned to each vendor rather than by claim volume alone.

## Business Impact

Vendor comparisons based solely on total claim amount may produce misleading conclusions.

Operational reporting should distinguish between:

- claim volume;
- average claim value;
- insurance product mix;
- total financial exposure.

## Recommendation

Evaluate vendor performance using product-adjusted KPIs instead of total claim amount alone.

## Priority

High

## Confidence

High

---

# BF-005

## Title

Financial Exposure Is Highly Concentrated Across Claims

## Business Question

How concentrated is total financial exposure across the claims portfolio?

## Visual Reference

VIZ-001 — Lorenz Curve

## Finding

The Lorenz Curve shows substantial concentration of financial exposure.

Approximately 80% of claims account for only 35% of cumulative financial exposure, meaning the remaining 20% of claims account for approximately 65% of total exposure.

## Business Impact

A relatively small share of claims drives most of the portfolio's financial exposure.

Claim volume alone therefore provides an incomplete view of portfolio risk.

## Recommendation

Prioritise exposure-based monitoring and segmentation alongside claim-volume metrics.

## Priority

High

## Confidence

High

---

# BF-006

## Title

Financial Exposure Is Concentrated in Life and Property Insurance

## Business Question

Which insurance products account for the largest shares of total financial exposure?

## Visual Reference

VIZ-002 — Product Exposure

## Finding

Life Insurance represents 55.23% of total financial exposure, followed by Property at 25.10% and Health at 11.02%.

Together, these three insurance types account for approximately 91.35% of portfolio exposure.

## Business Impact

Portfolio financial risk is strongly concentrated in a small number of insurance products.

Life Insurance alone accounts for more than half of total financial exposure.

## Recommendation

Use product-specific exposure monitoring and allocate risk-review resources according to financial exposure rather than claim volume alone.

## Priority

High

## Confidence

High

---

# BF-007

## Title

High-Severity Claims Drive the Majority of Financial Exposure

## Business Question

Which claim-severity bands contribute most to total financial exposure?

## Visual Reference

VIZ-003 — Claim Severity

## Finding

Claims in the High (21,001–94,999) severity band account for 65.87% of total financial exposure.

Medium-High (7,001–21,000) claims contribute another 20.62%.

Together, these two severity bands account for 86.49% of total financial exposure.

Very High claims (>= 95,000) represent only 1.03% of all claims but contribute a further 6.07% of total exposure.

## Business Impact

Financial exposure is overwhelmingly driven by higher-severity claims rather than by claim frequency alone.

The Very High segment also represents a low-frequency but financially material tail risk.

## Recommendation

Use severity-based monitoring thresholds and enhanced review procedures for high and very-high-value claims.

## Priority

High

## Confidence

High

---

# PORTFOLIO BASELINE

The analysed portfolio contains:

- 10,000 total claims;
- 165.6M in total financial exposure;
- 16,564 average claim amount;
- 103 Very High claims;
- 1.03% of claims classified as Very High;
- 6.07% of total financial exposure generated by Very High claims.

These metrics provide the executive baseline used across the final Tableau dashboard.

---

# STATUS

Validated Findings: 7

Rejected Findings: documented separately

Supporting Analyses: documented through SQL, Business Questions and Tableau visualisations
