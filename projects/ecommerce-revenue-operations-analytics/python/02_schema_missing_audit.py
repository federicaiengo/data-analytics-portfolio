from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

csv_files = sorted(RAW_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in: {RAW_DIR}"
    )

audit_rows = []

print("=" * 90)
print("E-COMMERCE REVENUE & OPERATIONS ANALYTICS — SCHEMA & MISSING VALUE AUDIT")
print("=" * 90)

for file_path in csv_files:
    print(f"\nFILE: {file_path.name}")

    df = pd.read_csv(file_path)

    for column in df.columns:
        missing_count = int(df[column].isna().sum())
        non_null_count = int(df[column].notna().sum())
        unique_count = int(df[column].nunique(dropna=True))

        missing_percentage = (
            (missing_count / len(df)) * 100
            if len(df) > 0
            else 0
        )

        audit_rows.append(
            {
                "file_name": file_path.name,
                "column_name": column,
                "data_type": str(df[column].dtype),
                "row_count": len(df),
                "non_null_count": non_null_count,
                "missing_count": missing_count,
                "missing_percentage": round(missing_percentage, 2),
                "unique_count": unique_count,
            }
        )

        print(
            f"{column:<40} "
            f"dtype={str(df[column].dtype):<10} "
            f"missing={missing_count:<8} "
            f"missing_pct={missing_percentage:>6.2f}% "
            f"unique={unique_count}"
        )

audit_df = pd.DataFrame(audit_rows)

output_path = REPORTS_DIR / "02_schema_missing_audit.csv"
audit_df.to_csv(output_path, index=False)

print("\n" + "=" * 90)
print("SCHEMA & MISSING VALUE AUDIT COMPLETE")
print("=" * 90)
print(f"Saved report to: {output_path}")
