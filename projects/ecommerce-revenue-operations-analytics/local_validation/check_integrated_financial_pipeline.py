"""Integrated synthetic DuckDB subset of 15 original E-Commerce dbt SQL models.

Four original staging SQL models are dialect-adapted (strict source() and
TRY_TO_* -> TRY_CAST guards) and run on RAW synthetic text fixtures. Eleven
further original SQL models are chained: item/payment/review aggregations,
financial reconciliation, lifecycle full-refresh SELECT, fct_orders,
fct_order_items, calendar dim_date, and three monthly marts (finance, reviews, deliveries).

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
FACT_ITEMS = MODELS / "marts/core/fct_order_items.sql"
MART = MODELS / "marts/business/mart_revenue_financial_reconciliation.sql"
REVIEW_MART = MODELS / "marts/business/mart_customer_experience_reviews.sql"
DELIVERY_MART = MODELS / "marts/business/mart_delivery_operations.sql"
DIM_DATE = MODELS / "marts/core/dim_date.sql"


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


def render_delivery_mart():
    sql = render_exact_refs(DELIVERY_MART, {"fct_orders": "integrated_fct_orders"})
    sql, count = re.subn(
        r"to_char\(month_start_date,\s*'YYYY-MM'\)",
        "strftime(month_start_date, '%Y-%m')",
        sql, flags=re.IGNORECASE,
    )
    assert count == 1, "Delivery mart date-format conversion changed"
    return sql



def render_dim_date():
    """Execute the original calendar SQL with explicit Snowflake -> DuckDB adaptations."""
    sql = DIM_DATE.read_text(encoding="utf-8")
    for name, relation, expected in (
        ("fct_orders", "integrated_fct_orders", 9),
        ("fct_order_items", "integrated_fct_order_items", 1),
    ):
        marker = "{{ ref('" + name + "') }}"
        assert sql.count(marker) == expected, (
            f"dim_date: expected {expected} references to {name}"
        )
        sql = sql.replace(marker, relation)
    # Intentionally narrow substitutions, each verified against original SQL.
    # The Snowflake/dbt model is never edited by this test harness.
    rewrites = (
        (r"last_day\(max\(date_value\),\s*'month'\)", "last_day(max(date_value))", 1),
        (r"dateadd\(day,\s*1,\s*date_day\)", "(date_day + INTERVAL 1 DAY)::date", 1),
        (r"to_number\(to_char\(date_day,\s*'YYYYMMDD'\)\)",
         "CAST(strftime(date_day, '%Y%m%d') AS INTEGER)", 1),
        (r"to_char\(date_day,\s*'YYYY-MM'\)", "strftime(date_day, '%Y-%m')", 1),
        (r"yearofweekiso\(date_day\)", "date_part('isoyear', date_day)", 1),
        (r"weekiso\(date_day\)", "date_part('week', date_day)", 1),
        (r"dayofweekiso\(date_day\)", "date_part('isodow', date_day)", 2),
        (r"dayofyear\(date_day\)", "date_part('doy', date_day)", 1),
    )
    for pattern, replacement, expected in rewrites:
        sql, count = re.subn(pattern, replacement, sql, flags=re.IGNORECASE)
        assert count == expected, f"dim_date dialect adaptation drift: {pattern}"
    assert not any(token in sql for token in ("{{", "}}", "{%", "%}"))
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
        # Delivery timestamps are intentionally controlled synthetic inputs:
        # one punctual and one late order in Jan; punctual, late and
        # customer-before-carrier anomaly in Feb. Remaining timestamps NULL.
        deliveries = {
            "SYN-001": ("2026-01-10 10:00:00", "2026-01-10 18:00:00"),
            "SYN-003": ("2026-01-20 10:00:00", "2026-01-21 01:00:00"),
            "SYN-004": ("2026-02-02 10:00:00", "2026-02-02 22:00:00"),
            "SYN-006": ("2026-02-10 11:00:00", "2026-02-11 02:00:00"),
            "SYN-007": ("2026-02-12 10:00:00", "2026-02-12 09:30:00"),
        }
        orders = [
            (*order_data[:5],
             *deliveries.get(order_data[0], (None, None)),
             *order_data[7:])
            for order_data in orders
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
        create_view(con, "integrated_fct_order_items",
                    render_exact_refs(FACT_ITEMS, {"stg_order_items": "stg_order_items"}))
        create_view(con, "integrated_dim_date", render_dim_date())
        create_view(con, "integrated_monthly_mart", render_mart())
        create_view(con, "integrated_customer_reviews_mart", render_customer_reviews_mart())
        create_view(con, "integrated_delivery_operations_mart", render_delivery_mart())

        # Assert every *connected* model's grain, not just the last table.
        item = records(con, "int_order_items_summary", "order_id")
        payments = records(con, "int_order_payments_summary", "order_id")
        financial = records(con, "int_order_financial_reconciliation", "order_id")
        reviews = records(con, "int_order_reviews_summary", "order_id")
        lifecycle = records(con, "int_orders_lifecycle", "order_id")
        fact = records(con, "integrated_fct_orders", "order_id")
        item_fact_cursor = con.execute(
            "SELECT * FROM integrated_fct_order_items ORDER BY order_id, order_item_id"
        )
        item_fact_columns = [col[0] for col in item_fact_cursor.description]
        item_fact = [dict(zip(item_fact_columns, row)) for row in item_fact_cursor.fetchall()]
        mart = records(con, "integrated_monthly_mart", "year_month")
        review_mart = records(con, "integrated_customer_reviews_mart", "year_month")
        delivery_mart = records(con, "integrated_delivery_operations_mart", "year_month")

        # Calendar dimension: original dim_date SQL, connected to both facts.
        # Expected full daily spine covers Jan 1 through Mar 31, 2026:
        # the synthetic order timestamps begin in January and estimated
        # delivery / shipping-limit dates extend to March.
        date_cursor = con.execute(
            "SELECT * FROM integrated_dim_date ORDER BY date_day"
        )
        date_cols = [column[0] for column in date_cursor.description]
        date_rows = [dict(zip(date_cols, row)) for row in date_cursor.fetchall()]
        assert len(date_rows) == 90, "Calendar spine must include all 90 days"
        assert len({row["date_day"] for row in date_rows}) == 90
        assert len({row["date_key"] for row in date_rows}) == 90
        assert str(date_rows[0]["date_day"]) == "2026-01-01"
        assert str(date_rows[-1]["date_day"]) == "2026-03-31"
        assert all(row["date_day"] is not None for row in date_rows)
        assert all(row["date_key"] is not None for row in date_rows)
        assert date_rows[0]["date_key"] == 20260101
        assert date_rows[-1]["date_key"] == 20260331
        jan_four = next(row for row in date_rows if str(row["date_day"]) == "2026-01-04")
        assert jan_four["iso_week_number"] == 1
        assert jan_four["iso_week_year"] == 2026
        assert jan_four["iso_day_of_week"] == 7
        assert str(jan_four["week_start_date"]) == "2025-12-29"
        assert jan_four["is_weekend"] is True
        feb_one = next(row for row in date_rows if str(row["date_day"]) == "2026-02-01")
        assert feb_one["date_key"] == 20260201
        assert feb_one["year_month"] == "2026-02"
        assert feb_one["iso_day_of_week"] == 7
        assert feb_one["is_weekend"] is True
        assert str(feb_one["month_start_date"]) == "2026-02-01"
        assert str(feb_one["quarter_start_date"]) == "2026-01-01"
        feb_two = next(row for row in date_rows if str(row["date_day"]) == "2026-02-02")
        assert feb_two["iso_day_of_week"] == 1
        assert feb_two["is_weekend"] is False
        assert len(date_cols) == len(set(date_cols))

        expected_orders = {f"SYN-{n:03d}" for n in range(1, 9)}
        assert set(financial) == set(lifecycle) == set(fact) == expected_orders
        assert "SYN-998" in payments and "SYN-999" in item
        assert "SYN-997" in reviews
        assert "SYN-998" not in fact and "SYN-999" not in fact and "SYN-997" not in fact
        assert "_loaded_at" not in fact["SYN-001"], "fct_orders leaked ingestion metadata"
        assert len(item_fact) == 8, "Item fact must preserve all synthetic items"
        item_keys = [(row["order_id"], row["order_item_id"]) for row in item_fact]
        assert len(set(item_keys)) == 8, "Item fact duplicated a compound business key"
        assert con.execute("SELECT COUNT(*) FROM stg_order_items").fetchone()[0] == 8
        assert con.execute(
            "SELECT COUNT(*) FROM integrated_fct_order_items"
        ).fetchone()[0] == con.execute(
            "SELECT COUNT(*) FROM stg_order_items"
        ).fetchone()[0]
        item_by_order = {}
        for row in item_fact:
            item_by_order.setdefault(row["order_id"], []).append(row)
        assert len(item_by_order["SYN-001"]) == 2
        assert_money(
            sum((r["item_plus_freight_value"] for r in item_by_order["SYN-001"]),
                Decimal("0.00")),
            "150.00"
        )
        for key, expected in (
            ("SYN-002", "45.00"),
            ("SYN-004", "30.00"),
            ("SYN-005", "55.00"),
            ("SYN-006", "10.00"),
            ("SYN-007", "10.00"),
        ):
            assert len(item_by_order[key]) == 1
            assert_money(item_by_order[key][0]["item_plus_freight_value"], expected)
        assert item_by_order["SYN-999"][0]["price"] is None
        assert item_by_order["SYN-999"][0]["item_plus_freight_value"] is None
        assert len(item_by_order["SYN-999"]) == 1
        assert "SYN-999" not in fact, (
            "Orphan item is allowed in the item-grain fact but not the order-grain fact"
        )
        assert "_loaded_at" not in item_fact_columns
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
        assert set(mart) == set(review_mart) == set(delivery_mart) == {"2026-01", "2026-02"}
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

        # Independent, hand-enumerated customer experience expectations.
        # Jan: 001 (two scores 4,5) and 003 (score 2) have reviews.
        # Feb: 004 (score 3) and 007 (NULL score) have reviews.
        jan_review, feb_review = review_mart["2026-01"], review_mart["2026-02"]
        for month in (jan_review, feb_review):
            assert month["order_count"] == 4
            assert month["reviewed_order_count"] == 2
            assert month["unreviewed_order_count"] == 2
            assert math.isclose(float(month["review_coverage_rate_pct"]), 50.0)
        assert jan_review["scored_order_count"] == 2
        assert jan_review["review_record_count"] == 3
        assert math.isclose(float(jan_review["average_review_score"]), 3.25)
        assert (jan_review["low_score_order_count"],
                jan_review["mid_score_order_count"],
                jan_review["high_score_order_count"],
                jan_review["five_score_order_count"]) == (1, 0, 1, 0)
        assert jan_review["multiple_review_record_order_count"] == 1
        assert jan_review["multiple_review_score_order_count"] == 1
        assert jan_review["review_title_order_count"] == 1
        assert jan_review["review_message_order_count"] == 2
        assert math.isclose(float(jan_review["low_score_rate_pct"]), 50.0)
        assert math.isclose(float(jan_review["high_score_rate_pct"]), 50.0)
        assert math.isclose(float(jan_review["review_title_rate_pct"]), 50.0)
        assert math.isclose(float(jan_review["review_message_rate_pct"]), 100.0)
        assert feb_review["scored_order_count"] == 1
        assert feb_review["review_record_count"] == 2
        assert math.isclose(float(feb_review["average_review_score"]), 3.0)
        assert (feb_review["low_score_order_count"],
                feb_review["mid_score_order_count"],
                feb_review["high_score_order_count"],
                feb_review["five_score_order_count"]) == (0, 1, 0, 0)
        assert feb_review["multiple_review_record_order_count"] == 0
        assert feb_review["multiple_review_score_order_count"] == 0
        assert feb_review["review_title_order_count"] == 0
        assert feb_review["review_message_order_count"] == 1
        assert math.isclose(float(feb_review["review_message_rate_pct"]), 50.0)
        for month_id in ("2026-01", "2026-02"):
            assert review_mart[month_id]["order_count"] == mart[month_id]["order_count"]

        # Independently enumerated delivery operations KPI expectations.
        # Jan delivered: 001 on-time, 003 late, 008 no delivery timestamps.
        # Jan shipped 002 has approval before purchase: one temporal anomaly.
        # Feb delivered: 004 on-time, 006 late, 007 before-carrier anomaly.
        jan_delivery, feb_delivery = delivery_mart["2026-01"], delivery_mart["2026-02"]
        expected_delivery = {
            "2026-01": {
                "order_count": 4,
                "delivered_order_count": 3,
                "punctuality_comparable_order_count": 2,
                "on_time_or_early_order_count": 1,
                "late_delivery_order_count": 1,
                "punctuality_not_comparable_order_count": 1,
                "delivered_missing_approval_count": 2,
                "delivered_missing_carrier_timestamp_count": 1,
                "delivered_missing_customer_delivery_count": 1,
                "temporal_anomaly_order_count": 1,
                "carrier_before_approval_order_count": 0,
                "customer_delivery_before_carrier_order_count": 0,
                "valid_purchase_to_approval_order_count": 1,
                "valid_approval_to_carrier_order_count": 1,
                "valid_carrier_to_customer_order_count": 2,
                "valid_purchase_to_customer_order_count": 2,
            },
            "2026-02": {
                "order_count": 4,
                "delivered_order_count": 3,
                "punctuality_comparable_order_count": 3,
                "on_time_or_early_order_count": 2,
                "late_delivery_order_count": 1,
                "punctuality_not_comparable_order_count": 0,
                "delivered_missing_approval_count": 0,
                "delivered_missing_carrier_timestamp_count": 0,
                "delivered_missing_customer_delivery_count": 0,
                "temporal_anomaly_order_count": 1,
                "carrier_before_approval_order_count": 0,
                "customer_delivery_before_carrier_order_count": 1,
                "valid_purchase_to_approval_order_count": 4,
                "valid_approval_to_carrier_order_count": 3,
                "valid_carrier_to_customer_order_count": 2,
                "valid_purchase_to_customer_order_count": 3,
            },
        }
        for month_id, expected_fields in expected_delivery.items():
            delivery = delivery_mart[month_id]
            for field, expected in expected_fields.items():
                assert delivery[field] == expected, (
                    f"Delivery {month_id} {field}: {delivery[field]} != {expected}"
                )
            assert delivery["order_count"] == mart[month_id]["order_count"]
            assert delivery["order_count"] == review_mart[month_id]["order_count"]
        assert math.isclose(float(jan_delivery["late_delivery_rate_pct"]), 50.0)
        assert math.isclose(float(jan_delivery["on_time_or_early_rate_pct"]), 50.0)
        assert math.isclose(float(feb_delivery["late_delivery_rate_pct"]), 100 / 3)
        assert math.isclose(float(feb_delivery["on_time_or_early_rate_pct"]), 200 / 3)
        assert math.isclose(float(jan_delivery["average_purchase_to_approval_hours"]), 1.0)
        assert math.isclose(float(jan_delivery["average_approval_to_carrier_hours"]), 1.0)
        assert math.isclose(float(jan_delivery["average_carrier_to_customer_hours"]), 11.5)
        assert math.isclose(float(jan_delivery["average_purchase_to_customer_hours"]), 13.5)
        assert math.isclose(float(feb_delivery["average_purchase_to_approval_hours"]), 1.0)
        assert math.isclose(float(feb_delivery["average_approval_to_carrier_hours"]), 4 / 3)
        assert math.isclose(float(feb_delivery["average_carrier_to_customer_hours"]), 13.5)
        assert math.isclose(float(feb_delivery["average_purchase_to_customer_hours"]), 33.5 / 3)
        assert lifecycle["SYN-007"]["customer_delivery_before_carrier"] is True
        assert lifecycle["SYN-007"]["has_temporal_sequence_anomaly"] is True
        # Original mart still counts 007 as on-time; a data-quality flag is
        # separate from its punctuality aggregation. This is NOT an audit of
        # valid operational delivery performance.
        assert feb_delivery["on_time_or_early_order_count"] == 2
        assert feb_delivery["temporal_anomaly_order_count"] == 1
        # Alternative data-quality policy experiment: exclude impossible
        # timeline rows from punctuality's numerator AND denominator.
        # It does not modify the original delivery mart or historical KPIs.
        strict_delivery = con.execute("""
            SELECT
                strftime(date_trunc('month', order_purchase_timestamp), '%Y-%m')
                    AS year_month,
                count(*) FILTER (
                    WHERE order_status = 'delivered'
                      AND order_delivered_customer_date IS NOT NULL
                      AND order_estimated_delivery_date IS NOT NULL
                ) AS original_comparable,
                count(*) FILTER (
                    WHERE order_status = 'delivered'
                      AND order_delivered_customer_date IS NOT NULL
                      AND order_estimated_delivery_date IS NOT NULL
                      AND coalesce(has_temporal_sequence_anomaly, false)
                ) AS excluded_temporal_anomalies,
                count(*) FILTER (
                    WHERE order_status = 'delivered'
                      AND order_delivered_customer_date IS NOT NULL
                      AND order_estimated_delivery_date IS NOT NULL
                      AND NOT coalesce(has_temporal_sequence_anomaly, false)
                ) AS strict_comparable,
                count(*) FILTER (
                    WHERE order_status = 'delivered'
                      AND order_delivered_customer_date IS NOT NULL
                      AND order_estimated_delivery_date IS NOT NULL
                      AND NOT coalesce(has_temporal_sequence_anomaly, false)
                      AND order_delivered_customer_date
                          <= order_estimated_delivery_date
                ) AS strict_on_time
            FROM integrated_fct_orders
            GROUP BY 1
            ORDER BY 1
        """).fetchall()
        assert strict_delivery == [
            ("2026-01", 2, 0, 2, 1),
            ("2026-02", 3, 1, 2, 1),
        ], f"Strict delivery policy fixture drift: {strict_delivery!r}"
        for month_id, original, excluded, valid, timely in strict_delivery:
            assert original == valid + excluded
            assert timely <= valid
            assert original == delivery_mart[month_id]["punctuality_comparable_order_count"]
            if month_id == "2026-02":
                assert math.isclose(
                    float(delivery_mart[month_id]["on_time_or_early_rate_pct"]), 200 / 3
                )
                assert math.isclose(timely * 100.0 / valid, 50.0)
        # February original: on-time 2/3 (66.67%); alternative excluding
        # one anomalous delivery: 1/2 (50%). Policy choice remains open.


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
        assert records(con, "integrated_delivery_operations_mart", "year_month") == delivery_mart

        print("PASS: 14 original SQL models chained from synthetic RAW through item fact and three monthly marts.")
        print("PASS: 8 orders / 2 months; finance, reviews, lifecycle and all three monthly marts verified.")
        print("PASS: item-fact compound grain, including allowed orphan row, and original order-fact grain.")
        print("PASS: original 2/3 vs policy-excluded 1/2 February delivery punctuality distinguished.")
        print("PASS: source double-count trap (2x2=4) excluded by aggregate-before-JOIN grain.")
        print("Scope: guarded Snowflake->DuckDB staging casts and three mart date-format substitutions; no Snowflake, dbt MERGE, or full 28-model run.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
