# AI Search Visibility Lab — v1.0 closure review

**Date:** 3 November 2026  
**Disposition:** COMPLETE for the documented educational, synthetic portfolio case study  
**Code QA evidence:** [GitHub Actions run 41688614267](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/41688614267), head commit `a57eb96621df063e52eadf99e51c81326a5ac3a3` — **COMPLETED / SUCCESS**.

## Scope accepted for v1.0

Provide a reproducible, evidence-conscious **measurement toolkit** for mentions, citations, cited-domain diversity, repeated-query consistency and tracked competitor share of voice. Make its limitations explicit and demonstrate it with fabricated observations. **Do not** claim actual search rankings, a real AI-platform audit or proven SEO improvements.

## Acceptance review

| Criterion | Evidence | Verdict |
| --- | --- | --- |
| Working measurement code | `src/analyze_visibility.py` computes mention/citation rates, source diversity, repeated-query consistency, share of voice and top domains | PASS |
| Defined observation protocol | `methodology/measurement_protocol.md` and `methodology/query_set.csv` document identities, fixed prompts, timestamp, repeatability and caveats | PASS |
| Explicit evidence and provenance boundaries | `src/generate_report.py` distinguishes packaged synthetic rows from user-supplied observations; `src/validate_observation_evidence.py` rejects malformed metadata | PASS |
| Reproducible fictional example | `data/sample_observations.csv` has four **invented** rows; `results/demo_metrics.json` regenerated in CI and matched the committed baseline | PASS |
| Complete regression gate | In the cited run, the **21-method unittest suite** passed (10 metrics, 7 observation-evidence, 4 report-status); source/test compilation and analyzer CLI also passed | PASS |
| Reviewable technical reasoning | `case_studies/scientific_healthtech.md` explains query intents, domain-specific reasoning, confounding and limitations | PASS |
| Correctly scoped public description | Portfolio and project READMEs state the synthetic-only status; no empirical outcome claims | PASS |

## Reproduced synthetic report — not external performance

The packaged four-row example has: **4 observations**, mention rate **0.75**, citation rate **0.50**, source diversity **0.50**, retrieval consistency **0.50** across **2 eligible repeated-query groups**, and tracked share of voice **0.375**. These numbers describe *fictional inputs only*. They are regression fixtures, not Gossmere, a real company, a platform, an observed model, or a ranking signal. `null` retrieval consistency when no eligible repeated group exists is handled separately.

## Reproduction

Run from `projects/ai-search-visibility-lab` using Python 3.12 or a compatible Python version, without external Python dependencies:

```bash
python -m unittest discover -s tests -v
python src/analyze_visibility.py data/sample_observations.csv
python src/generate_report.py data/sample_observations.csv /tmp/ai-visibility-demo.json
```

The **active** GitHub workflow is `.github/workflows/ai-search-visibility-lab.yml` at the **repository root**; it has scoped path triggers and concurrency cancellation to limit unnecessary GitHub Actions runs. The historical workflow nested within the project folder was not an active repository-level workflow and has been removed to avoid ambiguity.

## Boundaries and post-closure change control

**Not measured:** live AI replies, real or independently verified citations, traffic, indexed pages, impressions, AI Overviews or rankings, commercial leads, lift, source authorization or client results. Metadata validation is not factual citation verification. The source taxonomy is a simplified synthetic reference; calculated metrics are only as credible as the input collection design and review.

**Not production-certified:** the toolkit is a small educational application, not a privacy/security audit, a statistical power analysis, a systematic benchmark of current AI search engines, or a causal experiment.

**Closure:** no outstanding blocker for **this v1.0 demonstration scope**. Real-model observations, larger datasets, additional statistical methods, live source validation and new cybersecurity investigations are **future separate projects/versions**, not incomplete v1.0 promises. Do not retitle old historical 9/9 and 20/20 runs as if they had been the present release.

The closure was recorded after verified CI, and the final documentation change does not alter tested source code, the demo fixture or the regression workflow.
