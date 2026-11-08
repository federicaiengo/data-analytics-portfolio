# CSV Data Quality Audit — Read-only Python mini-project

**Scope:** independent portfolio demonstration, using explicitly synthetic customer records. Not a client engagement, production data-cleaning service or claim about real customer data.

A small, dependency-free audit for Excel-exported CSV files. It answers a practical question: *before someone uses a spreadsheet for reporting or a data import, what should be reviewed rather than silently accepted?*

## What it checks

- Duplicate nonempty business keys after **outer whitespace trimming** and **case-folded comparison** (the source is never changed).
- Missing keys and missing values in explicitly configured required columns.
- Basic email **shape only** (not existence, deliverability or consent).
- Real Gregorian dates in the strict `YYYY-MM-DD` format.
- Incorrect numbers of fields in CSV rows and surrounding whitespace in cells.
- Missing/ambiguous headers and malformed CSV quoting fail closed rather than producing a misleading partial report.

Each reported count can overlap with another (a row can have multiple issues); **issue observations are not unique affected records**.

## Run the fictional example

Requires Python 3.11–3.13; no third-party packages and no network access.

```powershell
python projects/csv-data-quality-audit/src/audit_csv.py --input projects/csv-data-quality-audit/demo/synthetic_customers.csv --report quality-report.json --key customer_id --required customer_id,email,signup_date --email-column email --date-column signup_date
```

The resulting JSON report records aggregate counts and validation configuration, with **no raw CSV values or identifying row data**. The input is never overwritten. When used on files containing real information, keep both input and report outside public Git repositories and do not paste raw data into public issues.

### Expected fictional-demo observations

| Check | Count |
|---|---:|
| CSV rows read | 6 |
| Rows with correct column count | 5 |
| Distinct nonempty keys | 3 |
| Duplicate keys | 1 |
| Missing key | 1 |
| Missing required values | 2 (one key, one email) |
| Invalid email shape | 1 |
| Invalid ISO date | 1 |
| Wrong number of columns | 1 |
| Cells with outer whitespace | 1 |
| Total overlapping issue observations | 8 |

These are deterministic expectations for invented records, **not measurements from a client's file**.

## Regression tests

```powershell
python -m unittest discover -s projects/csv-data-quality-audit/tests -v
```

Negative cases cover duplicate/ambiguous headers, invalid dates, row-width errors, malformed quoting, source immutability, data minimization and atomic report output. A dedicated CI workflow runs **only on the assigned Windows home self-hosted runner**, never a GitHub-hosted runner and never from an untrusted pull request.

### Exit codes

- `0`: audit completed. Issues may still exist; inspect the JSON report.
- `1`: unreadable/invalid input or report-writing error.
- `2`: with `--fail-on-issues`, audit completed and found issues (JSON report still produced).

## Limits and safe use

This is an **audit**, not an automatic cleaner or an ETL pipeline. Missing values are not invented; duplicates are only flagged; no row is deleted. Date and email checks are syntactic. Business-level validity, international email rules, cross-file joins, schema evolution, volume/performance limits, handling of sensitive information and manual remediation decisions require separate review. Files stay local unless their owner explicitly authorizes sharing.

**Technical focus:** CSV parsing, deterministic validation, schema contracts, data minimization, non-destructive analysis, idempotent JSON output, unit tests and failure semantics.
