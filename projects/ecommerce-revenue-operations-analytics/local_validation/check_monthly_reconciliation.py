"""Synthetic-only local check; does not connect to Snowflake or read files."""
import duckdb

con = duckdb.connect(":memory:")
con.execute("""
CREATE TABLE synthetic_orders (
  order_id VARCHAR,
  order_purchase_timestamp TIMESTAMP,
  financial_values_match BOOLEAN
)
""")
con.executemany(
    "INSERT INTO synthetic_orders VALUES (?, ?, ?)",
    [
        ("SYN-001", "2026-01-03 10:00:00", True),
        ("SYN-002", "2026-01-15 10:00:00", False),
        ("SYN-003", "2026-01-20 10:00:00", None),
        ("SYN-004", "2026-02-02 10:00:00", True),
    ],
)
rows = con.execute("""
SELECT
  CAST(DATE_TRUNC('month', order_purchase_timestamp) AS DATE) AS month_start_date,
  COUNT(*) AS order_count,
  COUNT(*) FILTER (WHERE financial_values_match IS NOT NULL) AS comparable_order_count,
  COUNT(*) FILTER (WHERE financial_values_match = FALSE) AS mismatching_order_count
FROM synthetic_orders
GROUP BY 1
ORDER BY 1
""").fetchall()
actual = [(str(month), total, comparable, mismatch)
          for month, total, comparable, mismatch in rows]
expected = [
    ("2026-01-01", 3, 2, 1),
    ("2026-02-01", 1, 1, 0),
]
assert actual == expected, f"Unexpected monthly aggregates: {actual!r}"
print("PASS: synthetic monthly reconciliation matches expected counts (2 months, 4 orders).")
print("Scope: DuckDB-only; no Snowflake execution or performance claims.")
