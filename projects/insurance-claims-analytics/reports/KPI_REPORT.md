# KPI REPORT

Project: Insurance Claims Analytics – Claims Performance & Fraud Detection

---

# Purpose

This report documents executive KPIs calculated for management reporting and future Power BI development.

---

# KPI-001 — Executive Portfolio Summary

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| KPI | Value |
|---|---:|
| Total Claims | 10,000 |
| Total Claim Amount | 165,638,300.00 |
| Average Claim Amount | 16,563.83 |
| High-Value Claims | 103 |
| Claims Without Vendor | 3,245 |
| Vendor Assignment Rate | 67.55% |

## Interpretation

The portfolio contains 10,000 claims with total financial exposure of 165.64 million.

High-value claims represent a limited share of total claim volume but require dedicated monitoring because they are concentrated in Life Insurance.

Vendor assignment is present for 67.55% of claims, while 32.45% have no assigned vendor.

## Status

PASS

---

# KPI-002 — Portfolio Summary by Insurance Type

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Insurance Type | Claims | Total Claim Amount | Average Claim Amount | High-Value Claims | Claim Volume % | Financial Exposure % |
|---|---:|---:|---:|---:|---:|---:|
| Life | 1,682 | 91,478,000.00 | 54,386.44 | 103 | 16.82 | 55.23 |
| Property | 1,692 | 41,579,000.00 | 24,573.88 | 0 | 16.92 | 25.10 |
| Health | 1,690 | 18,254,000.00 | 10,801.18 | 0 | 16.90 | 11.02 |
| Motor | 1,574 | 8,663,000.00 | 5,503.81 | 0 | 15.74 | 5.23 |
| Travel | 1,670 | 4,976,000.00 | 2,979.64 | 0 | 16.70 | 3.00 |
| Mobile | 1,692 | 688,300.00 | 406.80 | 0 | 16.92 | 0.42 |

## Interpretation

Claim volume is evenly distributed across insurance products.

Financial exposure is highly concentrated in Life Insurance, which represents 55.23% of the total portfolio despite accounting for only 16.82% of all claims.

All high-value claims (≥95,000) belong to Life Insurance.

## Status

PASS

---

# KPI-003 — Claim Status Dashboard

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Claim Status | Claims | Total Claim Amount | Average Claim Amount | Portfolio Share % |
|---|---:|---:|---:|---:|
| A | 9,497 | 157,182,500.00 | 16,550.75 | 94.97 |
| D | 503 | 8,455,800.00 | 16,810.74 | 5.03 |

## Interpretation

The claims portfolio is overwhelmingly concentrated in status **A**, representing 94.97% of all claims.

Average claim amount is nearly identical between both statuses, suggesting that claim status alone does not explain financial exposure.

This confirms the conclusions previously documented in RF-002.

## Status

PASS

---

# KPI-004 — Incident Severity Dashboard

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Incident Severity | Claims | Total Claim Amount | Average Claim Amount | Portfolio Share % |
|---|---:|---:|---:|---:|
| Total Loss | 3,390 | 56,937,500.00 | 16,795.72 | 33.90 |
| Major Loss | 3,317 | 55,249,900.00 | 16,656.59 | 33.17 |
| Minor Loss | 3,293 | 53,450,900.00 | 16,231.67 | 32.93 |

## Interpretation

Claim volume and financial exposure are distributed almost uniformly across the three incident severity categories.

Average claim amounts differ only marginally, confirming that incident severity alone is not a strong predictor of financial exposure.

This supports the conclusions previously documented in RF-001.

## Status

PASS

---

# KPI-005 — Risk Segmentation Dashboard

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Risk Segment | Claims | Total Claim Amount | Average Claim Amount | Portfolio Share % |
|---|---:|---:|---:|---:|
| L | 4,395 | 72,602,400.00 | 16,519.32 | 43.95 |
| M | 4,150 | 68,554,900.00 | 16,519.25 | 41.50 |
| H | 1,455 | 24,481,000.00 | 16,825.43 | 14.55 |

