from __future__ import annotations
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

def as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}

def split_pipe(value: str):
    return [x.strip() for x in (value or "").split("|") if x.strip()]

def normalize_domain(value: str) -> str:
    value = value.strip().lower()
    if not value:
        return ""
    if "://" in value:
        value = urlparse(value).netloc
    return value.removeprefix("www.")

def calculate_metrics(rows):
    total = len(rows)
    if not total:
        return {"observations": 0, "mention_rate": 0.0, "citation_rate": 0.0,
                "source_diversity": 0.0, "retrieval_consistency": None, "repeated_query_groups": 0,
                "share_of_voice": 0.0, "top_domains": []}

    mentions = sum(as_bool(r.get("target_mentioned", "")) for r in rows)
    citations = sum(as_bool(r.get("target_cited", "")) for r in rows)

    domains = []
    competitor_mentions = 0
    by_query = defaultdict(list)
    for r in rows:
        # A repeated comparison must refer to the SAME target, wording and
        # model. Collapsing all models or prompt variants into one query_id
        # can turn a change in experimental conditions into "instability".
        dimensions = ("platform", "model", "query_id", "query_text", "target_brand")
        key = tuple(r.get(field, "") for field in dimensions)
        if not r.get("query_id") or not r.get("target_brand") or not r.get("query_text"):
            raise ValueError("Each observation needs query_id, query_text and target_brand")
        by_query[key].append(as_bool(r.get("target_mentioned", "")))
        domains.extend(normalize_domain(d) for d in split_pipe(r.get("cited_domains", "")) if normalize_domain(d))
        competitor_mentions += len(set(split_pipe(r.get("competitor_mentions", ""))))

    source_diversity = (len(set(domains)) / len(domains)) if domains else 0.0
    # Single observations contain no repeatability evidence. They must not be
    # counted as "100% consistent". None means NOT MEASURED, not 0% stability.
    repeated_groups = [outcomes for outcomes in by_query.values() if len(outcomes) >= 2]
    consistent_groups = sum(len(set(outcomes)) == 1 for outcomes in repeated_groups)
    retrieval_consistency = (consistent_groups / len(repeated_groups)) if repeated_groups else None
    share_of_voice = mentions / (mentions + competitor_mentions) if (mentions + competitor_mentions) else 0.0

    return {
        "observations": total,
        "mention_rate": mentions / total,
        "citation_rate": citations / total,
        "source_diversity": source_diversity,
        "retrieval_consistency": retrieval_consistency,
        "repeated_query_groups": len(repeated_groups),
        "share_of_voice": share_of_voice,
        "top_domains": Counter(domains).most_common(5),
    }

def load_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main(path):
    metrics = calculate_metrics(load_csv(path))
    print(f"Observations: {metrics['observations']}")
    for key in ("mention_rate", "citation_rate", "source_diversity", "retrieval_consistency", "share_of_voice"):
        value = metrics[key]
        print(f"{key}: {value:.1%}" if value is not None else f"{key}: not measured (no repeated comparable groups)")
    print("top_domains:", metrics["top_domains"])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python src/analyze_visibility.py <observations.csv>")
    main(sys.argv[1])
