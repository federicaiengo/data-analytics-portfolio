"""Local two-connection DuckDB snapshot and write-conflict experiments.

All records are invented, on one temporary DuckDB file in a single Python
process. This deliberately tests database behavior, NOT the correctness of
the connected 11-model SQL subset under concurrent real source updates,
dbt MERGE compilation, or multi-process/warehouse isolation.
"""
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb


def state(connection):
    return dict(connection.execute(
        "SELECT order_id, order_status FROM synthetic_orders ORDER BY order_id"
    ).fetchall())


def main():
    with TemporaryDirectory(prefix="synthetic_duckdb_concurrency_") as d:
        db_path = str(Path(d) / "sandbox.duckdb")
        a = duckdb.connect(db_path)
        b = duckdb.connect(db_path)
        try:
            a.execute("""
                CREATE TABLE synthetic_orders (
                    order_id VARCHAR PRIMARY KEY,
                    order_status VARCHAR NOT NULL
                );
                INSERT INTO synthetic_orders VALUES
                    ('SYN-001', 'created'),
                    ('SYN-002', 'created');
            """)
            assert state(a) == state(b) == {
                "SYN-001": "created", "SYN-002": "created"
            }

            # Connection A pins a read snapshot; B commits a new version.
            a.execute("BEGIN TRANSACTION")
            before = state(a)
            b.execute("BEGIN TRANSACTION")
            b.execute("""
                UPDATE synthetic_orders SET order_status='shipped'
                WHERE order_id='SYN-001'
            """)
            b.execute("COMMIT")
            assert state(a) == before, (
                "Read snapshot changed mid-transaction; investigate isolation"
            )

            # An old snapshot must NOT silently overwrite a committed writer.
            conflict_detected = False
            try:
                a.execute("""
                    UPDATE synthetic_orders SET order_status='canceled'
                    WHERE order_id='SYN-001'
                """)
            except duckdb.Error as exc:
                assert "conflict" in str(exc).lower(), (
                    "Unexpected database error rather than write conflict: "
                    + str(exc)
                )
                conflict_detected = True
            finally:
                a.execute("ROLLBACK")
            assert conflict_detected, "Stale writer silently overwrote committed data"
            assert state(a)["SYN-001"] == "shipped"
            assert state(b)["SYN-001"] == "shipped"

            # A fresh transaction can intentionally retry using current state.
            a.execute("BEGIN TRANSACTION")
            assert state(a)["SYN-001"] == "shipped"
            a.execute("""
                UPDATE synthetic_orders SET order_status='delivered'
                WHERE order_id='SYN-001'
            """)
            a.execute("COMMIT")
            assert state(b)["SYN-001"] == "delivered"

            # Concurrent modifications to *different* order IDs should not
            # force accidental cross-key overwrites.
            a.execute("BEGIN TRANSACTION")
            b.execute("BEGIN TRANSACTION")
            a.execute("""
                UPDATE synthetic_orders SET order_status='closed'
                WHERE order_id='SYN-001'
            """)
            b.execute("""
                UPDATE synthetic_orders SET order_status='approved'
                WHERE order_id='SYN-002'
            """)
            a.execute("COMMIT")
            b.execute("COMMIT")
            assert state(a) == state(b) == {
                "SYN-001": "closed", "SYN-002": "approved"
            }
            assert a.execute(
                "SELECT count(*) = count(distinct order_id) "
                "FROM synthetic_orders"
            ).fetchone()[0] is True

            print("PASS: committed writer invisible to earlier transaction snapshot.")
            print("PASS: stale same-key update conflicts; rollback preserves committed row.")
            print("PASS: fresh retry and independent-key concurrent changes.")
            print("Scope: one process/two DuckDB connections; no production race guarantee.")
        finally:
            a.close()
            b.close()


if __name__ == "__main__":
    main()
