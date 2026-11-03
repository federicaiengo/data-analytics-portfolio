"""Integrated synthetic DuckDB subset of 12 original E-Commerce dbt SQL models.

Four original staging SQL models are dialect-adapted (strict source() and
TRY_TO_* -> TRY_CAST guards) and run on RAW synthetic text fixtures. Seven
further original SQL models are chained: item/payment/review aggregations,
financial reconciliation, lifecycle full-refresh SELECT, fct_orders, and
monthly financial and customer-review marts.

No Snowflake connection or source-data copy, no dbt compilation, MERGE,
watermarking, production performance measurement, or 28-model DAG execution.
"""
from decimal import Decimal
import math
from pathlib import Path
import re

import duckdb

from check_original_intermediate_reconciliation import exact_model_sql
from check_original_lifecycle import load_full_refresh_sql
from original_staging_duckdb import STAGING_SPEC, render_original_staging


ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "dbt/ecommerce_revenue_operations/models"
FACT = MODELS / "marts/core/fct_orders.sql"
MART = MODELS / "marts/business/mart_revenue_financial_reconciliation.sql"
REVIEW_MART = MODELS / "marts/business/mart_customer_experience_reviews.sql"


def render_exact_refs(path, refs):
    sql = path.read_text(encoding="utf-8")
    for ref_name, relation in refs.items():
        marker = "{{ ref('" + ref_name + "') }}"
        assert sql.count(marker) == 1, f"{path.name}: expected one {marker}"
        sql = sql.replace(marker, relation)
    assert not any(token in sql for token in ("{{", "}}", "{%", "%}")), (
        f"{path.name}: unresolved or unexpected dbt template"
    )
    return sql


def render_mart():
    sql = render_exact_refs(MART, {"fct_orders": "integrated_fct_orders"})
    # Only dialect change needed in this subset. Original SQL is untouched.
    sql, count = re.subn(
        r"to_char\(month_start_date,\s*'YYYY-MM'\)",
        "strftime(month_start_date, '%Y-%m')",
        sql, flags=re.IGNORECASE,
    )
    assert count == 1, "Unexpected mart date formatting; review dialect change"
    return sql


def render_customer_reviews_mart():
    sql = render_exact_refs(REVIEW_MART, {"fct_orders": "integrated_fct_orders"})
    sql, count = re.subn(
        r"to_char\(month_start_date,\s*'YYYY-MM'\)",
        "strftime(month_start_date, '%Y-%m')",
        sql, flags=re.IGNORECASE,
    )
    assert count == 1, "Review mart date-format conversion changed"
    return sql


def create_view(con, name, sql):
    # Identifiers are fixed in this file, never derived from external inputs.
    con.execute("CREATE VIEW " + name + " AS " + sql)


def records(con, relation, key):
    result = con.execute("SELECT * FROM " + relation + " ORDER BY " + key)
    fields = [d[0] for d in result.description]
    rows = [dict(zip(fields, row)) for row in result.fetchall()]
    ids = [row[key] for row in rows]
    assert len(ids) == len(set(ids)), f"{relation}: unexpected duplicate grain on {key}"
    return {row[key]: row for row in rows}


def assert_money(value, expected):
    assert value == Decimal(expected), f"money: {value!r} != {expected}"


