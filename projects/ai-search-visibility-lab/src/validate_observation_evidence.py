"""Fail-closed metadata checks before scoring operator-supplied AI observations.

These checks establish internal consistency, not independent source verification.
Never place unedited answer text or personal correspondence in error messages.
"""
from __future__ import annotations

from datetime import datetime
from urllib.parse import urlsplit


def validate_observations(rows: list[dict[str, str]]) -> int:
    if not rows:
        raise ValueError("No observed responses provided; no measurements can be reported")

    required = (
        "run_id", "observed_at_utc", "platform", "model", "query_id",
        "query_text", "target_brand", "target_mentioned", "target_cited",
    )
    for line, row in enumerate(rows, start=2):
        if not isinstance(row, dict) or None in row:
            raise ValueError(f"Malformed observation CSV at line {line}")
        for field in required:
            if not str(row.get(field) or "").strip():
                raise ValueError(f"Missing required {field} at observation line {line}")

        try:
            observed = datetime.fromisoformat(str(row["observed_at_utc"]).replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"Invalid observation timestamp at line {line}") from None
        if observed.tzinfo is None or observed.utcoffset() is None or observed.utcoffset().total_seconds() != 0:
            raise ValueError(f"Observation timestamp must be UTC at line {line}")

        label = str(row["target_cited"]).strip().lower()
        if label not in {"0", "1", "true", "false", "yes", "no", "y", "n"}:
            raise ValueError(f"Invalid target_cited label at line {line}")
        urls = [value.strip() for value in str(row.get("cited_urls") or "").split("|") if value.strip()]
        if label in {"1", "true", "yes", "y"} and not urls:
            raise ValueError(f"Citation marked true without an evidence URL at line {line}")
        for url in urls:
            try:
                parsed = urlsplit(url)
                valid = parsed.scheme in {"https", "http"} and bool(parsed.hostname)
            except ValueError:
                valid = False
            if not valid:
                raise ValueError(f"Invalid citation URL at observation line {line}")
    return len(rows)
