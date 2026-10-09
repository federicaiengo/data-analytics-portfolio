# Cleaning Protocol — implemented source audit, v1

## Purpose and source
The immutable original [IBM educational HR CSV](../raw/WA_Fn-UseC_-HR-Employee-Attrition.csv) is the source for the reproducible [cleaned 32-column CSV](employee_attrition_clean.csv). This is a descriptive portfolio exercise, not a live employer dataset or an experiment. Avoid treating group differences as causal.

## Decision log (2026-10-09)
The original full file was independently scanned before publishing the cleaned copy.

| Decision | Evidence | Action | Impact |
| --- | --- | --- | --- |
| Preserve employee rows | 1,470 complete, unique employee IDs; 0 duplicate full rows | Keep all rows in original order | 1,470 → 1,470 |
| Missing values | 0 blank/NULL values across 35 fields | **No imputation** | No fabricated values |
| Constant `EmployeeCount` | `1` in every row | Remove from cleaned copy only | One uninformative field removed |
| Constant `Over18` | `Y` in every row | Remove from cleaned copy only | One uninformative field removed |
| Constant `StandardHours` | `80` in every row | Remove from cleaned copy only | One uninformative field removed |
| Categories and numeric bounds | No observed failures against documented checks | Preserve all other values without recoding | 32 retained fields |
| Tenure consistency | Zero failures in four inequalities listed below | No row deletions or corrections | Analysis cohort unchanged |
| Attrition labels | `Yes=237`, `No=1,233` | Keep original values | Observed rate = 16.1224% |

The implemented Python checker [`clean_employee_attrition.py`](../../python/clean_employee_attrition.py) makes these rules executable. The [data-quality log](DATA_QUALITY_LOG.md) lists every completed audit and evidence source.

## Four explicit consistency tests
- `YearsAtCompany <= TotalWorkingYears`
- `YearsInCurrentRole <= YearsAtCompany`
- `YearsWithCurrManager <= YearsAtCompany`
- `YearsSinceLastPromotion <= YearsAtCompany`

**Zero observed violations** do not establish the absence of all imaginable consistency defects.

## Rebuild (project root)
```bash
python python/clean_employee_attrition.py
python -m unittest discover tests -v
```

The script writes `data/clean/employee_attrition_clean.csv` and `data/clean/source_quality_report.json` after full validation. It never changes `data/raw/`. The JSON report is **not yet part of the repository** because that Python run still needs independent runtime verification.

The cleaned CSV was separately produced by a full-source programmatic projection applying the documented rules, committed to GitHub, and read back byte for byte. **13 new unit tests are committed but not yet run**; they cannot be reported as passing.

## Constraints
- Exact 35-column original schema is required; unexpected source changes block rather than silently change the cohort.
- Empty/invalid categories, duplicate employee IDs, non-integer/range violations and impossible tenure relations fail validation.
- Do not interpret missingness-free sample data as proof of realistic data quality in actual workforce systems.
- Cleaning and SQL analytics are separate; the existing SQL queries may still read the unchanged raw-backed `employee_attrition` table until the analyst explicitly loads the clean CSV.