def main():
    con = duckdb.connect(":memory:")
    try:
        con.execute("""
        CREATE TABLE raw_orders (
            order_id VARCHAR PRIMARY KEY,
            customer_id VARCHAR,
            order_status VARCHAR,
            order_purchase_timestamp VARCHAR,
            order_approved_at VARCHAR,
            order_delivered_carrier_date VARCHAR,
            order_delivered_customer_date VARCHAR,
            order_estimated_delivery_date VARCHAR,
            _loaded_at TIMESTAMP,
            _source_filename VARCHAR,
            _source_row_number INTEGER
        );
        CREATE TABLE raw_order_items (
            order_id VARCHAR,
            order_item_id VARCHAR,
            product_id VARCHAR,
            seller_id VARCHAR,
            shipping_limit_date VARCHAR,
            price VARCHAR,
            freight_value VARCHAR
        );
        CREATE TABLE raw_order_payments (
            order_id VARCHAR,
            payment_sequential VARCHAR,
            payment_type VARCHAR,
            payment_installments VARCHAR,
            payment_value VARCHAR
        );
        CREATE TABLE raw_order_reviews (
            review_id VARCHAR,
            order_id VARCHAR,
            review_score VARCHAR,
            review_comment_title VARCHAR,
            review_comment_message VARCHAR,
            review_creation_date VARCHAR,
            review_answer_timestamp VARCHAR
        );
        """)
        def order(key, status, purchase, *, approved=True, anomaly=False):
            # All values intentionally synthetic and reproducible.
            day = purchase[:10]
            hour = "07:00:00" if anomaly else "09:00:00"
            approval = f"{day} {hour}" if approved else None
            return (
                key, "CUSTOMER-" + key, status, purchase, approval, None,
                None, f"{day} 23:00:00", "2026-03-01 00:00:00",
                "synthetic_only.csv", int(key[-3:]),
            )

        orders = [
            order("SYN-001", "delivered", "2026-01-10 08:00:00"),
            order("SYN-002", "shipped", "2026-01-15 08:00:00", anomaly=True),
            order("SYN-003", "delivered", "2026-01-20 08:00:00", approved=False),
            order("SYN-004", "delivered", "2026-02-02 08:00:00"),
            order("SYN-005", "canceled", "2026-02-05 08:00:00"),
            order("SYN-006", "delivered", "2026-02-10 08:00:00"),
            order("SYN-007", "delivered", "2026-02-12 08:00:00"),
            order("SYN-008", "delivered", "2026-01-25 08:00:00", approved=False),
        ]
        con.executemany(
            "INSERT INTO raw_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            orders,
        )
        # Order 1 has two items and two payments: a raw join would return 4
        # rows and inflate both revenue and the payment amount.
        con.executemany(
            "INSERT INTO raw_order_items VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (order_id, str(index), product_id, seller_id,
                 "2026-03-01 00:00:00", price, freight)
                for index, (order_id, product_id, seller_id, price, freight)
                in enumerate([
                    ("SYN-001", "P1", "SELLER1", "90.00", "5.00"),
                    ("SYN-001", "P2", "SELLER1", "50.00", "5.00"),
                    ("SYN-002", "P3", "SELLER2", "40.00", "5.00"),
                    ("SYN-004", "P4", "SELLER3", "25.00", "5.00"),
                    ("SYN-005", "P5", "SELLER4", "50.00", "5.00"),
                    ("SYN-006", "P6", "SELLER5", "10.00", "0.00"),
                    ("SYN-007", "P7", "SELLER6", "10.00", "0.00"),
                    # Orphan bad source amount must TRY_CAST to NULL;
                    # neither source orphan nor invalid value enters fact.
                    ("SYN-999", "ORPHAN", "OTHER", "bad-price", "0.00"),
                ], start=1)
            ],
        )
        con.executemany(
            "INSERT INTO raw_order_payments VALUES (?, ?, ?, ?, ?)",
            [
                (order_id, str(index), payment_type, str(installments), amount)
                for index, (order_id, payment_type, installments, amount)
                in enumerate([
                    ("SYN-001", "credit_card", 3, "100.00"),
                    ("SYN-001", "voucher", 1, "50.00"),
                    ("SYN-002", "credit_card", 1, "50.00"),
                    ("SYN-003", "voucher", 1, "20.00"),
                    ("SYN-004", "credit_card", 1, "30.00"),
                    ("SYN-006", "credit_card", 1, "10.01"),
                    ("SYN-007", "credit_card", 1, "10.02"),
                    ("SYN-998", "voucher", 1, "bad-payment"),
                ], start=1)
            ],
        )
        con.executemany(
            "INSERT INTO raw_order_reviews VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("RV1", "SYN-001", 4, "Good", "OK", "2026-01-11 08:00:00", "2026-01-12 08:00:00"),
                ("RV2", "SYN-001", 5, None, "Great", "2026-01-13 08:00:00", None),
                ("RV3", "SYN-003", 2, None, "Late", "2026-01-21 08:00:00", None),
                ("RV4", "SYN-004", 3, None, None, "2026-02-03 08:00:00", None),
                ("RV5", "SYN-007", None, None, "Unrated", "2026-02-13 08:00:00", None),
                ("ORPHAN", "SYN-997", "bad-score", None, None, "bad-timestamp", None),
            ],
        )
        # Execute the FOUR original staging SQL models on raw synthetic text.
        # The strict bridge allows only explicitly counted TRY_TO_* casts and
        # source() replacements; original repository SQL remains unchanged.
        for model_name in STAGING_SPEC:
            create_view(con, model_name, render_original_staging(model_name))
        assert con.execute(
            "SELECT typeof(order_purchase_timestamp) FROM stg_orders "
            "WHERE order_id='SYN-001'"
        ).fetchone()[0] == "TIMESTAMP"
        assert con.execute(
            "SELECT price IS NULL FROM stg_order_items WHERE order_id='SYN-999'"
        ).fetchone()[0] is True
        assert con.execute(
            "SELECT payment_value IS NULL FROM stg_order_payments "
            "WHERE order_id='SYN-998'"
        ).fetchone()[0] is True
        assert con.execute(
            "SELECT review_score IS NULL FROM stg_order_reviews "
            "WHERE order_id='SYN-997'"
        ).fetchone()[0] is True
        assert con.execute(
            "SELECT review_creation_date IS NULL FROM stg_order_reviews "
            "WHERE order_id='SYN-997'"
        ).fetchone()[0] is True

        # Lifecycle helper replaces exactly one ref('stg_orders') with this
        # stage relation; the financial model reads the SAME staging view.
        create_view(con, "synthetic_stg_orders", "SELECT * FROM stg_orders")

        create_view(con, "int_order_items_summary",
                    exact_model_sql("int_order_items_summary.sql",
                                    {"stg_order_items": "stg_order_items"}))
        create_view(con, "int_order_payments_summary",
                    exact_model_sql("int_order_payments_summary.sql",
                                    {"stg_order_payments": "stg_order_payments"}))
        create_view(con, "int_order_financial_reconciliation",
                    exact_model_sql(
                        "int_order_financial_reconciliation.sql", {
                            "stg_orders": "stg_orders",
                            "int_order_items_summary": "int_order_items_summary",
                            "int_order_payments_summary": "int_order_payments_summary",
                        },
                    ))
        create_view(con, "int_order_reviews_summary",
                    exact_model_sql(
                        "int_order_reviews_summary.sql",
                        {"stg_order_reviews": "stg_order_reviews"},
                    ))
        create_view(con, "int_orders_lifecycle", load_full_refresh_sql())
        create_view(con, "integrated_fct_orders",
                    render_exact_refs(FACT, {
                        "int_orders_lifecycle": "int_orders_lifecycle",
                        "int_order_financial_reconciliation": "int_order_financial_reconciliation",
                        "int_order_reviews_summary": "int_order_reviews_summary",
                    }))
        create_view(con, "integrated_monthly_mart", render_mart())
        create_view(con, "integrated_customer_reviews_mart", render_customer_reviews_mart())

        # Assert every *connected* model's grain, not just the last table.
        item = records(con, "int_order_items_summary", "order_id")
        payments = records(con, "int_order_payments_summary", "order_id")
        financial = records(con, "int_order_financial_reconciliation", "order_id")
        reviews = records(con, "int_order_reviews_summary", "order_id")
        lifecycle = records(con, "int_orders_lifecycle", "order_id")
        fact = records(con, "integrated_fct_orders", "order_id")
        mart = records(con, "integrated_monthly_mart", "year_month")
        review_mart = records(con, "integrated_customer_reviews_mart", "year_month")
        expected_orders = {f"SYN-{n:03d}" for n in range(1, 9)}
        assert set(financial) == set(lifecycle) == set(fact) == expected_orders
        assert "SYN-998" in payments and "SYN-999" in item
        assert "SYN-997" in reviews
        assert "SYN-998" not in fact and "SYN-999" not in fact and "SYN-997" not in fact
        assert "_loaded_at" not in fact["SYN-001"], "fct_orders leaked ingestion metadata"
        assert item["SYN-001"]["order_item_count"] == 2
        assert payments["SYN-001"]["payment_record_count"] == 2
        assert_money(item["SYN-001"]["item_plus_freight_value"], "150.00")
        assert_money(payments["SYN-001"]["payment_value"], "150.00")
        assert_money(fact["SYN-001"]["item_plus_freight_value"], "150.00")
        assert_money(fact["SYN-001"]["payment_value"], "150.00")
        assert fact["SYN-001"]["financial_values_match"] is True
        assert fact["SYN-001"]["review_record_count"] == 2
        assert fact["SYN-001"]["average_review_score"] == Decimal("4.5")
        assert fact["SYN-001"]["has_multiple_review_scores"] is True
        assert_money(financial["SYN-002"]["payment_minus_item_freight_value"], "5.00")
        assert fact["SYN-002"]["financial_values_match"] is False
        assert lifecycle["SYN-002"]["approval_before_purchase"] is True
        assert fact["SYN-002"]["has_temporal_sequence_anomaly"] is True
        assert fact["SYN-003"]["missing_item_summary"] is True
        assert fact["SYN-003"]["financial_values_match"] is None
        assert fact["SYN-003"]["review_record_count"] == 1
        assert fact["SYN-005"]["missing_payment_summary"] is True
        assert fact["SYN-005"]["financial_values_match"] is None
        assert fact["SYN-005"]["review_record_count"] is None
        assert fact["SYN-006"]["financial_values_match"] is True
        assert_money(fact["SYN-006"]["payment_minus_item_freight_value"], "0.01")
        assert fact["SYN-007"]["financial_values_match"] is False
        assert_money(fact["SYN-007"]["payment_minus_item_freight_value"], "0.02")
        assert fact["SYN-007"]["review_record_count"] == 1
        assert fact["SYN-007"]["average_review_score"] is None
        assert fact["SYN-008"]["missing_item_summary"] is True
        assert fact["SYN-008"]["missing_payment_summary"] is True
        assert fact["SYN-008"]["financial_values_match"] is None

        # Independent hand-computed financial expectations, not generated by
        # copying the same SQL formulas used in the models under test.
        assert set(mart) == set(review_mart) == {"2026-01", "2026-02"}
        jan, feb = mart["2026-01"], mart["2026-02"]
        for month in (jan, feb):
            assert month["order_count"] == 4
            assert month["delivered_order_count"] == 3
            assert month["mismatching_order_count"] == 1
        assert (jan["comparable_order_count"],
                jan["matching_order_count"],
                jan["missing_item_summary_order_count"],
                jan["missing_payment_summary_order_count"]) == (2, 1, 2, 1)
        assert (feb["comparable_order_count"],
                feb["matching_order_count"],
                feb["missing_item_summary_order_count"],
                feb["missing_payment_summary_order_count"]) == (3, 2, 0, 1)
        assert_money(jan["item_plus_freight_value"], "195.00")
        assert_money(jan["payment_value"], "220.00")
        assert_money(jan["absolute_mismatch_value"], "5.00")
        assert_money(feb["item_plus_freight_value"], "105.00")
        assert_money(feb["payment_value"], "50.03")
        assert_money(feb["absolute_mismatch_value"], "0.02")
        assert math.isclose(float(jan["mismatch_rate_pct"]), 50.0, abs_tol=1e-8)
        assert math.isclose(float(feb["mismatch_rate_pct"]), 100 / 3, abs_tol=1e-8)

        naive_count = con.execute("""
            SELECT count(*)
            FROM stg_order_items i
            JOIN stg_order_payments p USING (order_id)
            WHERE i.order_id = 'SYN-001'
        """).fetchone()[0]
        assert naive_count == 4
        assert con.execute("SELECT count(*) FROM integrated_fct_orders").fetchone()[0] == 8
        # Repeat query to ensure determinism without side effects or network.
        assert records(con, "integrated_monthly_mart", "year_month") == mart
        assert records(con, "integrated_customer_reviews_mart", "year_month") == review_mart

        print("PASS: 12 original SQL models chained from synthetic RAW to two monthly marts.")
        print("PASS: 8 orders / 2 months; finance, reviews, lifecycle and both monthly marts verified.")
        print("PASS: source double-count trap (2x2=4) excluded by aggregate-before-JOIN grain.")
        print("Scope: four guarded Snowflake->DuckDB staging cast adaptations and one mart date-format change; no Snowflake, dbt MERGE, or full 28-model run.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
