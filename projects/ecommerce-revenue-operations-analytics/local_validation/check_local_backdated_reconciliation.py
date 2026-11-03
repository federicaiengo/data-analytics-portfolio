"""Synthetic-only detection and optional repair of backdated lifecycle changes.

Compares the ORIGINAL lifecycle full-refresh SELECT against a locally managed
DuckDB target using exact row EXCEPT (including NULL semantics), rather than
relying only on the original >= MAX(_loaded_at) incremental filter.

The repair uses a locally constructed MERGE, NOT dbt-compiled/Snowflake SQL.
Missing-source keys are a STOP condition: no implicit deletion, no silent
tombstone inference. The local repair owns a transaction and rolls back on
failed contracts; this is NOT a concurrency guarantee for Snowflake/dbt.
Neither actual Snowflake data nor secrets are read.
"""
from pathlib import Path

import duckdb

from check_original_lifecycle import load_full_refresh_sql
from check_local_incremental_semantics import (
    merge_incremental, order, render_incremental_select, snapshot,
)

FULL = load_full_refresh_sql()
SOURCE = "SELECT * FROM (" + FULL + ") AS full_source"
TARGET = "local_incremental_target"


def exact_keys(con, relation_sql):
    rows = con.execute("SELECT order_id FROM (" + relation_sql + ")").fetchall()
    values = [r[0] for r in rows]
    if any(key is None for key in values):
        raise ValueError("NULL business key: stop reconciliation")
    if len(values) != len(set(values)):
        raise ValueError("Duplicate business key: stop reconciliation")
    return set(values)


def source_only_keys(con):
    # A deletion or filtering change is NOT automatically a deletion request.
    return sorted(
        row[0] for row in con.execute(
            "SELECT order_id FROM local_incremental_target "
            "EXCEPT SELECT order_id FROM (" + SOURCE + ")"
        ).fetchall()
    )


def validate_contract(con):
    src_keys = exact_keys(con, SOURCE)
    target_keys = exact_keys(con, "SELECT * FROM " + TARGET)
    target_schema = [
        (r[0], r[1]) for r in con.execute("DESCRIBE " + TARGET).fetchall()
    ]
    source_schema = [
        (r[0], r[1])
        for r in con.execute("DESCRIBE SELECT * FROM (" + SOURCE + ")").fetchall()
    ]
    if target_schema != source_schema:
        raise ValueError("Unexpected source/target schema drift (name or type)")
    missing_in_source = sorted(target_keys - src_keys)
    if missing_in_source:
        raise RuntimeError(
            "Source missing keys; manual deletion/reload policy required: "
            + ", ".join(missing_in_source)
        )
    return src_keys, target_keys


def reconcile_full_snapshot(con):
    """Run an all-or-nothing DuckDB reconciliation, including all guards.

    Owns the local transaction; callers must not already be in one. This is
    deliberately NOT a production locking/concurrency protocol.
    """
    con.execute("BEGIN TRANSACTION")
    try:
        validate_contract(con)
        con.execute(
            "CREATE TEMP TABLE reconciliation_delta AS "
            + SOURCE + " EXCEPT SELECT * FROM " + TARGET
        )
        changed = exact_keys(con, "SELECT * FROM reconciliation_delta")
        # EXCEPT compares complete rows including NULLs and old timestamps.
        if changed:
            merge_incremental(con, "SELECT * FROM reconciliation_delta")
        exact_keys(con, "SELECT * FROM " + TARGET)
        source_to_target = con.execute(
            "SELECT COUNT(*) FROM (" + SOURCE +
            " EXCEPT SELECT * FROM " + TARGET + ")"
        ).fetchone()[0]
        target_to_source = con.execute(
            "SELECT COUNT(*) FROM (SELECT * FROM " + TARGET +
            " EXCEPT " + SOURCE + ")"
        ).fetchone()[0]
        assert source_to_target == 0 and target_to_source == 0, (
            "Full-source reconciliation differs in at least one direction"
        )
        con.execute("DROP TABLE reconciliation_delta")
        con.execute("COMMIT")
        return sorted(changed)
    except Exception:
        con.execute("ROLLBACK")
        raise


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
        con.execute("CREATE TABLE " + TARGET + " AS " + FULL)
        incremental = render_incremental_select()
        before = snapshot(con)
        assert reconcile_full_snapshot(con) == [], "Initial snapshot should match"
        assert snapshot(con) == before, "No-op reconciliation mutated rows"

        # Unchanged old watermark: the existing incremental filter misses the
        # status/NULL timestamp correction and a newly backdated order.
        con.execute("""
            UPDATE synthetic_stg_orders
            SET order_status = 'delivered', order_approved_at = NULL
            WHERE order_id = 'SYN-001'
        """)
        con.execute(
            "INSERT INTO synthetic_stg_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            order("SYN-000", "created", "2026-01-01 12:00:00"),
        )
        assert con.execute(
            "SELECT COUNT(*) FROM (" + incremental + ")"
        ).fetchone()[0] == 2, "Incremental selection unexpectedly included old rows"
        merge_incremental(con, incremental)
        statuses = dict(con.execute(
            "SELECT order_id, order_status FROM " + TARGET
        ).fetchall())
        assert statuses["SYN-001"] == "created", "Baseline miss no longer reproduced"
        assert "SYN-000" not in statuses, "Baseline missed-new-key condition changed"

        delta = reconcile_full_snapshot(con)
        assert delta == ["SYN-000", "SYN-001"], f"Unexpected backfill keys: {delta}"
        statuses = dict(con.execute(
            "SELECT order_id, order_status FROM " + TARGET
        ).fetchall())
        assert len(statuses) == 4
        assert statuses["SYN-000"] == "created"
        assert statuses["SYN-001"] == "delivered"
        corrected = con.execute("""
            SELECT is_approval_missing, is_delivered_order_missing_approval,
                   _loaded_at
            FROM local_incremental_target WHERE order_id = 'SYN-001'
        """).fetchone()
        assert corrected[0:2] == (True, True)
        assert str(corrected[2]) == "2026-01-30 12:00:00", (
            "Historical _loaded_at was silently changed"
        )
        after = snapshot(con)
        assert reconcile_full_snapshot(con) == [], "Repair is not idempotent"
        assert snapshot(con) == after

        # A newly arrived equal-watermark record can still be handled by
        # the original incremental logic after this correction.
        con.execute(
            "INSERT INTO synthetic_stg_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            order("SYN-004", "created", "2026-02-01 12:00:00"),
        )
        merge_incremental(con, incremental)
        assert reconcile_full_snapshot(con) == []
        assert len(snapshot(con)) == 5

        # Explicitly do NOT equate a missing source key with a delete.
        # A delete must be resolved against a governed source/deletion policy.
        con.execute("DELETE FROM synthetic_stg_orders WHERE order_id = 'SYN-002'")
        assert source_only_keys(con) == ["SYN-002"]
        prior = snapshot(con)
        try:
            reconcile_full_snapshot(con)
        except RuntimeError as error:
            assert "SYN-002" in str(error)
        else:
            raise AssertionError("Missing-source key was not a fail-closed condition")
        assert snapshot(con) == prior, "Deletion guard mutated the target"

        print("PASS: backdated NULL/status changes and older new keys detected and recovered.")
        print("PASS: idempotent reconciliation, equal-watermark normal MERGE, no duplicates.")
        print("PASS: source-missing key detected without inferred destructive delete.")
        print("LIMIT: full-source scan cost, missing-key policy, source freshness and concurrency.")
        print("Scope: synthetic DuckDB reconciliation; NOT dbt/Snowflake production repair.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
