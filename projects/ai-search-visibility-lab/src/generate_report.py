from __future__ import annotations
import json
import sys
from pathlib import Path
from analyze_visibility import calculate_metrics, load_csv

def build_report(input_csv: str, output_json: str) -> None:
    metrics = calculate_metrics(load_csv(input_csv))
    payload = {
        "dataset": Path(input_csv).name,
        "data_status": "synthetic demonstration data",
        "interpretation_warning": "Correlation is not proof of causation.",
        **metrics,
    }
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(output_json).write_text(json.dumps(payload, indent=2), encoding="utf-8")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python src/generate_report.py <observations.csv> <output.json>")
    build_report(sys.argv[1], sys.argv[2])