## Interpretation

Claim volume is concentrated in Low and Medium risk customers.

Average claim amount is almost identical across all three segments, indicating that customer risk segmentation alone does not explain financial exposure.

This confirms the conclusions previously documented in RF-003.

## Status

PASS

---

# KPI-006 — Vendor Coverage by Insurance Type

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Insurance Type | Total Claims | Claims with Vendor | Claims without Vendor | Vendor Assignment Rate % |
|---|---:|---:|---:|---:|
| Motor | 1,574 | 1,086 | 488 | 69.00 |
| Travel | 1,670 | 1,136 | 534 | 68.02 |
| Life | 1,682 | 1,141 | 541 | 67.84 |
| Mobile | 1,692 | 1,145 | 547 | 67.67 |
| Health | 1,690 | 1,132 | 558 | 66.98 |
| Property | 1,692 | 1,115 | 577 | 65.90 |

## Interpretation

Vendor assignment is remarkably consistent across all insurance products, varying only from 65.90% to 69.00%.

This indicates that vendor allocation is a stable operational process and is not materially influenced by insurance product type.

## Status

PASS

---

# KPI-007 — High-Value Claim Rate by Insurance Type

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Insurance Type | Total Claims | High-Value Claims | High-Value Rate % |
|---|---:|---:|---:|
| Life | 1,682 | 103 | 6.12 |
| Motor | 1,574 | 0 | 0.00 |
| Mobile | 1,692 | 0 | 0.00 |
| Travel | 1,670 | 0 | 0.00 |
| Health | 1,690 | 0 | 0.00 |
| Property | 1,692 | 0 | 0.00 |

## Interpretation

All high-value claims (≥95,000) belong exclusively to the Life Insurance portfolio.

Although Life Insurance represents only 16.82% of claim volume, it accounts for 100% of high-value claims, confirming it as the primary source of catastrophic financial exposure.

## Related Findings

- BF-001
- BF-002

## Status

PASS

---

# KPI-008 — Claim Amount Quartiles

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Metric | Claim Amount |
|---|---:|
| Minimum | 100.00 |
| Q1 | 2,000.00 |
| Median | 7,000.00 |
| Q3 | 21,000.00 |
| Maximum | 100,000.00 |

## Interpretation

Half of all claims have an amount of 7,000 or less.

Seventy-five percent of claims have an amount of 21,000 or less.

The gap between Q3 and the maximum confirms a strongly right-skewed distribution with a relatively small number of very high-value claims.

## Dashboard Use

These quartiles can support:

- claim-value bands;
- box plots;
- outlier monitoring;
- high-value review thresholds.

## Status

PASS

---

# KPI-009 — Claim Amount Bands

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Claim Amount Band | Claims | Total Claim Amount | Average Claim Amount | Portfolio Share % |
|---|---:|---:|---:|---:|
| Low (<= 2,000) | 2,861 | 2,441,300.00 | 853.30 | 28.61 |
| Medium-Low (2,001–7,000) | 2,170 | 9,875,000.00 | 4,550.69 | 21.70 |
| Medium-High (7,001–21,000) | 2,504 | 34,159,000.00 | 13,641.77 | 25.04 |
| High (21,001–94,999) | 2,362 | 109,108,000.00 | 46,193.06 | 23.62 |
| Very High (>= 95,000) | 103 | 10,055,000.00 | 97,621.36 | 1.03 |

## Interpretation

Although only 1.03% of claims are classified as Very High, they represent over ten million in financial exposure.

Nearly half of the portfolio (50.31%) consists of claims worth 7,000 or less, while the High and Very High bands generate most of the financial exposure despite representing less than one quarter of total claim volume.

## Dashboard Use

These operational bands are suitable for executive dashboards, portfolio segmentation, monitoring thresholds and drill-down analyses.

## Status

PASS

---

