# HR Analytics — validated clean data

The original source in [`data/raw/`](../raw/) remains unchanged. The [cleaned 32-column CSV](employee_attrition_clean.csv) is now committed and independently verified against the 1,470-row source.

## What changed?
Only three fields that were constant for all records were removed:
`EmployeeCount=1`, `Over18=Y`, `StandardHours=80`.

All **1,470 rows**, `EmployeeNumber` keys, `Attrition` outcomes and the remaining **32 columns** are preserved in original order. No imputation, de-duplication by deletion or outlier replacement was necessary in the documented checks.

## Inspect the work
- [`employee_attrition_clean.csv`](employee_attrition_clean.csv): actual source-projected file, 1,470 × 32.
- [`CLEANING_PROTOCOL.md`](CLEANING_PROTOCOL.md): rationale, transformations and exact rebuild command.
- [`DATA_QUALITY_LOG.md`](DATA_QUALITY_LOG.md): source-wide checks, evidence and remaining limitations.
- [`python/clean_employee_attrition.py`](../../python/clean_employee_attrition.py): Python standard-library implementation.
- [`tests/test_clean_employee_attrition.py`](../../tests/test_clean_employee_attrition.py): 13 regression tests, **13/13 PASS locally** against Git-blob-verified source; the full 1,470-row Python regeneration remains unverified.

The script optionally generates `source_quality_report.json`; that file is not yet committed. Do not confuse the independently performed source audit with a verified Python end-to-end regeneration.

The broader HR project remains **in progress**: desktop compatibility of the static Excel workbook, automated workbook generation, any additional HR analyses and final QA remain separate tasks.
