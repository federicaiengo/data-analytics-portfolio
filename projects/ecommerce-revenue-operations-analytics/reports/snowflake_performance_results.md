# Snowflake Query Performance Benchmark — Results

This document is intentionally a **measurement record**, not a performance claim.

The benchmark SQL is:

`sql/07_snowflake_performance_benchmark.sql`

## Goal

Measure the difference between:

- a baseline reporting query that re-aggregates order items and payments from staging tables on every execution;
- a read-side query against an explicitly created **temporary table** `BENCHMARK_ORDER_FINANCIAL_RECONCILIATION` populated from the dbt `INT_ORDER_FINANCIAL_RECONCILIATION` **view**. The dbt project's intermediate layer is configured as `view`, NOT table.

The two queries must first be shown to return logically equivalent reconciliation results. **Report the one-time table-build time, bytes scanned, and refresh requirements**. Comparing only baseline vs precomputed read is not a fair end-to-end speedup statement.

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
| Intermediate dbt materialization | view (verified in dbt_project.yml) |
| Benchmark table | session temporary table |
| Table-build elapsed / execution / bytes scanned | TODO — must include in cost discussion |
| Query order / repetitions | TODO |
| Data state / model refresh | TODO |

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
| build | temp table creation | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 1 | baseline | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 1 | optimized | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 2 | baseline | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 2 | optimized | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 3 | baseline | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 3 | optimized | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

## Summary

Do not fill this section until measurements exist.

- Median baseline elapsed time: **TODO**
- Median materialized-table read elapsed time: **TODO**
- Temp-table build elapsed time: **TODO**
- Amortized cost for N reads (including build): **TODO / N specified**
- Table refresh/maintenance overhead: **NOT MEASURED**
- Relative elapsed-time change: **TODO**
- Baseline bytes scanned: **TODO**
- Optimized bytes scanned: **TODO**
- Baseline partitions scanned: **TODO**
- Optimized partitions scanned: **TODO**

## Technical interpretation

The intended optimization is architectural rather than cosmetic: the existing dbt intermediate VIEW must be explicitly materialized into a TEMPORARY TABLE for this experiment. Reads then reuse precomputed reconciliation values. This is a controlled **what-if** experiment, not a claim that the repository's current dbt intermediate layer is a materialized table or that the optimized production pipeline already exists.

Whether this improves runtime, bytes scanned, or partition scanning on this dataset must be determined from the measurements above. No improvement should be claimed unless the benchmark demonstrates it.

## CV / interview guardrail

Until this file contains real measurements, the defensible statement is:

> Prepared a controlled Snowflake benchmark design comparing staging-layer reaggregation with an explicitly materialized temporary-table read, including logical-equivalence checks and a build-cost ledger. The benchmark has not yet been executed.

Only after real results are recorded should the portfolio or CV quantify an improvement.
