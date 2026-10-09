# Measurement Protocol

## Purpose
Measure AI-search visibility reproducibly rather than relying on anecdotal screenshots.

## Observation unit
One platform/model response to one frozen query at one timestamp.

## Required fields
- run_id
- observed_at_utc
- platform
- model
- query_id
- query_text
- target_brand
- target_mentioned (0/1)
- target_cited (0/1)
- cited_urls (pipe-delimited)
- cited_domains (pipe-delimited)
- competitor_mentions (pipe-delimited)
- notes

## Protocol
1. Freeze the query set before a comparison round.
2. Record platform/model and UTC timestamp.
3. Do not silently rewrite prompts between repeated observations.
4. Preserve source URLs/domains when the platform exposes them.
5. Store observations append-only.
6. Calculate metrics from raw observations; never edit raw rows to improve results.
7. Repeat the **same query text** on the **same platform/model** and for the **same target** before estimating retrieval consistency. A single response is **not** a repeatability estimate. Report the count of eligible repeated groups and use `not measured` (null), not 0%, when none qualify.
8. Keep planned comparisons of different models, prompts or targets in separate strata unless using an explicitly justified pooled design.
9. Report missing citations and unavailable metadata explicitly.

## Interpretation
A visibility change can coincide with a content/site change without being caused by it. Platform updates, retrieval variance, personalization, geography and index freshness are potential confounders. Report correlations as correlations unless the experimental design supports a stronger claim.
