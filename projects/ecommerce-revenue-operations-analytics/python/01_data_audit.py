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

print("=" * 80)
print("E-COMMERCE REVENUE & OPERATIONS ANALYTICS — INITIAL DATA AUDIT")
print("=" * 80)

for file_path in csv_files:
    print(f"\nReading: {file_path.name}")

    df = pd.read_csv(file_path)

    row_count = len(df)
    column_count = len(df.columns)
    duplicate_rows = int(df.duplicated().sum())
    total_missing_values = int(df.isna().sum().sum())

    audit_rows.append(
        {
            "file_name": file_path.name,
            "rows": row_count,
            "columns": column_count,
            "duplicate_rows": duplicate_rows,
            "total_missing_values": total_missing_values,
        }
    )

    print(f"Rows: {row_count:,}")
    print(f"Columns: {column_count}")
    print(f"Duplicate rows: {duplicate_rows:,}")
    print(f"Missing values: {total_missing_values:,}")

audit_df = pd.DataFrame(audit_rows)

output_path = REPORTS_DIR / "01_data_audit_summary.csv"
audit_df.to_csv(output_path, index=False)

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
print(audit_df.to_string(index=False))
print(f"\nSaved report to: {output_path}")
