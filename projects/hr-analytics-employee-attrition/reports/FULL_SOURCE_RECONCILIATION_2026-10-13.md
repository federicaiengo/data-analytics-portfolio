# HR Analytics — independent full-source artifact reconciliation (2026-10-13)

## Scope and status

**PASS — independent source-to-artifact reconciliation and subsequent Python end-to-end validation.** First, an isolated JavaScript audit compared the tracked CSV files against independently reproduced transformations and aggregate calculations. Subsequently, the two production Python pipelines passed [GitHub Actions full-source QA run 38336050248](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/38336050248), including all 24 unit/integration tests and byte-for-byte comparisons of generated CSV files. Neither audit validates the Excel XLSX workbook in desktop Microsoft Excel.

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

## Python pipeline regression gates — executed and PASS

- `tests/test_clean_employee_attrition.py::test_full_source_rebuild_matches_committed_clean_dataset`: run the production Python cleaner against the full tracked input, write temporary outputs, compare the generated cleaned CSV **byte for byte** with the committed reference, and assert source immutability and 1,470 / 237 invariants.
- `tests/test_dashboard_source.py::test_full_source_aggregate_rebuild_matches_committed_csv`: run the Python aggregator against all tracked records in a temporary location, compare with the committed 28-row CSV, and check category denominators.

Run from the HR project directory when a Python environment is available:

```bash
python -m unittest discover -s tests -v
```

**Actual execution evidence (2026-10-13):** Python 3.12.15 on GitHub Actions run [38336050248](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/38336050248) reported **24 tests run, OK**, including the two full-source integration tests. The cleaner reported **1,470 rows / 32 columns**, and the dashboard aggregator generated **28 group rows**. Both regenerated files were compared to their committed reference CSVs using `cmp` and passed. The workflows generated output under the runner's temporary directory, leaving the source CSV unchanged. Earlier fixture tests (13 + 9 on 2026-10-09) are historical evidence, superseded for current regression status by this 24-test run.

## Still pending

- Validate the static seven-sheet XLSX in a compatible spreadsheet application against the tracked aggregate source.
- Automate XLSX regeneration separately if the project requires it.
- Interpret observed differences with suitable confounding and generalizability caveats, without claiming proven retention interventions.
