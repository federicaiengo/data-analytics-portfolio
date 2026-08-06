# BUSINESS FINDINGS

**Project:** Insurance Claims Analytics – Claims Performance & Fraud Detection  
**Database:** PostgreSQL 18  
**Status:** In Progress

---

# Purpose

This document records validated business findings supported by reproducible SQL analysis.

Only findings with sufficient evidence and a clear business implication are promoted here. Analyses that do not meet the acceptance criteria are preserved separately in `business_rejected_findings.md`.

---

# BF-001 — Claim Value Differs Materially by Insurance Type

## Business Question

Which insurance types generate the highest financial impact?

## SQL Reference

`BA-001`

## Finding

Claim frequency is relatively balanced across insurance types, but average claim value differs substantially.

Life Insurance produces the highest average claim amount, followed by Property and Health insurance. Mobile Insurance has the lowest average claim value.

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

A single claim-review strategy would not reflect the materially different exposure profiles across insurance products.

## Recommendation

Define insurance-type-specific review thresholds, monitoring rules and resource-allocation priorities.

## Priority

High

## Confidence

High

---

# BF-002 — High-Value Claims Are Concentrated in Life Insurance

## Business Question

Which insurance products generate the highest-value claims?

## SQL References

- `BA-007`
- `BA-008`
- `BA-009`

## Finding

All 103 claims with values greater than or equal to 95,000 belong to Life Insurance.

The average amount within this high-value group is 97,621.36.

## Evidence

| Insurance Type | High-Value Claims (>= 95,000) | Average Claim Amount |
|---|---:|---:|
| Life | 103 | 97,621.36 |

Upper-end claim distribution:

| Claim Amount | Occurrences |
|---:|---:|
| 100,000 | 18 |
| 99,000 | 27 |
| 98,000 | 11 |
| 97,000 | 12 |
| 96,000 | 15 |
| 95,000 | 20 |

## Interpretation

The dataset supports a strong concentration of high-value exposure in the Life Insurance portfolio.

The repeated upper-end amounts do not, by themselves, prove the existence of a contractual policy limit.

## Business Impact

Life Insurance represents the portfolio area with the greatest high-value claim exposure and therefore warrants enhanced financial controls and review capacity.

## Recommendation

Prioritize Life Insurance for:

- high-value claim review;
- exception monitoring;
- fraud-screening rules;
- reserve and exposure reporting.

## Priority

High

## Confidence

High

---

# Status Summary

- Validated Business Findings: 2
- Rejected Standalone Findings: 4
- Exploratory Analyses Retained: 1
---

# BF-003

## Title

Agent Financial Exposure

## Business Question

Which agents manage the highest financial exposure?

## SQL Reference

BA-010

## Status

UNDER REVIEW

## Notes

Finding pending execution and validation.
