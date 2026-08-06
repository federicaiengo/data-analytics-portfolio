# BUSINESS REJECTED FINDINGS

**Project:** Insurance Claims Analytics – Claims Performance & Fraud Detection  
**Status:** In Progress

---

# Purpose

This document preserves analyses that did not produce a sufficiently strong standalone business finding.

Rejected and exploratory analyses are retained because they:

- document the analytical process;
- prevent duplicated work;
- demonstrate critical evaluation;
- may support future multivariable analysis;
- preserve full traceability between business questions, SQL and decisions.

---

# RF-001 — Claim Amount by Incident Severity

## SQL Reference

`BA-002`

## Business Question

Does incident severity significantly influence claim amount?

## Result

| Incident Severity | Average Claim Amount |
|---|---:|
| Total Loss | 16,795.72 |
| Major Loss | 16,656.59 |
| Minor Loss | 16,231.67 |

## Decision

Rejected as a standalone business finding.

## Reason

The difference between the highest and lowest category is limited and does not support a materially different claim-management recommendation.

## Possible Future Reuse

Combine incident severity with insurance type, claim status or high-value claim flags.

---

# RF-002 — Claim Amount by Claim Status

## SQL Reference

`BA-003`

## Business Question

How do claim amounts differ by claim status?

## Result

| Claim Status | Claims | Average Claim Amount |
|---|---:|---:|
| D | 503 | 16,810.74 |
| A | 9,497 | 16,550.75 |

## Decision

Rejected as a standalone business finding.

## Reason

The average difference is approximately 1.6%, which is insufficient to support a strong business conclusion without additional operational context for the status codes.

## Possible Future Reuse

Reassess after the meaning of the status codes is documented or combine status with insurance type and claim value bands.

---

# RF-003 — Claim Amount by Risk Segmentation

## SQL Reference

`BA-004`

## Business Question

Does customer risk segmentation explain claim value?

## Result

| Risk Segment | Average Claim Amount |
|---|---:|
| High | 16,825.43 |
| Low | 16,519.32 |
| Medium | 16,519.25 |

## Decision

Rejected as a standalone business finding.

## Reason

Average claim amounts are nearly identical across risk segments. Risk segmentation alone does not explain claim value in this dataset.

## Possible Future Reuse

Combine risk segmentation with insurance type, incident severity, customer attributes or high-value claim indicators.

---

# RF-004 — Claim Amount by Police Report Availability

## SQL Reference

`BA-006`

## Business Question

Does police report availability correlate with claim amount?

## Result

| Police Report Available | Average Claim Amount |
|---|---:|
| 1 | 16,641.00 |
| 0 | 16,389.00 |

## Decision

Rejected as a standalone business finding.

## Reason

The observed difference is approximately 1.5% and does not support a meaningful standalone recommendation.

## Possible Future Reuse

Combine police-report availability with insurance type, incident severity, injury status or high-value claim flags.

---

# EA-001 — Insurance Type × Incident Severity

## SQL Reference

`BA-005`

## Business Question

How does incident severity affect claim amounts within each insurance type?

## Result

Some within-product differences were observed, particularly in Life and Property Insurance, while Health, Motor, Travel and Mobile showed limited variation.

## Decision

Retained as exploratory supporting analysis.

## Reason

The analysis adds context to RF-001 but does not yet support a standalone recommendation.

## Possible Future Reuse

Use as supporting evidence in product-specific claim severity analysis or a future dashboard.

---

# Rules

Rejected findings and exploratory analyses are never deleted.

Each record must contain:

- ID;
- SQL reference;
- business question;
- result;
- decision;
- reason;
- possible future reuse.

---

# RF-005 — Life Insurance Claim Concentration by Agent

## SQL Reference

BA-014

## Business Question

Are Life Insurance claims operationally concentrated among a small number of agents?

## Result

Top-ranking agents manage between four and six Life Insurance claims.

The distribution is relatively balanced across the leading agents.

## Decision

Rejected as a standalone business finding.

## Reason

The analysis does not demonstrate a meaningful operational concentration.

## Future Value

May be combined with geographical information, departments or workload metrics if additional data becomes available.
