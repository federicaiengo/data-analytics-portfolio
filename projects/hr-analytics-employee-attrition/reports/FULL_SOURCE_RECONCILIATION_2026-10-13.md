# HR Analytics — independent full-source artifact reconciliation (2026-10-13)

## Scope and status

**PASS — independent source-to-artifact reconciliation.** This audit read the complete tracked CSV files from GitHub and independently reproduced the transformation and grouped calculations in an isolated JavaScript validation. It **did not execute** the repository's two Python pipeline scripts. It **did not** regenerate or inspect the Excel XLSX workbook in Microsoft Excel.

This project uses the public IBM HR educational dataset; it is **not real employer data**. Comparisons are descriptive, **not causal**.

## Exact inputs

| Artifact | Git blob SHA | Verified shape |
| --- | --- | --- |
| Original `data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv` | `b8531237e39eccb4f3c87ee840c3dfbb6cdbce3b` | 1,470 × 35 |
| Tracked `data/clean/employee_attrition_clean.csv` | `3a499d85fcfdd6dd85f50cb2661c988bacf5c848` | 1,470 × 32 |
| Tracked `excel/hr_dashboard_group_metrics.csv` | `9df294be1e774dddfea8fbf530bde855ebc5f6e3` | 28 aggregate rows |

## Checks actually performed

1. Read **every** one of the 1,470 records and 35 source fields. Checked nonblank fields, row and employee-ID uniqueness, expected categories and numeric formats.
2. Checked constants `EmployeeCount=1`, `Over18=Y`, and `StandardHours=80` throughout the source. Checked four employee-tenure inequalities.
3. Reconstructed the 32-column cleaned CSV by dropping **only** those three constants while preserving all source rows, field values and order. The independent reconstructed text matched the **tracked cleaned CSV byte for byte**.
4. Counted **237** `Attrition=Yes` records. Independently rebuilt all **28** grouped metrics for Overall, OverTime, JobRole, Department, JobSatisfaction, WorkLifeBalance and YearsAtCompanyBand, using four-decimal percentage formatting.
5. Checked every aggregate row and field against the tracked CSV. Each of the seven grouping dimensions summed to **1,470 employees and 237 attritions**. **No differences found.**

These outcomes confirm the published artifacts agree with an independently reconstructed set of calculations on the recorded source snapshot. They are **not a guarantee** that the Python implementation is correct under all inputs or that a spreadsheet workbook works in desktop Excel.

## Python pipeline regression gates — added, not yet executed

- `tests/test_clean_employee_attrition.py::test_full_source_rebuild_matches_committed_clean_dataset`: run the production Python cleaner against the full tracked input, write temporary outputs, compare the generated cleaned CSV **byte for byte** with the committed reference, and assert source immutability and 1,470 / 237 invariants.
- `tests/test_dashboard_source.py::test_full_source_aggregate_rebuild_matches_committed_csv`: run the Python aggregator against all tracked records in a temporary location, compare with the committed 28-row CSV, and check category denominators.

Run from the HR project directory when a Python environment is available:

```bash
python -m unittest discover -s tests -v
```

Do not report these new tests as **PASS** until their execution result is captured. Earlier fixture-based tests were reported as 13 cleaning tests and 9 aggregation tests passing on 2026-10-09; these are distinct from full-source Python execution.

## Still pending

- Execute the full-source Python integration tests and record their actual outcome.
- Validate the static seven-sheet XLSX in a compatible spreadsheet application against the tracked aggregate source.
- Automate XLSX regeneration separately if the project requires it.
- Interpret observed differences with suitable confounding and generalizability caveats, without claiming proven retention interventions.
