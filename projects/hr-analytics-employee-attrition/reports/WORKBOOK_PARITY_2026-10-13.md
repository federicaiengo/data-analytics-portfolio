# HR Analytics — static workbook-to-aggregate reconciliation (2026-10-13)

## Independent source-data inspection: PASS (not yet a Python CI result)

A read-only in-memory comparison inspected the actual committed XLSX Git blob
`2db1b794d86792fb2b12bac1d72b394eb6807d7b` and the 28-row aggregate
CSV Git blob `9df294be1e774dddfea8fbf530bde855ebc5f6e3`.

**Result: 28 of 28 distinct group rows reconciled, zero mismatches.**
Each row's displayed group label, employee count, recorded attritions and
attrition rate were compared to the aggregate CSV. The XLSX stores rates as
fractions while the CSV stores percentages rounded to four decimal places;
the accepted difference is at most 0.0000501 percentage points (rounding only).

| Evidence area | Matched source rows |
| --- | ---: |
| Overall (Dashboard KPI) | 1 |
| Overtime | 2 |
| Job roles | 9 |
| Departments | 3 |
| Job satisfaction | 4 |
| Work-life balance | 4 |
| Company tenure bands | 5 |
| **Total** | **28** |

The XLSX was inspected as an Office Open XML ZIP containing seven sheets:
Dashboard, Overtime, Job Roles, Departments, Satisfaction, Tenure and Method.
The source provenance cells on Method record the expected public raw CSV
filename, Git blob SHA `b8531237e39eccb4f3c87ee840c3dfbb6cdbce3b`,
1,470 raw employees and 35 raw columns. The earlier
[structural QA workflow run](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/38406517149)
also passed: seven-sheet package integrity, no cached error cells, 24/24
cleaning/aggregation Python tests, and both regenerated CSV checks.

## Repeatable independent gates (added after the earlier workflow run)

- `python/verify_workbook_parity.py` is a **read-only standard-library**
  command that checks every group cell and rate, the repeated Dashboard
  comparisons, and provenance against the actual raw CSV bytes.
- `tests/test_workbook_parity.py` adds eight tests, including deliberately
  corrupted in-memory count, rate, repeated KPI and SHA scenarios.
- The existing **manual-only** GitHub Actions HR QA workflow now includes
  these checks. **The new parity script and its tests were not executed by
  run 38406517149**, which predates their addition. A later manual run is
  needed before documenting a Python CI PASS.

From the project root:

```bash
python python/verify_workbook_parity.py
python -m unittest discover -s tests -v
```

## Optional template-based workbook rebuild (experimental)

A standalone [artifact_tool-based refresher](../python/refresh_workbook_snapshot.py)
imports the committed workbook as a *template*, computes 28 group aggregates
from the tracked raw CSV in memory, refuses inconsistent aggregate CSV inputs,
updates all group tables plus their Dashboard mirrors and provenance metadata,
and exports to a **new XLSX path**. The original workbook and CSV sources are
never overwritten. The output is checked again by the read-only parity gate.

From the HR project root, **in an environment with `artifact_tool` installed**:

```bash
python python/refresh_workbook_snapshot.py --output /tmp/HR_Attrition_Rebuilt.xlsx
```

**Verification status:** importing, editing, and exporting a seven-sheet
synthetic workbook was smoke-tested with `artifact_tool`. The whole refresher
has **NOT** yet been run on the real committed XLSX; therefore an actual
regenerated XLSX is not yet a verified deliverable. Template-based import/export
may alter workbook styling or Excel-specific features, so a visual and
desktop-Excel check is required before replacing the original. This tool is
optional; it is not invoked by the manual CI workflow.

## Limits and next work

This comparison examines the committed **static workbook**, not the result
of regenerating XLSX output from the raw source. The XLSX is not automatically
regenerated, and Microsoft Excel desktop rendering/compatibility has not been
independently validated. The independent audit cannot establish causal
relationships in this public educational HR dataset. No workbook cells or
website styling were modified during this audit.
