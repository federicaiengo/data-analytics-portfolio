# SUPPORTING ANALYSES

Project: Insurance Claims Analytics – Claims Performance & Fraud Detection

---

# Purpose

This document records completed analyses that support validated Business Findings without independently producing a new actionable finding.

Supporting analyses are preserved to maintain complete analytical traceability.

---

# SA-001

## Title

Insurance Type and Incident Severity Interaction

## SQL Reference

BA-005

## Business Question

How does incident severity affect claim amounts within each insurance type?

## Result

Incident severity produces limited differences within most insurance products.

The analysis confirms that insurance type explains claim-value differences more clearly than incident severity alone.

## Decision

Supporting Analysis.

## Supports

BF-001 — Claim Severity by Insurance Type

---

# SA-002

## Title

Product-Adjusted Agent Exposure Ranking

## SQL Reference

BA-015

## Business Question

Which agents generate the highest financial exposure within each insurance product?

## Method

The query uses:

- Common Table Expression (`WITH`);
- `ROW_NUMBER()` window function;
- `PARTITION BY insurance_type`;
- product-specific agent rankings.

## Result

Agent rankings differ substantially across insurance products.

Agents ranked highest globally are not necessarily ranked highest within Health, Motor, Property, Travel or Mobile Insurance.

Life Insurance produces financial values that are materially higher than every other product, confirming that raw agent-exposure rankings are strongly influenced by product mix.

## Decision

Supporting Analysis.

## Supports

BF-003 — Agent Exposure Is Driven by Insurance Product Mix

## Business Impact

Agent performance should be compared within the same insurance product or through product-adjusted metrics.

Raw total claim amount alone is not an appropriate cross-product performance measure.

---

# Rules

Supporting analyses are never deleted.

Each supporting analysis must reference:

- its SQL Analysis ID;
- the Business Finding it supports;
- its analytical contribution.

---

# SA-003

## Title

Product-Adjusted Vendor Exposure Ranking

## SQL Reference

BA-016

## Business Question

Which vendors generate the highest financial exposure within each insurance product?

## Method

The query uses:

- Common Table Expression (`WITH`);
- `ROW_NUMBER()` window function;
- `PARTITION BY insurance_type`;
- product-specific vendor rankings.

## Result

Vendor rankings differ substantially across insurance products.

Life Insurance vendors dominate only within the Life portfolio, while different vendors lead Health, Property, Motor, Travel and Mobile Insurance.

## Decision

Supporting Analysis.

## Supports

BF-004 — Vendor Financial Exposure Is Driven by Insurance Product Mix

## Business Impact

Vendor performance should be evaluated within the same insurance product or through product-adjusted metrics.

Cross-product rankings based only on total claim amount are not appropriate.


## VIZ-002 — Financial Exposure by Insurance Type

**Status:** PASS

**Purpose:**  
Provide a recruiter- and stakeholder-friendly visualization of financial exposure across insurance products.

**Source dataset:**  
`viz_002_product_exposure.csv`

**Visualization:**  
Horizontal bar chart ranked by total claim amount, with exposure share percentages displayed as data labels.

**Key results:**
- Life: 91,478,000 total exposure — 55.23%
- Property: 41,579,000 — 25.10%
- Health: 18,254,000 — 11.02%
- Motor: 8,663,000 — 5.23%
- Travel: 4,976,000 — 3.00%
- Mobile: 688,300 — 0.42%

**Business interpretation:**  
Financial exposure is highly concentrated by insurance type. Life Insurance alone accounts for 55.23% of total claim exposure, while Life and Property together account for 80.33%.

**Tableau implementation:**  
- Horizontal bar chart
- Descending exposure ranking
- Financial exposure displayed in millions
- Exposure-share labels formatted to two decimal places
- Field headers removed for cleaner presentation
- Mobile's 0.42% label is omitted from the visible chart because of the very short bar; the underlying value remains available in the data/tooltip.

