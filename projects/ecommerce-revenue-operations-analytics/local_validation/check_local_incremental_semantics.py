"""DuckDB-only experiment for order-lifecycle incremental MERGE semantics.

Uses ORIGINAL int_orders_lifecycle SELECT, with guarded dbt config/Jinja
substitutions, and an explicitly LOCAL DuckDB MERGE implementation aligned to
the original model's unique_key and >= max(_loaded_at) predicate. This is
NOT a dbt-generated MERGE, real Snowflake run, or end-to-end dbt validation.
"""
from pathlib import Path
import re

import duckdb

from check_original_lifecycle import load_full_refresh_sql

MODEL = (
    Path(__file__).resolve().parents[1]
    / "dbt/ecommerce_revenue_operations/models/intermediate/int_orders_lifecycle.sql"
)


def render_incremental_select():
    original = MODEL.read_text(encoding="utf-8")
    for required in (
        "materialized='incremental'",
        "unique_key='order_id'",
        "incremental_strategy='merge'",
        "on_schema_change='sync_all_columns'",
    ):
        assert required in original, f"dbt config changed: {required}"
    original, n_config = re.subn(
        r"\A\s*\{\{\s*config\([\s\S]*?\)\s*\}\}\s*",
        "", original, count=1,
    )
    assert n_config == 1, "Unexpected dbt config block"
    for marker in ("{% if is_incremental() %}", "{% endif %}"):
        assert original.count(marker) == 1, f"Unexpected Jinja marker: {marker}"
        original = original.replace(marker, "")
    refs = {
        "{{ ref('stg_orders') }}": "synthetic_stg_orders",
        "{{ this }}": "local_incremental_target",
        "'1900-01-01'::timestamp_ntz": "TIMESTAMP '1900-01-01'",
    }
    for marker, replacement in refs.items():
        assert original.count(marker) == 1, f"Expected exactly one: {marker}"
        original = original.replace(marker, replacement)
    assert original.count("where _loaded_at >=") == 1
    assert original.count("max(_loaded_at)") == 1
    assert not any(token in original for token in ("{{", "}}", "{%", "%}", "timestamp_ntz"))
    return original


def snapshot(con):
    return con.execute(
        "SELECT * FROM local_incremental_target ORDER BY order_id"
    ).fetchall()


def merge_incremental(con, select_sql):
    # The DuckDB MERGE statement is locally assembled to simulate the dbt
    # unique_key MERGE contract. It is not captured dbt compiled SQL.
    columns = [
        row[0] for row in con.execute("DESCRIBE local_incremental_target").fetchall()
    ]
    assert "order_id" in columns and "_loaded_at" in columns
    assert len(columns) == len(set(columns))
    update_assignments = ", ".join(
        f"{column} = s.{column}" for column in columns if column != "order_id"
    )
    insert_columns = ", ".join(columns)
    insert_values = ", ".join(f"s.{column}" for column in columns)
    statement = (
        "MERGE INTO local_incremental_target AS t "
        f"USING ({select_sql}) AS s ON t.order_id = s.order_id "
        f"WHEN MATCHED THEN UPDATE SET {update_assignments} "
        f"WHEN NOT MATCHED THEN INSERT ({insert_columns}) "
        f"VALUES ({insert_values})"
    )
    con.execute(statement)


def order(key, status, loaded_at):
    return (
        key, "CUSTOMER-" + key, status,
        "2026-01-01 08:00:00", "2026-01-01 09:00:00",
        None, None, "2026-01-10 08:00:00",
        loaded_at, "synthetic_only.csv", int(key[-3:]),
    )


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
        con.executemany(
            "INSERT INTO synthetic_stg_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                order("SYN-001", "created", "2026-01-30 12:00:00"),
                order("SYN-002", "shipped", "2026-02-01 12:00:00"),
                order("SYN-003", "created", "2026-02-01 12:00:00"),
            ],
        )
        # Full-refresh source SQL from the same original model.
        con.execute(
            "CREATE TABLE local_incremental_target AS " + load_full_refresh_sql()
        )
        assert con.execute(
            "SELECT count(*) FROM local_incremental_target"
        ).fetchone()[0] == 3
        incremental = render_incremental_select()
        assert con.execute(
            "SELECT count(*) FROM (" + incremental + ")"
        ).fetchone()[0] == 2, "Must reprocess both rows sharing last watermark"

        # First rerun without input changes must be exactly idempotent.
        before = snapshot(con)
        merge_incremental(con, incremental)
        assert snapshot(con) == before, "No-op rerun changed rows"

        # A new batch includes an UPDATE tied to the old max watermark,
        # one genuinely new key, and a deliberately backdated change.
        con.execute(
            "UPDATE synthetic_stg_orders SET order_status='delivered' "
            "WHERE order_id='SYN-002'"
        )
        con.execute(
            "UPDATE synthetic_stg_orders SET order_status='canceled' "
            "WHERE order_id='SYN-001'"
        )
        con.execute(
            "INSERT INTO synthetic_stg_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            order("SYN-004", "created", "2026-02-02 12:00:00"),
        )
        assert con.execute(
            "SELECT count(*) FROM (" + incremental + ")"
        ).fetchone()[0] == 3
        merge_incremental(con, incremental)
        rows = {
            key: status for key, status in con.execute(
                "SELECT order_id, order_status FROM local_incremental_target"
            ).fetchall()
        }
        assert len(rows) == 4
        assert rows["SYN-002"] == "delivered", "Equal watermark update not merged"
        assert rows["SYN-004"] == "created", "New order not inserted"
        # Deliberate limitation: an old source mutation with unchanged, old
        # ingestion timestamp is NOT picked up by this watermark contract.
        assert rows["SYN-001"] == "created", "Older source row unexpectedly updated"

        # A rerun with only latest batch is idempotent, including metadata.
        assert con.execute(
            "SELECT count(*) FROM (" + incremental + ")"
        ).fetchone()[0] == 1
        before = snapshot(con)
        merge_incremental(con, incremental)
        assert snapshot(con) == before

        # A new row sharing the current maximum watermark is not skipped.
        con.execute(
            "INSERT INTO synthetic_stg_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            order("SYN-005", "created", "2026-02-02 12:00:00"),
        )
        assert con.execute(
            "SELECT count(*) FROM (" + incremental + ")"
        ).fetchone()[0] == 2
        merge_incremental(con, incremental)
        assert con.execute(
            "SELECT count(*) FROM local_incremental_target"
        ).fetchone()[0] == 5
        assert con.execute(
            "SELECT count(distinct order_id) FROM local_incremental_target"
        ).fetchone()[0] == 5
        before = snapshot(con)
        merge_incremental(con, incremental)
        assert snapshot(con) == before

        print("PASS: original lifecycle incremental predicate + local DuckDB MERGE contract.")
        print("PASS: equal watermark updates, insert, idempotent reruns, tied new batch.")
        print("KNOWN LIMIT: unchanged old _loaded_at can omit a backdated source correction.")
        print("Scope: local emulation, not dbt compiled MERGE or Snowflake execution.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
