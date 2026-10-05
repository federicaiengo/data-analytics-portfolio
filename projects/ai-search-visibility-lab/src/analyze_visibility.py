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
                "source_diversity": 0.0, "retrieval_consistency": 0.0,
                "share_of_voice": 0.0, "top_domains": []}

    mentions = sum(as_bool(r.get("target_mentioned", "")) for r in rows)
    citations = sum(as_bool(r.get("target_cited", "")) for r in rows)

    domains = []
    competitor_mentions = 0
    by_query = defaultdict(list)
    for r in rows:
        domains.extend(normalize_domain(d) for d in split_pipe(r.get("cited_domains", "")) if normalize_domain(d))
        competitor_mentions += len(split_pipe(r.get("competitor_mentions", "")))
        by_query[r.get("query_id", "")].append(as_bool(r.get("target_mentioned", "")))

    source_diversity = (len(set(domains)) / len(domains)) if domains else 0.0
    consistent_queries = sum(1 for outcomes in by_query.values() if len(set(outcomes)) == 1)
    retrieval_consistency = consistent_queries / len(by_query) if by_query else 0.0
    share_of_voice = mentions / (mentions + competitor_mentions) if (mentions + competitor_mentions) else 0.0

    return {
        "observations": total,
        "mention_rate": mentions / total,
        "citation_rate": citations / total,
        "source_diversity": source_diversity,
        "retrieval_consistency": retrieval_consistency,
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
        print(f"{key}: {metrics[key]:.1%}")
    print("top_domains:", metrics["top_domains"])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python src/analyze_visibility.py <observations.csv>")
    main(sys.argv[1])
