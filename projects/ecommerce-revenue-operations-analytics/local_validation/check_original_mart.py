"""Run the repository's original monthly reconciliation mart SQL on synthetic DuckDB data.

This intentionally tests only the mart, not its upstream dbt models.
The only dialect adaptation is Snowflake TO_CHAR(date, 'YYYY-MM') -> STRFTIME.
No credentials, network, or real data are used by this script.
"""
from pathlib import Path
import re
import duckdb

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "dbt/ecommerce_revenue_operations/models/marts/business/mart_revenue_financial_reconciliation.sql"
sql = MODEL.read_text(encoding="utf-8")
reference = "{{ ref('fct_orders') }}"
assert sql.count(reference) == 1, "Unexpected dbt dependency; review before executing"
sql = sql.replace(reference, "synthetic_fct_orders")
sql, substitutions = re.subn(
    r"to_char\(month_start_date,\s*'YYYY-MM'\)",
    "strftime(month_start_date, '%Y-%m')",
    sql,
    flags=re.IGNORECASE,
)
assert substitutions == 1, "Unexpected formatting expression; review dialect adaptation"

con = duckdb.connect(":memory:")
con.execute("""
CREATE TABLE synthetic_fct_orders (
    order_id VARCHAR,
    order_purchase_timestamp TIMESTAMP,
    order_status VARCHAR,
    item_sales_value DECIMAL(12,2),
    freight_value DECIMAL(12,2),
    item_plus_freight_value DECIMAL(12,2),
    payment_value DECIMAL(12,2),
    missing_item_summary BOOLEAN,
    missing_payment_summary BOOLEAN,
    financial_values_match BOOLEAN,
    payment_minus_item_freight_value DECIMAL(12,2)
)
""")
con.executemany(
    "INSERT INTO synthetic_fct_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    [
        ("SYN-001", "2026-01-03 10:00:00", "delivered", 90, 10, 100, 100, False, False, True, 0),
        ("SYN-002", "2026-01-15 10:00:00", "shipped", 40, 5, 45, 50, False, False, False, 5),
        ("SYN-003", "2026-01-20 10:00:00", "delivered", None, None, None, 20, True, False, None, None),
        ("SYN-004", "2026-02-02 10:00:00", "delivered", 25, 5, 30, 30, False, False, True, 0),
    ],
)
con.execute("CREATE VIEW original_mart_under_test AS " + sql)
rows = con.execute("""
SELECT year_month, order_count, delivered_order_count,
       comparable_order_count, matching_order_count, mismatching_order_count,
       mismatch_rate_pct, absolute_mismatch_value,
       average_absolute_mismatch_value, maximum_absolute_mismatch_value,
       missing_item_summary_order_count, missing_payment_summary_order_count
FROM original_mart_under_test
ORDER BY month_start_date
""").fetchall()
actual = [tuple(float(v) if isinstance(v, float) else v for v in row) for row in rows]
expected = [
    ("2026-01", 3, 2, 2, 1, 1, 50.0, 5, 5, 5, 1, 0),
    ("2026-02", 1, 1, 1, 1, 0, 0.0, 0, None, None, 0, 0),
]
assert len(actual) == len(expected), f"Month count mismatch: {actual!r}"
for month, (observed, wanted) in enumerate(zip(actual, expected), start=1):
    assert len(observed) == len(wanted)
    for column, (got, want) in enumerate(zip(observed, wanted), start=1):
        assert got == want, f"month={month} column={column}: got {got!r}, expected {want!r}"
print("PASS: original mart SQL passed synthetic monthly reconciliation assertions.")
print("Scope: one original dbt mart, one explicit dialect adaptation; upstream models untested.")
