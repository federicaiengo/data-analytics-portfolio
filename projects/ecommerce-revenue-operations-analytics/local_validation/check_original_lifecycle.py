"""Synthetic DuckDB audit of the original dbt order-lifecycle SELECT.

The dbt config and incremental-only WHERE/Jinja block are removed under
strict guards to exercise a full-refresh SELECT without a Snowflake account.
This does NOT validate the MERGE, watermark, or dbt incremental materialization.
"""
from pathlib import Path
import re

import duckdb

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "dbt/ecommerce_revenue_operations/models/intermediate/int_orders_lifecycle.sql"


def load_full_refresh_sql():
    source = MODEL.read_text(encoding="utf-8")
    pattern = r"\A\s*\{\{\s*config\([\s\S]*?\)\s*\}\}\s*"
    source, count = re.subn(pattern, "", source, count=1)
    assert count == 1, "Unexpected dbt config format; manual review required"
    increment = r"(?ms)^\s*\{% if is_incremental\(\) %\}.*?\{% endif %\}"
    source, count = re.subn(increment, "", source, count=1)
    assert count == 1, "Unexpected dbt incremental gate; manual review required"
    marker = "{{ ref('stg_orders') }}"
    assert source.count(marker) == 1, "Unexpected staging reference"
    source = source.replace(marker, "synthetic_stg_orders")
    assert "{{" not in source and "{%" not in source and "}}" not in source and "%}" not in source, (
        "Unresolved dbt templates; manual review required"
    )
    return source


def main():
    con = duckdb.connect(":memory:")
    try:
        con.execute("""
        CREATE TABLE synthetic_stg_orders (
            order_id VARCHAR PRIMARY KEY,
            customer_id VARCHAR,
            order_status VARCHAR,
            order_purchase_timestamp TIMESTAMP,
            order_approved_at TIMESTAMP,
            order_delivered_carrier_date TIMESTAMP,
            order_delivered_customer_date TIMESTAMP,
            order_estimated_delivery_date TIMESTAMP,
            _loaded_at TIMESTAMP,
            _source_filename VARCHAR,
            _source_row_number INTEGER
        )
        """)
        def row(key, status, approved, carrier, delivered, estimated):
            return (
                key, "CUSTOMER-" + key, status, "2026-01-01 08:00:00",
                approved, carrier, delivered, estimated,
                "2026-02-01 00:00:00", "synthetic_fixture.csv", int(key[-2:]),
            )

        con.executemany(
            "INSERT INTO synthetic_stg_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                row("SYN-01", "delivered", "2026-01-01 09:00:00",
                    "2026-01-02 09:00:00", "2026-01-03 09:00:00",
                    "2026-01-04 09:00:00"),
                row("SYN-02", "delivered", "2026-01-01 07:00:00",
                    "2026-01-02 09:00:00", "2026-01-03 09:00:00",
                    "2026-01-04 09:00:00"),
                row("SYN-03", "delivered", None,
                    "2026-01-02 09:00:00", "2026-01-03 09:00:00",
                    "2026-01-04 09:00:00"),
                row("SYN-04", "shipped", "2026-01-01 09:00:00",
                    None, None, "2026-01-04 09:00:00"),
                row("SYN-05", "delivered", "2026-01-01 10:00:00",
                    "2026-01-01 09:00:00", "2026-01-03 09:00:00",
                    "2026-01-04 09:00:00"),
                row("SYN-06", "delivered", "2026-01-01 09:00:00",
                    "2026-01-02 12:00:00", "2026-01-02 11:00:00",
                    "2026-01-04 09:00:00"),
                row("SYN-07", "delivered", "2026-01-01 09:00:00",
                    "2026-01-02 09:00:00", "2026-01-03 09:00:00",
                    "2026-01-01 07:00:00"),
                row("SYN-08", "delivered", "2026-01-01 09:00:00",
                    "2026-01-02 09:00:00", "2026-01-01 07:00:00",
                    "2026-01-04 09:00:00"),
            ],
        )
        con.execute("CREATE VIEW test_original_lifecycle AS " + load_full_refresh_sql())
        cursor = con.execute("SELECT * FROM test_original_lifecycle ORDER BY order_id")
        names = [v[0] for v in cursor.description]
        rows = [dict(zip(names, result)) for result in cursor.fetchall()]
        by_id = {r["order_id"]: r for r in rows}
        assert len(rows) == 8 and len(by_id) == 8, "Order grain lost or duplicated"
        expected = {
            "SYN-01": (False, False, False, False, False, False, False, False),
            "SYN-02": (True, False, False, False, False, False, True, False),
            "SYN-03": (False, False, False, False, False, True, False, False),
            "SYN-04": (False, False, False, False, False, False, False, True),
            "SYN-05": (False, True, False, False, False, False, True, False),
            "SYN-06": (False, False, True, False, False, False, True, False),
            "SYN-07": (False, False, False, False, True, False, True, False),
            "SYN-08": (False, False, True, True, False, False, True, False),
        }
        fields = (
            "approval_before_purchase",
            "carrier_before_approval",
            "customer_delivery_before_carrier",
            "customer_delivery_before_purchase",
            "estimated_delivery_before_purchase",
            "is_delivered_order_missing_approval",
            "has_temporal_sequence_anomaly",
            "is_customer_delivery_timestamp_missing",
        )
        for key, want in expected.items():
            got = tuple(by_id[key][field] for field in fields)
            assert got == want, f"{key}: {got!r} != {want!r}"
        assert by_id["SYN-01"]["purchase_to_approval_hours"] == 1
        assert by_id["SYN-01"]["approval_to_carrier_hours"] == 24
        assert by_id["SYN-01"]["carrier_to_customer_hours"] == 24
        assert by_id["SYN-01"]["purchase_to_customer_hours"] == 49
        assert by_id["SYN-02"]["purchase_to_approval_hours"] is None
        assert by_id["SYN-05"]["approval_to_carrier_hours"] is None
        assert by_id["SYN-06"]["carrier_to_customer_hours"] is None
        assert by_id["SYN-03"]["is_delivered_order_missing_approval"] is True
        assert by_id["SYN-04"]["is_delivered_order_missing_customer_delivery_timestamp"] is False
        print("PASS: original order-lifecycle SELECT on 8 synthetic rows and QA flags.")
        print("Scope: full-refresh SELECT with documented dbt-Jinja removal; no incremental MERGE.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