# KPI-010 — Financial Exposure by Claim Amount Band

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Claim Amount Band | Total Claim Amount | Financial Exposure % |
|---|---:|---:|
| Low (<= 2,000) | 2,441,300.00 | 1.47 |
| Medium-Low (2,001–7,000) | 9,875,000.00 | 5.96 |
| Medium-High (7,001–21,000) | 34,159,000.00 | 20.62 |
| High (21,001–94,999) | 109,108,000.00 | 65.87 |
| Very High (>= 95,000) | 10,055,000.00 | 6.07 |

## Interpretation

Claims between 21,001 and 94,999 generate nearly two-thirds (65.87%) of the entire portfolio exposure.

Very High claims represent only 1.03% of claim volume but contribute 6.07% of total financial exposure.

Together, the High and Very High bands account for 71.94% of portfolio value despite representing only 24.65% of all claims.

## Dashboard Use

Suitable for executive portfolio composition charts, exposure monitoring and financial risk dashboards.

## Status

PASS

---

# KPI-011 — Pareto Analysis of Financial Exposure

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Claim Amount Band | Total Claim Amount | Exposure % | Cumulative Exposure % |
|---|---:|---:|---:|
| High (21,001–94,999) | 109,108,000.00 | 65.87 | 65.87 |
| Medium-High (7,001–21,000) | 34,159,000.00 | 20.62 | 86.49 |
| Very High (>=95,000) | 10,055,000.00 | 6.07 | 92.56 |
| Medium-Low (2,001–7,000) | 9,875,000.00 | 5.96 | 98.53 |
| Low (<=2,000) | 2,441,300.00 | 1.47 | 100.00 |

## Interpretation

Financial exposure follows a strong Pareto distribution.

The High claim band alone generates 65.87% of total portfolio exposure.

Adding the Medium-High band increases cumulative exposure to 86.49%.

The two lowest claim bands together contribute only 7.43% of total financial exposure.

## Dashboard Use

Suitable for Pareto charts, executive portfolio concentration analysis and strategic risk monitoring.

## Status

PASS

---

# KPI-012 — Executive Portfolio Risk Matrix

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Insurance Type | Total Claims | Total Claim Amount | High-Value Claims | High-Value Rate % | Average Claim Amount |
|---|---:|---:|---:|---:|---:|
| Life | 1,682 | 91,478,000.00 | 103 | 6.12 | 54,386.44 |
| Property | 1,692 | 41,579,000.00 | 0 | 0.00 | 24,573.88 |
| Health | 1,690 | 18,254,000.00 | 0 | 0.00 | 10,801.18 |
| Motor | 1,574 | 8,663,000.00 | 0 | 0.00 | 5,503.81 |
| Travel | 1,670 | 4,976,000.00 | 0 | 0.00 | 2,979.64 |
| Mobile | 1,692 | 688,300.00 | 0 | 0.00 | 406.80 |

## Interpretation

Life Insurance is the dominant portfolio risk driver.

It combines the highest total financial exposure, the highest average claim amount and the only occurrence of high-value claims, making it the primary business area requiring executive monitoring.

All remaining insurance products present progressively lower financial exposure and no high-value claims.

## Dashboard Use

Suitable for executive risk matrices, portfolio prioritization and strategic management reporting.

## Status

PASS

---

# KPI-013 — Executive Claim Status by Insurance Product

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Insurance Type | Status | Claims | Total Claim Amount | Average Claim Amount |
|---|---:|---:|---:|---:|
| Health | A | 1,605 | 17,347,000.00 | 10,808.10 |
| Health | D | 85 | 907,000.00 | 10,670.59 |
| Life | A | 1,605 | 86,815,000.00 | 54,090.34 |
| Life | D | 77 | 4,663,000.00 | 60,558.44 |
| Mobile | A | 1,608 | 654,500.00 | 407.03 |
| Mobile | D | 84 | 33,800.00 | 402.38 |
| Motor | A | 1,489 | 8,180,000.00 | 5,493.62 |
| Motor | D | 85 | 483,000.00 | 5,682.35 |
| Property | A | 1,608 | 39,454,000.00 | 24,536.07 |
| Property | D | 84 | 2,125,000.00 | 25,297.62 |
| Travel | A | 1,582 | 4,732,000.00 | 2,991.15 |
| Travel | D | 88 | 244,000.00 | 2,772.73 |

