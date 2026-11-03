"""Synthetic-only DuckDB validation of the unchanged original fct_orders dbt SQL.

The SQL in the repository is loaded verbatim except for three exact dbt ref()
substitutions. Source upstream relations are deliberately synthetic and
pre-aggregated: this is not a full dbt/Snowflake migration or an integrated
run of the original intermediate models.

Checks left-join grain, missing upstream relations, financial/review fields,
orphan data, and exposes duplicate upstream keys as a grain hazard.
"""
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "dbt/ecommerce_revenue_operations/models/marts/core/fct_orders.sql"
DEPENDENCIES = {
    "int_orders_lifecycle": "fixture_lifecycle",
    "int_order_financial_reconciliation": "fixture_reconciliation",
    "int_order_reviews_summary": "fixture_reviews",
}

# Explicit schemas match columns consumed by fct_orders. No raw source records.
LIFECYCLE = {
    "order_id": "VARCHAR",
    "customer_id": "VARCHAR",
    "order_status": "VARCHAR",
    "order_purchase_timestamp": "TIMESTAMP",
    "order_approved_at": "TIMESTAMP",
    "order_delivered_carrier_date": "TIMESTAMP",
    "order_delivered_customer_date": "TIMESTAMP",
    "order_estimated_delivery_date": "TIMESTAMP",
    "is_approval_missing": "BOOLEAN",
    "is_carrier_timestamp_missing": "BOOLEAN",
    "is_customer_delivery_timestamp_missing": "BOOLEAN",
    "is_delivered_order_missing_approval": "BOOLEAN",
    "is_delivered_order_missing_carrier_timestamp": "BOOLEAN",
    "is_delivered_order_missing_customer_delivery_timestamp": "BOOLEAN",
    "approval_before_purchase": "BOOLEAN",
    "carrier_before_approval": "BOOLEAN",
    "customer_delivery_before_carrier": "BOOLEAN",
    "customer_delivery_before_purchase": "BOOLEAN",
    "estimated_delivery_before_purchase": "BOOLEAN",
    "has_temporal_sequence_anomaly": "BOOLEAN",
    "purchase_to_approval_hours": "DOUBLE",
    "approval_to_carrier_hours": "DOUBLE",
    "carrier_to_customer_hours": "DOUBLE",
    "purchase_to_customer_hours": "DOUBLE",
}
FINANCIAL = {
    "order_id": "VARCHAR",
    "order_item_count": "INTEGER",
    "distinct_product_count": "INTEGER",
    "distinct_seller_count": "INTEGER",
    "item_sales_value": "DECIMAL(12,2)",
    "freight_value": "DECIMAL(12,2)",
    "item_plus_freight_value": "DECIMAL(12,2)",
    "payment_record_count": "INTEGER",
    "distinct_payment_type_count": "INTEGER",
    "max_payment_installments": "INTEGER",
    "payment_value": "DECIMAL(12,2)",
    "missing_item_summary": "BOOLEAN",
    "missing_payment_summary": "BOOLEAN",
    "payment_minus_item_freight_value": "DECIMAL(12,2)",
    "financial_values_match": "BOOLEAN",
}
REVIEWS = {
    "order_id": "VARCHAR",
    "review_record_count": "INTEGER",
    "distinct_review_id_count": "INTEGER",
    "average_review_score": "DECIMAL(5,2)",
    "minimum_review_score": "INTEGER",
    "maximum_review_score": "INTEGER",
    "distinct_review_score_count": "INTEGER",
    "has_multiple_review_scores": "BOOLEAN",
    "first_review_creation_date": "TIMESTAMP",
    "last_review_creation_date": "TIMESTAMP",
    "first_review_answer_timestamp": "TIMESTAMP",
    "last_review_answer_timestamp": "TIMESTAMP",
    "review_title_record_count": "INTEGER",
    "review_message_record_count": "INTEGER",
    "has_review_title": "BOOLEAN",
    "has_review_message": "BOOLEAN",
}


