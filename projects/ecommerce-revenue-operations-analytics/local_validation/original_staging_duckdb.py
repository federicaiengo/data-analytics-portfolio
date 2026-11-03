"""Narrow SQL-dialect bridge for four ORIGINAL Snowflake/dbt staging models.

Transforms only exact dbt source() references and TRY_TO_* calls used by the
repository's four order-related staging models. Raises on any unfamiliar
templating or conversion syntax instead of silently changing semantics.

This bridge does NOT establish full Snowflake-to-DuckDB compatibility.
"""
from pathlib import Path
import re

STAGING_DIR = (
    Path(__file__).resolve().parents[1]
    / "dbt/ecommerce_revenue_operations/models/staging"
)

# model filename, original dbt source, local synthetic RAW relation,
# expected (timestamp, number, decimal) conversion occurrence counts.
STAGING_SPEC = {
    "stg_orders": ("orders", "raw_orders", (5, 0, 0)),
    "stg_order_items": ("order_items", "raw_order_items", (1, 1, 2)),
    "stg_order_payments": ("order_payments", "raw_order_payments", (0, 2, 1)),
    "stg_order_reviews": ("order_reviews", "raw_order_reviews", (2, 1, 0)),
}

_TIMESTAMP = re.compile(r"\btry_to_timestamp_ntz\(\s*([a-z_][a-z_0-9]*)\s*\)", re.I)
_NUMBER = re.compile(r"\btry_to_number\(\s*([a-z_][a-z_0-9]*)\s*,\s*38\s*,\s*0\s*\)", re.I)
_DECIMAL = re.compile(r"\btry_to_decimal\(\s*([a-z_][a-z_0-9]*)\s*,\s*12\s*,\s*2\s*\)", re.I)


def render_original_staging(model_name):
    assert model_name in STAGING_SPEC, f"Unsupported staging model: {model_name}"
    source_table, raw_relation, wanted = STAGING_SPEC[model_name]
    path = STAGING_DIR / f"{model_name}.sql"
    sql = path.read_text(encoding="utf-8")
    marker = "{{ source('olist_raw', '" + source_table + "') }}"
    assert sql.count(marker) == 1, f"{model_name}: unexpected source() reference"
    sql = sql.replace(marker, raw_relation)

    sql, timestamps = _TIMESTAMP.subn(r"try_cast(\1 AS TIMESTAMP)", sql)
    sql, numbers = _NUMBER.subn(r"try_cast(\1 AS BIGINT)", sql)
    sql, decimals = _DECIMAL.subn(r"try_cast(\1 AS DECIMAL(12,2))", sql)

    assert (timestamps, numbers, decimals) == wanted, (
        f"{model_name}: cast counts changed: "
        f"{(timestamps, numbers, decimals)} != {wanted}"
    )
    assert not any(token in sql for token in ("{{", "}}", "{%", "%}", "try_to_")), (
        f"{model_name}: unknown dbt/Jinja or Snowflake conversion syntax"
    )
    return sql
