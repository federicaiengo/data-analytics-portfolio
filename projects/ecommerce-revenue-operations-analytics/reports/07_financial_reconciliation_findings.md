# Financial Reconciliation Findings

## Purpose

This analysis compares order-level payment value against the sum of item sales value and freight value after both transactional sources have been aggregated to a controlled one-row-per-order grain.

The objective is to identify reconciliation differences without introducing row multiplication from multi-item or multi-payment orders.

---

## Reconciliation Coverage

The order-level reconciliation model contains:

- 99,441 orders
- 99,441 distinct order IDs
- 98,665 orders with both item and payment summaries available
- 98,362 financially matching orders
- 303 financially mismatching orders
- 775 orders without an item summary
- 1 order without a payment summary

Among comparable orders, the mismatch rate is approximately:

**0.3071%**

---

## Mismatch Magnitude

Across the 303 mismatching orders:

- minimum absolute difference: BRL 0.02
- median absolute difference: BRL 5.90
- average absolute difference: BRL 10.79
- maximum absolute difference: BRL 182.81

The magnitude distribution shows that the phenomenon cannot be explained exclusively by trivial rounding differences.

---

## Order Status

299 of the 303 mismatches occur on delivered orders.

Breakdown:

- 260 delivered orders where payment value exceeds item value plus freight
- 39 delivered orders where payment value is lower than item value plus freight
- 2 canceled orders with positive differences
- 2 shipped orders with positive differences

Order status therefore does not explain the majority of the observed differences.

---

## Multi-Payment Assessment

The largest reconciliation differences do not require multiple payment records.

Several of the highest-value mismatch cases contain:

- one payment record
- one item
- one product
- one seller

This indicates that row multiplication or split-payment behavior is not the primary explanation for the financial differences.

---

## Credit-Card Installment Pattern

A strong monotonic relationship appears between credit-card installment count and reconciliation mismatch incidence.

For single-payment-record credit-card orders:

| Installments | Comparable Orders | Mismatches | Mismatch Rate | Payment > Item + Freight | Avg. Absolute Difference |
|---|---:|---:|---:|---:|---:|
| 1 | 23,591 | 8 | 0.034% | 25.0% | BRL 3.13 |
| 2–5 | 34,216 | 120 | 0.351% | 89.2% | BRL 4.48 |
| 6–10 | 15,348 | 113 | 0.736% | 93.8% | BRL 16.50 |
| 11+ | 325 | 24 | 7.385% | 100.0% | BRL 30.94 |

Both the incidence and the average magnitude of reconciliation differences increase substantially as installment count increases.

The direction of the difference also becomes increasingly asymmetric: higher-installment mismatches are overwhelmingly cases where payment value exceeds item sales plus freight.

---

## Analytical Finding

**Financial reconciliation discrepancies are strongly associated with higher credit-card installment counts.**

The relationship is visible in three independent dimensions:

1. mismatch incidence rises with installment count;
2. average absolute mismatch magnitude rises with installment count;
3. higher-installment mismatches increasingly have payment value greater than item value plus freight.

---

## Interpretation Constraint

The dataset establishes the statistical association but does not identify its economic cause.

The analysis therefore does not classify the difference as:

- financing interest
- payment-processing fees
- installment charges
- source-system error
- commercial adjustment

without additional source documentation or business-system evidence.

The finding should be interpreted as a reproducible reconciliation behavior associated with credit-card installment structure, not as proof of a specific charging mechanism.

---

## Modeling Decision

Payment value and item-plus-freight value should remain separate measures in the analytical model.

They should not be assumed to be interchangeable.

Reconciliation differences should remain observable rather than being silently corrected or overwritten.

---

## Status

**Confirmed analytical finding with strong empirical association.**

**Root economic cause: not identifiable from the available dataset alone.**