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
| Retrieval consistency | Share of repeated runs with the same target outcome |
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
├── requirements.txt
└── README.md
```

## Quick start

```bash
python src/analyze_visibility.py data/sample_observations.csv
python -m unittest discover tests
```

The included dataset is **synthetic demonstration data**, clearly labelled so that portfolio results cannot be mistaken for live platform measurements.

## Scientific / technical use case

The initial query set is designed around complex science/health-tech discovery patterns: definition, mechanism, comparison, evidence, limitations and vendor/category discovery. This makes the framework useful for technically demanding domains while remaining vendor-neutral and reusable.

## Next milestone

Add a documented real-world observation set collected under a fixed protocol, then compare repeated runs without overstating causal conclusions.
