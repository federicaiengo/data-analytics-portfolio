# Independent raw-source KPI cross-check — 2026-10-09

## Purpose
Verify documented insurance dashboard KPIs against the actual raw dataset, not merely by repeating figures from the README or Tableau screenshot.

## What was checked
Using an RFC-compatible CSV parser on the raw `data/raw/insurance_data.csv`, inspected **10,000 rows and 38 columns**, rejected **0 malformed rows**, and found **0 duplicate transaction IDs**. Recomputed aggregate claim values and `CLAIM_AMOUNT >= 95,000` high-value counts, without emitting personal-looking field values.

| KPI | Independently recomputed from source | Existing KPI report | Consistent? |
| --- | ---: | ---: | --- |
| Total claim rows | 10,000 | 10,000 | yes |
| Total claim amount (dataset units) | 165,638,300 | 165,638,300 | yes |
| Life Insurance claim rows | 1,682 | 1,682 | yes |
| Life Insurance claim value | 91,478,000 | 91,478,000 | yes |
| Claims at/above 95,000 | 103 | 103 | yes |
| High-value claims classified Life | 103 | 103 | yes |

Other category counts and values were also recomputed; they agree with `reports/KPI_REPORT.md`: Health 1,690 / 18,254,000; Property 1,692 / 41,579,000; Travel 1,670 / 4,976,000; Motor 1,574 / 8,663,000; Mobile 1,692 / 688,300.

**Provenance:** original CSV is tracked in this repository. A reproducible Python standard-library cross-check is included at `python/verify_public_kpis.py`. This verification was performed by programmatically reading the original CSV through the GitHub connection and independently aggregating it; it was **not** a new PostgreSQL or Tableau execution. Monetary units are unspecified by the source; do not assume a currency or call the sum an insured loss.

## Data-minimization caution — review required
The source CSV includes columns with names resembling personally identifying/financial information, including **CUSTOMER_NAME**, addresses, **SSN**, **ROUTING_NUMBER** and **ACCT_NUMBER**. The dataset's fictitious/synthetic nature and permission status were **not independently established in this audit**. Do not reproduce these values in dashboards, screenshots, public examples, exports or logs. If the underlying data are not demonstrably safe to redistribute, replacing tracked raw input requires a dedicated consent/provenance review and repository-history analysis; deleting from the latest commit alone may leave prior history visible.

## Limitations
- This checks a defined subset of KPI claims, not every join, view, underlying SQL query, fraud hypothesis, external dashboard screenshot or data-subject consent.
- It is not evidence of deployed production quality, economic causality or future risk prediction.
- Data privacy/distribution question remains OPEN until source rights and synthetic provenance are verified.

## Independent executable QA — continued
Added `tests/test_verify_public_kpis.py` with **eight regression tests** for the aggregate script: claim-value sum and 95,000 threshold boundary, protection against returning identifier values, duplicate/missing transaction IDs, invalid/nonfinite amounts, missing source fields and UTF-8 BOM support.

**Local verification:** Python 3.13.5 `python -m unittest discover tests -v` from the Insurance project directory, **8/8 PASS**. The test script and production script used in the isolated local run matched their actual GitHub **blob hashes**, respectively `4f813a554cd2f73612a7e209d03b5cc01fce8471` and `1bfbfeb8893b5b14af67fc836979cf7c3962cfbe`.

All test rows use obviously invented placeholders, not copied claimant identifiers. These tests establish defined behavior on synthetic edge-case fixtures; they do **not** establish dataset licensing/synthetic provenance or a fresh PostgreSQL/Tableau execution.

Run from `projects/insurance-claims-analytics/`:

```bash
python -m unittest discover tests -v
python python/verify_public_kpis.py
```

The second command requires the original raw CSV and was **not re-executed in the local Python runtime** in this block; source-based aggregate cross-check is separately documented above.
