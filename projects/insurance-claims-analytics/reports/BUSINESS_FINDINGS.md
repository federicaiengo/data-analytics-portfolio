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

# STATUS

Validated Findings: 4

Rejected Findings: documented separately

Supporting Analyses: documented through SQL and Business Questions
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