## Interpretation

Claim status distribution is highly consistent across all insurance products.

Status **A** accounts for the vast majority of claims regardless of insurance type.

Life Insurance remains the largest financial contributor in both statuses, confirming that portfolio exposure is driven primarily by product type rather than operational status.

## Status

PASS

---

# KPI-014 — Top Agents Managing High-Value Claims

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Agent | High-Value Claims | Total High-Value Amount | Average High-Value Amount |
|---|---:|---:|---:|
| AGENT00388 | 2 | 197,000.00 | 98,500.00 |
| AGENT00679 | 2 | 197,000.00 | 98,500.00 |
| AGENT00700 | 2 | 195,000.00 | 97,500.00 |
| AGENT00814 | 2 | 194,000.00 | 97,000.00 |
| AGENT00004 | 2 | 194,000.00 | 97,000.00 |
| AGENT00399 | 1 | 100,000.00 | 100,000.00 |
| AGENT00056 | 1 | 100,000.00 | 100,000.00 |
| AGENT00446 | 1 | 100,000.00 | 100,000.00 |
| AGENT00086 | 1 | 100,000.00 | 100,000.00 |
| AGENT00312 | 1 | 100,000.00 | 100,000.00 |

## Interpretation

High-value claims are distributed across multiple agents rather than concentrated within a single individual.

The highest-ranked agents manage only two catastrophic claims each, suggesting that operational responsibility for high-value claims is broadly distributed.

## Status

PASS

---

# KPI-015 — Top Vendors Managing High-Value Claims

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Vendor | High-Value Claims | Total High-Value Amount | Average High-Value Amount |
|---|---:|---:|---:|
| VNDR00307 | 3 | 287,000.00 | 95,666.67 |
| VNDR00456 | 2 | 197,000.00 | 98,500.00 |
| VNDR00175 | 2 | 195,000.00 | 97,500.00 |
| VNDR00508 | 2 | 195,000.00 | 97,500.00 |
| VNDR00579 | 2 | 195,000.00 | 97,500.00 |
| VNDR00453 | 2 | 192,000.00 | 96,000.00 |
| VNDR00266 | 2 | 192,000.00 | 96,000.00 |
| VNDR00150 | 1 | 100,000.00 | 100,000.00 |
| VNDR00261 | 1 | 100,000.00 | 100,000.00 |
| VNDR00117 | 1 | 100,000.00 | 100,000.00 |

## Interpretation

High-value claims are distributed across several vendors.

Vendor **VNDR00307** manages the highest number of catastrophic claims (3), while the remaining top vendors manage one or two each.

No evidence of a single vendor dominating catastrophic financial exposure was identified.

## Status

PASS

---

# KPI-016 — Agent vs Vendor Concentration Matrix

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Entity | Entities | Maximum High-Value Claims | Average High-Value Claims | Maximum Financial Exposure |
|---|---:|---:|---:|---:|
| Agent | 98 | 2 | 1.05 | 197,000.00 |
| Vendor | 59 | 3 | 1.14 | 287,000.00 |

## Interpretation

High-value claims remain broadly distributed across both operational groups.

Vendors show a slightly higher concentration than agents, with fewer entities handling catastrophic claims and a higher maximum financial exposure.

However, neither agents nor vendors exhibit a level of concentration suggesting operational dependence on a single entity.

## Status

PASS

---

# KPI-017 — Portfolio Concentration Index

## Initial Execution

Status: FAIL

## Error

