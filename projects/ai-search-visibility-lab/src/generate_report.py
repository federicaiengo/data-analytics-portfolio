from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .analyze_visibility import calculate_metrics, load_csv
except ImportError:  # Direct CLI execution from the src/ directory.
    from analyze_visibility import calculate_metrics, load_csv

DEMO_SOURCE = Path(__file__).resolve().parents[1] / "data" / "sample_observations.csv"
KINDS = {
    "synthetic": "synthetic demonstration data",
    "observational": "operator-supplied observations; not independently verified",
}


def build_report(input_csv: str, output_json: str, *, input_kind: str | None = None) -> None:
    # Never silently label an arbitrary input file as synthetic or as observed.
    if input_kind is None:
        if Path(input_csv).resolve() != DEMO_SOURCE.resolve():
            raise ValueError(
                "Input status is unknown: specify --input-kind synthetic or observational. "
                "Neither choice establishes independent verification."
            )
        input_kind = "synthetic"
    if input_kind not in KINDS:
        raise ValueError("input_kind must be 'synthetic' or 'observational'")

    metrics = calculate_metrics(load_csv(input_csv))
    payload = {
        "dataset": Path(input_csv).name,
        "data_status": KINDS[input_kind],
        "interpretation_warning": "Correlation is not proof of causation.",
        **metrics,
    }
    target = Path(output_json)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a provenance-labelled AI visibility report.")
    parser.add_argument("input_csv")
    parser.add_argument("output_json")
    parser.add_argument("--input-kind", choices=tuple(KINDS),
                        help="Required for any dataset other than the packaged synthetic demo.")
    args = parser.parse_args()
    try:
        build_report(args.input_csv, args.output_json, input_kind=args.input_kind)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"FAIL: {exc}\n")
