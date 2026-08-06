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