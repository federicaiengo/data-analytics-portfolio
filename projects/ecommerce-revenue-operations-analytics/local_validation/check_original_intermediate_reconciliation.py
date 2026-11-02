"""Exercise three unchanged original dbt intermediate SQL models in DuckDB.

Synthetic-only regression harness: not Snowflake, dbt compilation, or a
production-data pipeline. Each dependency is substituted once by exact ref.
No user files, credentials or network data are read.
"""
from decimal import Decimal
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "dbt/ecommerce_revenue_operations/models/intermediate"

MODEL_REFS = (
    ("int_order_items_summary.sql", "test_item_summary", {"stg_order_items": "stg_order_items"}),
    ("int_order_payments_summary.sql", "test_payment_summary", {"stg_order_payments": "stg_order_payments"}),
    (
        "int_order_financial_reconciliation.sql",
        "test_financial_reconciliation",
        {
            "stg_orders": "stg_orders",
            "int_order_items_summary": "test_item_summary",
            "int_order_payments_summary": "test_payment_summary",
        },
    ),
)


def exact_model_sql(filename, refs):
    sql = (MODELS / filename).read_text(encoding="utf-8")
    for source_ref, relation in refs.items():
        marker = "{{ ref('" + source_ref + "') }}"
        assert sql.count(marker) == 1, (
            f"{filename}: expected exactly one {marker}; inspect model drift"
        )
        sql = sql.replace(marker, relation)
    assert "{{" not in sql and "}}" not in sql, (
        f"{filename}: unsupported/unresolved Jinja syntax"
    )
    return sql


def keyed_rows(con, table):
    cursor = con.execute("SELECT * FROM " + table + " ORDER BY order_id")
    names = [column[0] for column in cursor.description]
    data = [dict(zip(names, row)) for row in cursor.fetchall()]
    keys = [row["order_id"] for row in data]
    assert len(keys) == len(set(keys)), f"Duplicate order grain in {table}"
    return {row["order_id"]: row for row in data}


def main():
    con = duckdb.connect(":memory:")
    try:
        con.execute("""
        CREATE TABLE stg_orders (
            order_id VARCHAR PRIMARY KEY,
            customer_id VARCHAR,
            order_status VARCHAR
        );
        CREATE TABLE stg_order_items (
            order_id VARCHAR,
            product_id VARCHAR,
            seller_id VARCHAR,
            price DECIMAL(12,2),
            freight_value DECIMAL(12,2)
        );
        CREATE TABLE stg_order_payments (
            order_id VARCHAR,
            payment_type VARCHAR,
            payment_installments INTEGER,
            payment_value DECIMAL(12,2)
        );
        """)
        con.executemany("INSERT INTO stg_orders VALUES (?, ?, ?)", [
            ("SYN-001", "C1", "delivered"),
            ("SYN-002", "C2", "shipped"),
            ("SYN-003", "C3", "delivered"),
            ("SYN-004", "C4", "delivered"),
            ("SYN-005", "C5", "delivered"),
            ("SYN-006", "C6", "delivered"),
            ("SYN-007", "C7", "delivered"),
        ])
        con.executemany("INSERT INTO stg_order_items VALUES (?, ?, ?, ?, ?)", [
            ("SYN-001", "P1", "S1", "90.00", "5.00"),
            ("SYN-001", "P2", "S1", "50.00", "5.00"),
            ("SYN-002", "P3", "S2", "40.00", "5.00"),
            ("SYN-004", "P4", "S3", "25.00", "5.00"),
            ("SYN-005", "P5", "S4", "50.00", "5.00"),
            ("SYN-006", "P6", "S5", "10.00", "0.00"),
            ("SYN-007", "P7", "S6", "10.00", "0.00"),
            ("SYN-999", "ORPHAN", "ORPHAN", "5.00", "0.00"),
        ])
        con.executemany("INSERT INTO stg_order_payments VALUES (?, ?, ?, ?)", [
            ("SYN-001", "credit_card", 3, "60.00"),
            ("SYN-001", "voucher", 1, "40.00"),
            ("SYN-001", "credit_card", 3, "50.00"),
            ("SYN-002", "credit_card", 1, "50.00"),
            ("SYN-003", "voucher", 1, "20.00"),
            ("SYN-004", "credit_card", 1, "30.00"),
            ("SYN-006", "credit_card", 1, "10.01"),
            ("SYN-007", "credit_card", 1, "10.02"),
            ("SYN-998", "voucher", 1, "2.00"),
        ])
        for filename, name, refs in MODEL_REFS:
            sql = exact_model_sql(filename, refs)
            con.execute("CREATE VIEW " + name + " AS " + sql)

        items = keyed_rows(con, "test_item_summary")
        payments = keyed_rows(con, "test_payment_summary")
        reconciled = keyed_rows(con, "test_financial_reconciliation")

        assert items["SYN-001"]["order_item_count"] == 2
        assert items["SYN-001"]["distinct_product_count"] == 2
        assert items["SYN-001"]["distinct_seller_count"] == 1
        assert items["SYN-001"]["item_plus_freight_value"] == Decimal("150.00")
        assert payments["SYN-001"]["payment_record_count"] == 3
        assert payments["SYN-001"]["distinct_payment_type_count"] == 2
        assert payments["SYN-001"]["max_payment_installments"] == 3
        assert payments["SYN-001"]["payment_value"] == Decimal("150.00")

        assert set(reconciled) == {"SYN-001", "SYN-002", "SYN-003",
                                    "SYN-004", "SYN-005", "SYN-006", "SYN-007"}
        assert "SYN-998" not in reconciled and "SYN-999" not in reconciled
        expected = {
            # order_id: missing_items, missing_payments, match, payment-minus-items
            "SYN-001": (False, False, True, Decimal("0.00")),
            "SYN-002": (False, False, False, Decimal("5.00")),
            "SYN-003": (True, False, None, None),
            "SYN-004": (False, False, True, Decimal("0.00")),
            "SYN-005": (False, True, None, None),
            "SYN-006": (False, False, True, Decimal("0.01")),
            "SYN-007": (False, False, False, Decimal("0.02")),
        }
        for order_id, want in expected.items():
            row = reconciled[order_id]
            got = (
                row["missing_item_summary"],
                row["missing_payment_summary"],
                row["financial_values_match"],
                row["payment_minus_item_freight_value"],
            )
            assert got == want, f"{order_id}: observed={got!r}; expected={want!r}"

        # A raw items x payments JOIN would multiply six rows for SYN-001.
        naive_rows = con.execute("""
            SELECT count(*) FROM stg_order_items i
            JOIN stg_order_payments p USING (order_id)
            WHERE order_id = 'SYN-001'
        """).fetchone()[0]
        assert naive_rows == 6, naive_rows
        assert len(reconciled) == 7, "Aggregating before joining lost order grain"
        print("PASS: 3 unchanged original intermediate dbt SQL models executed on DuckDB.")
        print("PASS: 7 orders; multiple items/payments, nulls, orphans, cent tolerance, grain.")
        print("Scope: synthetic in-memory values only; no Snowflake or entire dbt project.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
