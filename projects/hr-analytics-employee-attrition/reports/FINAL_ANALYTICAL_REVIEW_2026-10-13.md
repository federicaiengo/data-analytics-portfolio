# HR Employee Attrition — final analytical review (2026-10-13)

**Scope: final review of the documented observational findings and data controls.**  
**Status: analytic review complete; XLSX desktop compatibility and template-based regeneration are still unverified.**

## Evidence and reproducibility

- Public **IBM HR Analytics** educational data, one static cross-sectional sample: **1,470 employees, 237 recorded attritions** (16.12%). No actual employer interventions, follow-up outcomes or causal effects are observed.
- Tracked raw source contains **35 columns**; the cleaned working CSV has **32 columns** with 3 verified constant fields omitted and **all 1,470 records preserved**.
- Full-source source-cleaning and 28-row aggregation scripts produced CSV artifacts identical to the tracked copies.
- [Verified HR GitHub Actions run 38411506600](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/38411506600): **32/32 Python tests PASS**, read-only seven-sheet XLSX package integrity PASS; the workbook matches **28/28** distinct aggregate rows, **seven repeated Dashboard groups**, and source row/column/hash provenance. No runtime spreadsheet regeneration or desktop Excel rendering is implied.

## Highest-value descriptive results

| Comparison | Observed attritions / group | In-sample attrition rate |
| --- | ---: | ---: |
| All employees | 237 / 1,470 | **16.12%** |
| Overtime: Yes | 127 / 416 | **30.53%** |
| Overtime: No | 110 / 1,054 | **10.44%** |
| Sales Representatives | 33 / 83 | **39.76%** |
| Job satisfaction: 1 | 66 / 289 | **22.84%** |
| Job satisfaction: 4 | 52 / 459 | **11.33%** |
| Work-life balance: 1 | 25 / 80 | **31.25%** |
| Years at company: 0–1 | 75 / 215 | **34.88%** |
| Years at company: 11+ | 20 / 246 | **8.13%** |

Percentages use the stated group denominator, not the 1,470-row overall population denominator.

### Robustness check: overtime within departments

Descriptive overtime patterns remain visible within each department in this specific sample:

| Department | Overtime Yes | Overtime No |
| --- | ---: | ---: |
| Human Resources | 5 / 17 (**29.41%**) | 7 / 46 (**15.22%**) |
| Research & Development | 74 / 271 (**27.31%**) | 59 / 690 (**8.55%**) |
| Sales | 48 / 128 (**37.50%**) | 44 / 318 (**13.84%**) |

This reduces one simple explanation (the overall overtime gap arising *only* from mixing departments), but **does not control for job level, tenure, role, pay, selection or other confounders**. The smaller HR/overtime cells warrant particular caution. It does **not** establish a causal effect of overtime.

## Interpretation for a decision-maker

The strongest practical conclusion is **where to investigate**, not what treatment to implement. Prioritize questions about workload and overtime distribution, early tenure/onboarding, role-specific conditions and low satisfaction. Design follow-up analysis by department, role and seniority with adequate denominators before intervening.

If applied to a real organization, audit missing data and representativeness; distinguish voluntary vs involuntary exits and time-at-risk; define follow-up cohorts and avoid using a static attrition label as a churn hazard. Record policy change dates and comparators before claiming retention impact.

### No unsupported claims

- A cross-sectional historical sample cannot prove that overtime, low satisfaction or tenure *causes* exits.
- The difference between tenure groups does not identify a time-to-exit curve; former employees may be absent from a snapshot.
- Some correlations could reflect confounding, job composition and survivorship.
- There is **no external validity demonstration**, independent real-company data, model deployment, live monitoring, or measured retention benefit.
- The in-repository seven-sheet workbook is a static evidence artifact: row parity and OOXML integrity are CI-verified; Excel desktop rendering and fresh XLSX generation **remain pending**.

## Final review checklist

| Review item | State |
| --- | --- |
| Raw-source record and schema integrity | Verified |
| Source cleaning and aggregate CSV reproducibility | Verified (GitHub Actions) |
| Static XLSX structure and 28/28 row-level aggregate equivalence | Verified (GitHub Actions) |
| Cross-group descriptive calculations and interpretation limits | Reviewed against raw CSV |
| Microsoft Excel desktop rendering | **Not verified** |
| Automated regeneration of the styled XLSX on the real source | **Not verified** |
| Intervention outcomes and causal inference | **Not measured / out of scope** |

**Analytical review is complete.** Project closure as a fully reproducible, desktop-validated spreadsheet deliverable awaits the two remaining Excel-specific gates.