def load_original_model(refs=DEPENDENCIES):
    sql = MODEL.read_text(encoding="utf-8")
    for dbt_name, relation in refs.items():
        marker = "{{ ref('" + dbt_name + "') }}"
        assert sql.count(marker) == 1, f"Expected exactly one dbt ref to {dbt_name}"
        sql = sql.replace(marker, relation)
    assert "{{" not in sql and "{%" not in sql and "}}" not in sql and "%}" not in sql, (
        "Unexpected additional dbt/Jinja template syntax"
    )
    return sql


def add_table(con, name, schema, data):
    cols = list(schema)
    # These are static identifiers specified in this script, not untrusted inputs.
    con.execute(
        f"CREATE TABLE {name} (" +
        ", ".join(f"{column} {kind}" for column, kind in schema.items()) +
        ")"
    )
    for row in data:
        assert row.keys() <= schema.keys(), f"Unexpected columns for {name}"
        placeholders = ", ".join("?" for _ in cols)
        con.execute(
            f"INSERT INTO {name} VALUES ({placeholders})",
            [row.get(column) for column in cols],
        )


def main():
    con = duckdb.connect(":memory:")
    try:
        t0 = "2026-01-01 08:00:00"
        add_table(con, "fixture_lifecycle", LIFECYCLE, [
            {
                "order_id": "SYN-001",
                "customer_id": "C1",
                "order_status": "delivered",
                "order_purchase_timestamp": t0,
                "order_approved_at": "2026-01-01 09:00:00",
                "order_delivered_customer_date": "2026-01-03 09:00:00",
                "has_temporal_sequence_anomaly": False,
                "purchase_to_approval_hours": 1.0,
            },
            {
                "order_id": "SYN-002",
                "customer_id": "C2",
                "order_status": "shipped",
                "order_purchase_timestamp": t0,
                "has_temporal_sequence_anomaly": True,
                "approval_before_purchase": True,
                "is_approval_missing": True,
            },
            {"order_id": "SYN-003", "customer_id": "C3", "order_status": "created"},
            {"order_id": "SYN-004", "customer_id": "C4", "order_status": "delivered"},
            {"order_id": "SYN-005", "customer_id": "C5", "order_status": "canceled"},
        ])
        add_table(con, "fixture_reconciliation", FINANCIAL, [
            {
                "order_id": "SYN-001",
                "order_item_count": 2,
                "distinct_product_count": 2,
                "item_sales_value": "140.00",
                "freight_value": "10.00",
                "item_plus_freight_value": "150.00",
                "payment_record_count": 3,
                "payment_value": "150.00",
                "missing_item_summary": False,
                "missing_payment_summary": False,
                "payment_minus_item_freight_value": "0.00",
                "financial_values_match": True,
            },
            {
                "order_id": "SYN-002",
                "order_item_count": 1,
                "payment_record_count": 1,
                "payment_value": "50.00",
                "item_plus_freight_value": "45.00",
                "payment_minus_item_freight_value": "5.00",
                "missing_item_summary": False,
                "missing_payment_summary": False,
                "financial_values_match": False,
            },
            {
                "order_id": "SYN-003",
                "payment_record_count": 1,
                "payment_value": "20.00",
                "missing_item_summary": True,
                "missing_payment_summary": False,
                "payment_minus_item_freight_value": None,
                "financial_values_match": None,
            },
            {"order_id": "SYN-999", "item_sales_value": "99.99"},
        ])
        add_table(con, "fixture_reviews", REVIEWS, [
            {
                "order_id": "SYN-001",
                "review_record_count": 2,
                "distinct_review_id_count": 2,
                "average_review_score": "4.50",
                "minimum_review_score": 4,
                "maximum_review_score": 5,
                "distinct_review_score_count": 2,
                "has_multiple_review_scores": True,
                "review_title_record_count": 1,
                "review_message_record_count": 2,
                "has_review_title": True,
                "has_review_message": True,
                "first_review_creation_date": "2026-01-04 08:00:00",
            },
            {
                "order_id": "SYN-003",
                "review_record_count": 1,
                "average_review_score": "2.00",
                "minimum_review_score": 2,
                "maximum_review_score": 2,
                "has_multiple_review_scores": False,
                "has_review_title": False,
                "has_review_message": True,
            },
            {"order_id": "SYN-004", "review_record_count": 0, "has_review_message": False},
            {"order_id": "SYN-998", "review_record_count": 1},
        ])
        con.execute("CREATE VIEW original_fact_orders_under_test AS " + load_original_model())
        cursor = con.execute("SELECT * FROM original_fact_orders_under_test ORDER BY order_id")
        columns = [col[0] for col in cursor.description]
        records = [dict(zip(columns, record)) for record in cursor.fetchall()]
        ids = [r["order_id"] for r in records]
        assert ids == [f"SYN-{i:03d}" for i in range(1, 6)], ids
        assert len(set(ids)) == 5, "Fact grain must remain one row per lifecycle order"
        by_id = {r["order_id"]: r for r in records}
        assert by_id["SYN-001"]["customer_id"] == "C1"
        assert by_id["SYN-001"]["order_item_count"] == 2
        assert by_id["SYN-001"]["payment_record_count"] == 3
        assert by_id["SYN-001"]["item_plus_freight_value"] == Decimal("150.00")
        assert by_id["SYN-001"]["payment_value"] == Decimal("150.00")
        assert by_id["SYN-001"]["financial_values_match"] is True
        assert by_id["SYN-001"]["review_record_count"] == 2
        assert by_id["SYN-001"]["average_review_score"] == Decimal("4.50")
        assert by_id["SYN-001"]["has_multiple_review_scores"] is True
        assert isinstance(by_id["SYN-001"]["first_review_creation_date"], datetime)

        assert by_id["SYN-002"]["financial_values_match"] is False
        assert by_id["SYN-002"]["payment_minus_item_freight_value"] == Decimal("5.00")
        assert by_id["SYN-002"]["has_temporal_sequence_anomaly"] is True
        assert by_id["SYN-002"]["review_record_count"] is None
        assert by_id["SYN-003"]["missing_item_summary"] is True
        assert by_id["SYN-003"]["financial_values_match"] is None
        assert by_id["SYN-003"]["review_record_count"] == 1
        assert by_id["SYN-004"]["item_sales_value"] is None
        assert by_id["SYN-004"]["review_record_count"] == 0
        assert by_id["SYN-005"]["item_sales_value"] is None
        assert by_id["SYN-005"]["review_record_count"] is None
        assert "SYN-998" not in by_id and "SYN-999" not in by_id

        # Original fact model explicitly excludes ingestion metadata from output.
        assert "_loaded_at" not in columns and "_source_filename" not in columns

        # Demonstrate the contract: duplicated upstream review keys multiply
        # fact rows. The source model does not itself enforce upstream uniqueness.
        con.execute(
            "CREATE VIEW duplicated_reviews AS SELECT * FROM fixture_reviews "
            "UNION ALL SELECT * FROM fixture_reviews WHERE order_id='SYN-001'"
        )
        other = dict(DEPENDENCIES, int_order_reviews_summary="duplicated_reviews")
        duplicate_sql = load_original_model(other)
        con.execute("CREATE VIEW fact_with_duplicate_review AS " + duplicate_sql)
        duplicated_count = con.execute(
            "SELECT count(*) FROM fact_with_duplicate_review "
            "WHERE order_id='SYN-001'"
        ).fetchone()[0]
        assert duplicated_count == 2, (
            "Duplicate upstream key no longer multiplies fact rows; investigate changed join"
        )
        print("PASS: original fct_orders SQL retains 5 synthetic lifecycle rows.")
        print("PASS: financial/review fields, nullability, orphan exclusions and grain checked.")
        print("PASS: duplicate upstream key demonstrably creates a grain hazard (2 rows).")
        print("Scope: synthetic pre-aggregated upstream relations, not full dbt/Snowflake.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