**Final chart title:**  
`Financial Exposure by Insurance Type`

**Final X-axis title:**  
`Financial Exposure (M)`

## VIZ-003 — Financial Exposure by Claim Severity

**Status:** PASS

**Purpose:**  
Show how total claim financial exposure is distributed across claim severity bands.

**Source dataset:**  
`viz_003_claim_severity_bands.csv`

**Visualization:**  
Horizontal bar chart displaying total financial exposure by claim severity band, with exposure-share percentages as data labels.

**Severity bands:**
- Low (<= 2,000)
- Medium-Low (2,001–7,000)
- Medium-High (7,001–21,000)
- High (21,001–94,999)
- Very High (>= 95,000)

**Key results:**
- Low: 2,861 claims — 2,441,300 total exposure — 1.47%
- Medium-Low: 2,170 claims — 9,875,000 — 5.96%
- Medium-High: 2,504 claims — 34,159,000 — 20.62%
- High: 2,362 claims — 109,108,000 — 65.87%
- Very High: 103 claims — 10,055,000 — 6.07%

**Business interpretation:**  
Financial exposure is strongly concentrated in the High severity band, which accounts for 65.87% of total exposure. This concentration is not driven simply by claim frequency: the High band contains fewer claims than the Low and Medium-High bands but generates substantially greater financial exposure.

The Very High band represents only 103 claims, yet contributes 6.07% of total exposure, highlighting the disproportionate financial impact of extreme individual claims.

**Tableau implementation:**
- Horizontal bar chart
- Custom semantic severity ordering
- Calculated field `Severity Order` used to preserve Low → Very High progression
- Financial exposure displayed in millions
- Exposure-share labels formatted to two decimal places
- Redundant field header removed
- Business-oriented chart and axis titles

**Final chart title:**  
`Financial Exposure by Claim Severity`

**Final X-axis title:**  
`Financial Exposure (M)`

## VIZ-004 — Top 10 Agents by Financial Exposure

**Status:** PASS

**Purpose:**  
Identify the agents associated with the highest total claim financial exposure and provide additional claim-volume context.

**Source dataset:**  
`viz_004_agent_exposure.csv`

**Visualization:**  
Horizontal bar chart ranking the Top 10 agents by total claim amount.

**Key results:**
- AGENT00807 — 528,800 total exposure — 14 claims — 0 high-value claims
- AGENT00679 — 489,000 — 13 claims — 2 high-value claims
- AGENT00771 — 422,100 — 15 claims — 0 high-value claims
- AGENT00125 — 400,400 — 10 claims — 0 high-value claims
- AGENT00789 — 392,900 — 9 claims — 1 high-value claim
- AGENT00525 — 385,900 — 15 claims — 0 high-value claims
- AGENT00319 — 375,600 — 18 claims — 0 high-value claims
- AGENT00388 — 373,800 — 17 claims — 2 high-value claims
- AGENT00439 — 370,000 — 12 claims — 1 high-value claim
- AGENT00482 — 368,000 — 11 claims — 0 high-value claims

**Business interpretation:**  
The agents with the highest aggregate financial exposure are not necessarily those associated with high-value individual claims. AGENT00807 has the highest total exposure despite having no high-value claims, while several lower-ranked agents have one or two.

This suggests that aggregate exposure can arise from claim volume and claim severity patterns rather than from extreme claims alone. Agent-level exposure should therefore be evaluated using multiple measures rather than a single high-value-claim indicator.

**Tableau implementation:**
- Horizontal bar chart
- Descending ranking by total claim amount
- Uniform bar encoding to keep financial exposure as the primary visual measure
- Total Claims and High Value Claims retained in tooltip for contextual analysis
- Financial exposure displayed in thousands
- Redundant Agent Id field header removed
- Business-oriented chart and axis titles

**Final chart title:**  
`Top 10 Agents by Financial Exposure`

**Final X-axis title:**  
`Financial Exposure`
