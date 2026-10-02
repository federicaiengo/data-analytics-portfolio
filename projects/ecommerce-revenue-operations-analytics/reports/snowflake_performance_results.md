# Snowflake Query Performance Benchmark — Results

This document is intentionally a **measurement record**, not a performance claim.

The benchmark SQL is:

`sql/07_snowflake_performance_benchmark.sql`

## Goal

Measure the difference between:

- a baseline reporting query that re-aggregates order items and payments from staging tables on every execution;
- an optimized query that reuses the materialized `INT_ORDER_FINANCIAL_RECONCILIATION` model.

The two queries must first be shown to return logically equivalent reconciliation results.

## Benchmark controls

Record these before interpreting results:

| Control | Observed value |
|---|---|
| Snowflake region | TODO |
| Warehouse name | TODO |
| Warehouse size | TODO |
| Auto-suspend / auto-resume | TODO |
| Database | ECOMMERCE_ANALYTICS |
| Schema | ANALYTICS |
| `USE_CACHED_RESULT` | FALSE |
| Run date/time | TODO |

## Logical-equivalence check

Expected requirement before accepting the benchmark:

```text
differing_rows = 0
```

Observed:

```text
TODO
```

## Raw benchmark runs

Run baseline and optimized queries multiple times in alternating order where practical. Preserve the raw values instead of reporting only the best run.

| Run | Variant | total_elapsed_time ms | execution_time ms | compilation_time ms | bytes_scanned | partitions_scanned | partitions_total | rows_produced |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | baseline | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 1 | optimized | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 2 | baseline | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 2 | optimized | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 3 | baseline | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 3 | optimized | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

## Summary

Do not fill this section until measurements exist.

- Median baseline elapsed time: **TODO**
- Median optimized elapsed time: **TODO**
- Relative elapsed-time change: **TODO**
- Baseline bytes scanned: **TODO**
- Optimized bytes scanned: **TODO**
- Baseline partitions scanned: **TODO**
- Optimized partitions scanned: **TODO**

## Technical interpretation

The intended optimization is architectural rather than cosmetic: aggregation and order-level financial reconciliation are computed in the transformation layer and materialized for reuse, instead of being recomputed inside every downstream reporting query.

Whether this improves runtime, bytes scanned, or partition scanning on this dataset must be determined from the measurements above. No improvement should be claimed unless the benchmark demonstrates it.

## CV / interview guardrail

Until this file contains real measurements, the defensible statement is:

> Implemented a reproducible Snowflake query-performance benchmark comparing repeated staging-layer aggregation with reuse of a materialized reconciliation model.

Only after real results are recorded should the portfolio or CV quantify an improvement.