```text
ERROR: window function calls cannot be nested
SQL state: 42P20

---

# KPI-017 — Portfolio Concentration Index

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Insurance Type | Total Claim Amount | Exposure Share % | Cumulative Exposure % |
|---|---:|---:|---:|
| Life | 91,478,000.00 | 55.23 | 55.23 |
| Property | 41,579,000.00 | 25.10 | 80.33 |
| Health | 18,254,000.00 | 11.02 | 91.35 |
| Motor | 8,663,000.00 | 5.23 | 96.58 |
| Travel | 4,976,000.00 | 3.00 | 99.58 |
| Mobile | 688,300.00 | 0.42 | 100.00 |

## Interpretation

Financial exposure is highly concentrated in the two largest insurance products.

Life and Property together account for 80.33% of total portfolio exposure.

Adding Health increases cumulative exposure to 91.35%.

## Dashboard Use

Suitable for cumulative exposure charts, portfolio concentration monitoring and executive prioritization.

## Status

PASS

---

# KPI-018 — Top 20 Claims Portfolio Exposure

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Metric | Value |
|---|---:|
| Total Amount (Top 20 Claims) | 1,998,000.00 |
| Portfolio Exposure Share | 1.21% |

## Interpretation

The 20 largest claims account for only 1.21% of total portfolio financial exposure.

This indicates that financial exposure is not concentrated in a handful of individual claims, but is distributed across a broader set of high-value claims.

## Dashboard Use

Suitable for executive concentration indicators, catastrophic claim monitoring and portfolio stability assessment.

## Status

PASS

---

# KPI-019 — Top 1% Claims Financial Exposure

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Metric | Value |
|---|---:|
| Top Claims (1%) | 100 |
| Total Claim Amount | 9,770,000.00 |
| Portfolio Exposure Share | 5.90% |

## Interpretation

The top 1% of claims generate 5.90% of the total portfolio financial exposure.

Although these claims are individually significant, portfolio exposure remains relatively diversified rather than being dominated by a very small number of catastrophic events.

## Dashboard Use

Suitable for portfolio concentration monitoring, executive risk reporting and catastrophic exposure tracking.

## Status

PASS

---

# KPI-020 — Executive Portfolio Summary

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Metric | Value |
|---|---:|
| Total Claims | 10,000 |
| Total Portfolio Amount | 165,638,300.00 |
| High-Value Claims | 103 |
| High-Value Claim Amount | 10,055,000.00 |
| High-Value Claims % | 1.03 |
| High-Value Exposure % | 6.07 |

## Interpretation

High-value claims represent only 1.03% of all claims but generate 6.07% of total financial exposure.

This confirms that catastrophic claims are relatively rare but contribute disproportionately to portfolio risk.

The remaining 98.97% of claims account for 93.93% of portfolio value, indicating a broadly diversified claims portfolio.

## Dashboard Use

Suitable for executive summary cards, portfolio health monitoring and strategic risk reporting.

## Status

PASS

---

# KPI-021 — Claim Amount Dispersion

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Metric | Value |
|---|---:|
| Average Claim Amount | 16,563.83 |
| Standard Deviation | 22,037.49 |
| Minimum Claim | 100.00 |
| Maximum Claim | 100,000.00 |

## Interpretation

The standard deviation exceeds the average claim amount, indicating a highly dispersed claim value distribution.

This confirms the presence of substantial variability across the portfolio, with relatively few high-value claims coexisting alongside a large number of low-value claims.

The portfolio therefore exhibits a positively skewed financial distribution, consistent with previous percentile and Pareto analyses.

## Dashboard Use

Suitable for statistical KPI cards, portfolio variability monitoring and executive risk assessment.

## Status

PASS

---

# KPI-022 — Coefficient of Variation

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Metric | Value |
|---|---:|
| Average Claim Amount | 16,563.83 |
| Standard Deviation | 22,037.49 |
| Coefficient of Variation | 1.3305 |

## Interpretation

The coefficient of variation is greater than 1, indicating that claim values are highly dispersed relative to the portfolio average.

This confirms that financial exposure is characterized by substantial variability, with claim amounts spread across a wide range of values rather than clustered around the mean.

## Dashboard Use

Suitable for executive statistical dashboards, portfolio variability monitoring and risk benchmarking.

## Status

PASS

---

# KPI-023 — Coefficient of Variation by Insurance Type

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Insurance Type | Average Claim Amount | Standard Deviation | Coefficient of Variation |
|---|---:|---:|---:|
| Health | 10,801.18 | 5,881.66 | 0.5445 |
| Motor | 5,503.81 | 2,889.52 | 0.5250 |
| Mobile | 406.80 | 201.31 | 0.4949 |
| Travel | 2,979.64 | 1,420.41 | 0.4767 |
| Life | 54,386.44 | 25,916.34 | 0.4765 |
| Property | 24,573.88 | 9,056.75 | 0.3686 |

## Interpretation

Property Insurance shows the lowest relative variability, indicating the most stable claim values.

Health and Motor exhibit the highest relative variability, while Life Insurance combines the highest average claim amount with only moderate relative dispersion.

Overall, claim variability differs across products despite similar portfolio structures.

## Dashboard Use

Suitable for product risk comparison, portfolio stability analysis and executive statistical dashboards.

## Status

PASS

---

# KPI-024 — Financial Exposure by Claim Decile

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Decile | Claims | Total Claim Amount | Average Claim Amount | Exposure Share % |
|---:|---:|---:|---:|---:|
| 1 | 1,000 | 264,800.00 | 264.80 | 0.16 |
| 2 | 1,000 | 731,500.00 | 731.50 | 0.44 |
| 3 | 1,000 | 1,862,000.00 | 1,862.00 | 1.12 |
| 4 | 1,000 | 3,585,000.00 | 3,585.00 | 2.16 |
| 5 | 1,000 | 5,656,000.00 | 5,656.00 | 3.41 |
| 6 | 1,000 | 9,364,000.00 | 9,364.00 | 5.65 |
| 7 | 1,000 | 14,675,000.00 | 14,675.00 | 8.86 |
| 8 | 1,000 | 21,845,000.00 | 21,845.00 | 13.19 |
| 9 | 1,000 | 35,261,000.00 | 35,261.00 | 21.29 |
| 10 | 1,000 | 72,394,000.00 | 72,394.00 | 43.71 |

## Interpretation

Financial exposure is highly concentrated in the highest-value claims.

The top decile alone generates 43.71% of the total portfolio value.

The top two deciles account for 65.00% of total exposure, while the lowest five deciles together contribute only 7.29%.

This distribution is well suited for Lorenz Curve and Gini coefficient visualizations.

## Dashboard Use

Suitable for Lorenz curves, inequality analysis, portfolio concentration dashboards and executive risk reporting.

## Status

PASS

---

# KPI-025 — Lorenz Curve Dataset

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Cumulative Claims % | Cumulative Financial Exposure % |
|---:|---:|
| 10.00 | 0.16 |
| 20.00 | 0.60 |
| 30.00 | 1.73 |
| 40.00 | 3.89 |
| 50.00 | 7.30 |
| 60.00 | 12.96 |
| 70.00 | 21.82 |
| 80.00 | 35.01 |
| 90.00 | 56.29 |
| 100.00 | 100.00 |

## Interpretation

The Lorenz dataset confirms a strong inequality in claim value distribution.

The lowest 50% of claims account for only 7.30% of total financial exposure.

Even after 90% of all claims are included, only 56.29% of total exposure has been accumulated.

The remaining 10% of claims generate 43.71% of the portfolio value, confirming a highly concentrated exposure profile.

## Dashboard Use

Designed for Lorenz Curve visualization, inequality analysis, executive portfolio dashboards and Gini coefficient reporting.

## Status

PASS

---

# KPI-026 — Gini Coefficient

## SQL Reference

`04_dashboard_kpis.sql`

## Results

| Metric | Value |
|---|---:|
| Gini Coefficient | 0.6303 |

## Interpretation

The portfolio exhibits a high degree of financial inequality.

A Gini coefficient of **0.6303** indicates that financial exposure is strongly concentrated among a relatively small proportion of claims.

This result is fully consistent with the Lorenz Curve, Pareto analysis and concentration indicators previously developed throughout the project.

## Dashboard Use

Suitable for executive inequality dashboards, portfolio concentration analysis and strategic risk reporting.

## Status

PASS