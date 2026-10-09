# Data Quality Log — HR Analytics

**Dataset:** IBM HR Analytics Employee Attrition & Performance, public educational sample  
**Review date:** 2026-10-09  
**Raw source:** [WA_Fn-UseC_-HR-Employee-Attrition.csv](../raw/WA_Fn-UseC_-HR-Employee-Attrition.csv)  
**Raw Git blob:** `b8531237e39eccb4f3c87ee840c3dfbb6cdbce3b`  
**Cleaned CSV:** [employee_attrition_clean.csv](employee_attrition_clean.csv)  
**Cleaned Git blob:** `3a499d85fcfdd6dd85f50cb2661c988bacf5c848`  
**Rebuild script:** [clean_employee_attrition.py](../../python/clean_employee_attrition.py)  
**Unit tests:** [test_clean_employee_attrition.py](../../tests/test_clean_employee_attrition.py)

## Executed source-quality audit

The original tracked CSV was parsed and scanned programmatically in-session. The checks below represent **observed facts about the full 1,470-row source**, not merely SQL text or planned validation.

| ID | Check | Actual observed result | Status |
| --- | --- | --- | --- |
| DQ-001 | Row count | 1,470; unchanged in cleaned output | PASS |
| DQ-002 | Column count | 35 source; 32 output after removing 3 constant columns | PASS |
| DQ-003 | Missing/blank values | 0 | PASS |
| DQ-004 | Exact duplicate rows | 0 | PASS |
| DQ-005 | EmployeeNumber uniqueness | 1,470 distinct identifiers; 0 duplicates | PASS |
| DQ-006 | Data types | All expected numeric fields parse as canonical nonnegative integers | PASS |
| DQ-007 | Categorical consistency | 0 invalid values across predefined source categories | PASS |
| DQ-008 | Numeric ranges | 0 violations of specified age, satisfaction, education, job-level, income/rate and percentage bounds | PASS |
| DQ-009 | Constant columns | `EmployeeCount=1`, `Over18=Y`, `StandardHours=80` in every row | PASS |
| DQ-010 | Logical consistency | 0 violations in four tenure inequalities checked below | PASS |
| DQ-011 | Target distribution preserved | 237/1,470 = 16.1224% observed attrition before/after | PASS |

### Logical comparisons

- `YearsAtCompany <= TotalWorkingYears`
- `YearsInCurrentRole <= YearsAtCompany`
- `YearsWithCurrManager <= YearsAtCompany`
- `YearsSinceLastPromotion <= YearsAtCompany`

No violations were found **for these four rules**; that does not prove every potential business consistency check was implemented.

### Explicit transformation decision

| Columns | Issue found | Decision | Impact | Validation |
| --- | --- | --- | --- | --- |
| `EmployeeCount`, `Over18`, `StandardHours` | Each is constant across all 1,470 source rows | Exclude from cleaned working copy **only** | 35 → 32 columns, no rows removed | Full source distinct-value scan |
| All other 32 fields | No missingness or duplicate/invalid values in checks above | Preserve input values and row order | No encoding, recoding, missing-value imputation or outlier deletion | Full source-to-cleaned field projection and Git readback |

Sample observed ranges: `Age=18..60`; `MonthlyIncome=1,009..19,999`; `YearsAtCompany=0..40`. These are observed ranges, **not assumptions for other HR datasets**.

## Evidence and remaining checks

- The source-cleaning implementation validates complete schema, expected category sets, constants, numeric/range constraints, uniqueness and four tenure inequalities; it writes CSV plus a JSON source-profile report when executed.
- The **cleaned 32-column CSV is actually committed** and has been read back from GitHub. It was independently projected from the same full source with the above checks, not silently substituted with hypothetical output.
- The Python cleaning file and its **13 regression tests were executed locally in Python 3.13.5: 13/13 PASS**. Before execution, both local files were byte-for-byte verified against GitHub blob hashes `9619ec51f29e0030fdda97bce8f81935a90b3def` (script) and `f1240d97c0f9c748ef5926b3c48de025199758eb` (tests). The full 1,470-row dataset was independently audited in-session; the Python cleaner has **not yet been run end-to-end on that full source file**.
- The script-generated `source_quality_report.json` is **not yet committed**; its creation requires a verified Python run. This log records the separate actual in-session full-source audit.
- These validation rules do not establish representativeness, data-source licensing, non-discrimination, causal inference or future HR decisions. This dataset is for educational analysis.

## Method rule

Only mark a check PASS when its computation actually ran against the referenced data. New checks and runtime/build requirements remain **pending** until verified separately. Never overwrite the original raw CSV.
