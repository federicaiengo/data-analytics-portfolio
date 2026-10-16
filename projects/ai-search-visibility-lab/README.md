# AI Search Visibility Lab

**Python · GEO/AEO · AI Search Measurement · Citation Analysis · Evidence Provenance**

A reproducible portfolio project for measuring how brands and sources appear in AI-generated answers.

The goal is not to claim a secret "AI ranking factor". The lab treats AI visibility as an **experimental measurement problem**: preserve the query, platform/model, run metadata, mentions, citations and sources; repeat observations; distinguish useful correlation from demonstrated causation.

## Questions this project answers

- Is a target brand mentioned for a defined query set?
- Is it cited, merely mentioned, or absent?
- Which source domains recur across answers?
- How stable are results across repeated runs?
- How diverse are cited sources?
- How does a target compare with named competitors?
- Do changes persist strongly enough to justify further investigation?

## Metrics

| Metric | Meaning |
|---|---|
| Mention rate | Share of observations containing the target brand |
| Citation rate | Share containing at least one target citation/source |
| Source diversity | Unique cited domains / total cited domains |
| Retrieval consistency | Share of comparable query/model/target groups with at least two observations that agree; `null` if none qualify |
| Share of voice | Target mentions / mentions across tracked brands |

## Reproducibility rules

Each observation stores a run ID, timestamp, platform, model, query ID, query text, target brand, answer text or excerpt, cited URLs/domains and notes. Raw observations are immutable; derived metrics are calculated separately.

**Interpretation rule:** correlation is evidence worth investigating, not proof of causation.

## Structure

```text
ai-search-visibility-lab/
├── data/
│   └── sample_observations.csv
├── src/
│   └── analyze_visibility.py
├── methodology/
│   ├── measurement_protocol.md
│   └── query_set.csv
├── tests/
│   └── test_metrics.py
├── case_studies/
│   └── scientific_healthtech.md
├── results/
│   └── demo_metrics.json
├── requirements.txt
└── README.md
```

## Quick start

```bash
python src/analyze_visibility.py data/sample_observations.csv
python -m unittest discover tests
python src/generate_report.py data/sample_observations.csv results/demo_metrics.json
```

## Provenance-safe reports (16 October 2026)

The original demonstration command above still produces the **same checked-in demo JSON**. Its data status is synthetic because it uses this project's specific, packaged demonstration CSV. For any other input path, report generation now requires an explicit source category:

```bash
python src/generate_report.py path/to/authorized_observations.csv output.json --input-kind observational
```

The generated JSON labels such input as **operator-supplied observations; not independently verified**. The alternative `--input-kind synthetic` is only for demonstrably invented data. Merely selecting a flag does **not** verify an observation, consent, source ownership, AI model answer or associated citation. Raw answers or potentially identifying evidence should be stored privately, not committed to this public portfolio.

The four new provenance checks were executed locally against the exact GitHub source blobs on 16 October 2026 (**4/4 PASS**). They cover refusal to guess unknown input status, preservation of the existing demo report, explicitly unverified observational data and rejection of unsupported status. The earlier 9/9 CI baseline applies to its recorded release; a new full-suite CI result for these additions is not yet claimed.

The output also includes the count of eligible `repeated_query_groups` so the denominator is auditable. A single response is never evidence of consistency.

The included dataset is **synthetic demonstration data**, clearly labelled so that portfolio results cannot be mistaken for live platform measurements.

## Scientific / technical use case

The initial query set is designed around complex science/health-tech discovery patterns: definition, mechanism, comparison, evidence, limitations and vendor/category discovery. This makes the framework useful for technically demanding domains while remaining vendor-neutral and reusable.

## Recruiter quick view

- **Working code:** `src/analyze_visibility.py` and `src/generate_report.py`
- **Measurement design:** `methodology/measurement_protocol.md`
- **Scientific/health-tech reasoning:** `case_studies/scientific_healthtech.md`
- **Machine-readable output:** `results/demo_metrics.json`
- **QA:** [manual GitHub Actions validation — 9/9 tests PASS](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/38336992176); synthetic demo metrics regenerated and compared with the tracked JSON

## Input validation

Mention and citation labels must be explicit yes/no flags; missing or ambiguous values are rejected instead of silently counted as negatives. Platform, model and query identity must be specified for repeatability analysis. Negative-case and reproducibility tests **passed (9/9)** in [manual QA run 38336992176](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/38336992176) on Python 3.12. This validates the code and synthetic fixture, **not AI-platform outcomes**. The included observations remain synthetic.

## Next milestone

Add a documented real-world observation set collected under a fixed protocol, then compare repeated runs without overstating causal conclusions.
