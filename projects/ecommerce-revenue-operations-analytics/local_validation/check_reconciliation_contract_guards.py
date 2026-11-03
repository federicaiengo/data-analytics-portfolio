"""Adversarial failure-mode checks for the local DuckDB reconciliation.

All records are fabricated. Validates source/target non-NULL unique keys,
complete column-name/type parity, missing-source key policy, and transaction
rollback when a deliberately injected error occurs AFTER a successful MERGE.

No user data, Snowflake connection, dbt adapter or production claims.
"""
import duckdb

import check_local_backdated_reconciliation as recovery
from check_local_incremental_semantics import order, snapshot


def fixture():
    con = duckdb.connect(":memory:")
    # No PRIMARY KEY constraint: intentionally allow adversarial duplicates.
    con.execute("""
        CREATE TABLE synthetic_stg_orders (
            order_id VARCHAR,
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
            order("SYN-001", "created", "2026-01-01 00:00:00"),
            order("SYN-002", "shipped", "2026-01-02 00:00:00"),
        ],
    )
    con.execute("CREATE TABLE local_incremental_target AS " + recovery.FULL)
    assert recovery.reconcile_full_snapshot(con) == []
    return con


def must_refuse(label, mutate, error_class, error_fragment):
    con = fixture()
    try:
        mutate(con)
        before = snapshot(con)
        try:
            recovery.reconcile_full_snapshot(con)
        except error_class as exc:
            assert error_fragment in str(exc), (
                f"{label}: unexpected rejection text {exc!r}"
            )
        else:
            raise AssertionError(f"{label}: dangerous input was accepted")
        assert snapshot(con) == before, (
            f"{label}: target changed even though reconciliation was rejected"
        )
        # A failed transaction must not leave an active transaction behind.
        con.execute("BEGIN TRANSACTION")
        con.execute("ROLLBACK")
        print("PASS: fail-closed " + label)
    finally:
        con.close()


def duplicate_source(con):
    con.execute(
        "INSERT INTO synthetic_stg_orders "
        "SELECT * FROM synthetic_stg_orders WHERE order_id='SYN-001'"
    )


def null_source_key(con):
    invalid = list(order("SYN-999", "created", "2026-01-03 00:00:00"))
    invalid[0] = None
    con.execute(
        "INSERT INTO synthetic_stg_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        invalid,
    )


def duplicate_target(con):
    con.execute(
        "INSERT INTO local_incremental_target "
        "SELECT * FROM local_incremental_target WHERE order_id='SYN-001'"
    )


def null_target_key(con):
    con.execute(
        "UPDATE local_incremental_target SET order_id=NULL "
        "WHERE order_id='SYN-001'"
    )


def schema_extra_column(con):
    con.execute("ALTER TABLE local_incremental_target ADD COLUMN unexpected VARCHAR")


def schema_wrong_type(con):
    con.execute(
        "ALTER TABLE local_incremental_target "
        "ALTER COLUMN order_status TYPE INTEGER USING 1"
    )


def missing_source_key(con):
    con.execute("DELETE FROM synthetic_stg_orders WHERE order_id='SYN-002'")


def rollback_after_merge():
    """Inject a fault after a real MERGE to assert database-level rollback."""
    con = fixture()
    original_merge = recovery.merge_incremental
    try:
        con.execute(
            "UPDATE synthetic_stg_orders SET order_status='delivered' "
            "WHERE order_id='SYN-001'"
        )
        before = snapshot(con)
        def injected_failure(connection, sql):
            original_merge(connection, sql)
            # Explicit test-only fault after the MERGE has written data.
            raise RuntimeError("injected post-merge failure")
        recovery.merge_incremental = injected_failure
        try:
            recovery.reconcile_full_snapshot(con)
        except RuntimeError as exc:
            assert str(exc) == "injected post-merge failure"
        else:
            raise AssertionError("Fault-injected MERGE unexpectedly committed")
        finally:
            recovery.merge_incremental = original_merge
        assert snapshot(con) == before, "A partial MERGE escaped ROLLBACK"
        # The rolled-back temporary delta must not poison a subsequent retry.
        assert recovery.reconcile_full_snapshot(con) == ["SYN-001"]
        assert con.execute(
            "SELECT order_status FROM local_incremental_target "
            "WHERE order_id='SYN-001'"
        ).fetchone()[0] == "delivered"
        assert recovery.reconcile_full_snapshot(con) == []
        print("PASS: post-MERGE injected failure rolled back and safe retry succeeded")
    finally:
        recovery.merge_incremental = original_merge
        con.close()


def main():
    must_refuse("source duplicate keys", duplicate_source,
                ValueError, "Duplicate business key")
    must_refuse("source NULL key", null_source_key,
                ValueError, "NULL business key")
    must_refuse("target duplicate keys", duplicate_target,
                ValueError, "Duplicate business key")
    must_refuse("target NULL key", null_target_key,
                ValueError, "NULL business key")
    must_refuse("unexpected target column", schema_extra_column,
                ValueError, "schema drift")
    must_refuse("changed target column type", schema_wrong_type,
                ValueError, "schema drift")
    must_refuse("source-missing key without deletion policy", missing_source_key,
                RuntimeError, "manual deletion/reload policy")
    rollback_after_merge()
    print("PASS: 7 independent guard-failure cases + transactional rollback/retry.")
    print("Scope: synthetic single-connection DuckDB; concurrency not established.")


if __name__ == "__main__":
    main()
