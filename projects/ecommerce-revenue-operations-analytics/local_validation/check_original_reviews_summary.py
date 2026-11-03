"""Synthetic-only DuckDB test for unchanged int_order_reviews_summary.sql.

Exercises the repository's original aggregation with one exact dbt ref()
replacement; no Snowflake credentials, source dumps, or production data.
"""
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import duckdb

MODEL = (
    Path(__file__).resolve().parents[1]
    / "dbt/ecommerce_revenue_operations/models/intermediate/int_order_reviews_summary.sql"
)


def main():
    sql = MODEL.read_text(encoding="utf-8")
    marker = "{{ ref('stg_order_reviews') }}"
    assert sql.count(marker) == 1, "Review summary dependency changed; review required"
    sql = sql.replace(marker, "fixture_order_reviews")
    assert "{{" not in sql and "{%" not in sql and "}}" not in sql and "%}" not in sql, (
        "Unexpected unresolved dbt/Jinja syntax"
    )

    con = duckdb.connect(":memory:")
    try:
        con.execute("""
            CREATE TABLE fixture_order_reviews (
                review_id VARCHAR,
                order_id VARCHAR,
                review_score INTEGER,
                review_comment_title VARCHAR,
                review_comment_message VARCHAR,
                review_creation_date TIMESTAMP,
                review_answer_timestamp TIMESTAMP
            )
        """)
        con.executemany(
            "INSERT INTO fixture_order_reviews VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("RV1", "SYN-001", 3, "Title 1", "Message 1", "2026-01-01 08:00:00", "2026-01-02 08:00:00"),
                ("RV2", "SYN-001", 4, None, None, "2026-01-03 08:00:00", None),
                ("RV2", "SYN-001", 5, "Title 3", "Message 3", "2026-01-02 08:00:00", "2026-01-04 08:00:00"),
                ("RV3", "SYN-002", 2, None, None, "2026-01-01 08:00:00", None),
                ("RV4", "SYN-003", None, None, "Text", None, None),
                ("RV5", "SYN-999", 1, "Orphan", None, "2026-02-01 08:00:00", None),
            ],
        )
        con.execute("CREATE VIEW original_review_summary_under_test AS " + sql)
        cursor = con.execute("SELECT * FROM original_review_summary_under_test ORDER BY order_id")
        names = [col[0] for col in cursor.description]
        rows = [dict(zip(names, row)) for row in cursor.fetchall()]
        assert [r["order_id"] for r in rows] == [
            "SYN-001", "SYN-002", "SYN-003", "SYN-999"
        ], "Review summary unexpectedly lost or duplicated an order grain"
        summary = {r["order_id"]: r for r in rows}
        one = summary["SYN-001"]
        assert one["review_record_count"] == 3
        assert one["distinct_review_id_count"] == 2
        assert one["average_review_score"] == 4
        assert one["minimum_review_score"] == 3
        assert one["maximum_review_score"] == 5
        assert one["distinct_review_score_count"] == 3
        assert one["has_multiple_review_scores"] is True
        assert one["review_title_record_count"] == 2
        assert one["review_message_record_count"] == 2
        assert one["has_review_title"] is True
        assert one["has_review_message"] is True
        assert one["first_review_creation_date"] == datetime(2026, 1, 1, 8)
        assert one["last_review_creation_date"] == datetime(2026, 1, 3, 8)
        assert one["first_review_answer_timestamp"] == datetime(2026, 1, 2, 8)
        assert one["last_review_answer_timestamp"] == datetime(2026, 1, 4, 8)
        two = summary["SYN-002"]
        assert two["review_record_count"] == 1
        assert two["average_review_score"] == 2
        assert two["distinct_review_score_count"] == 1
        assert two["has_multiple_review_scores"] is False
        assert two["has_review_title"] is False
        assert two["has_review_message"] is False
        three = summary["SYN-003"]
        assert three["review_record_count"] == 1
        assert three["average_review_score"] is None
        assert three["distinct_review_score_count"] == 0
        assert three["has_multiple_review_scores"] is False
        assert three["review_message_record_count"] == 1
        assert three["has_review_message"] is True
        assert summary["SYN-999"]["review_record_count"] == 1
        print("PASS: unchanged original review summary SQL, 6 synthetic review rows.")
        print("PASS: grain, duplicate review IDs, score variation, NULLs, timestamps, comments.")
        print("Scope: no real source data, no original staging or downstream fact integration.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
