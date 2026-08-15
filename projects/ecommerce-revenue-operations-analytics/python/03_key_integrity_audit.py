from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_csv(filename):
    return pd.read_csv(RAW_DIR / filename)


customers = load_csv("olist_customers_dataset.csv")
geolocation = load_csv("olist_geolocation_dataset.csv")
order_items = load_csv("olist_order_items_dataset.csv")
payments = load_csv("olist_order_payments_dataset.csv")
reviews = load_csv("olist_order_reviews_dataset.csv")
orders = load_csv("olist_orders_dataset.csv")
products = load_csv("olist_products_dataset.csv")
sellers = load_csv("olist_sellers_dataset.csv")
translations = load_csv("product_category_name_translation.csv")


audit_rows = []


def add_result(check_name, result_type, value, details=""):
    audit_rows.append(
        {
            "check_name": check_name,
            "result_type": result_type,
            "value": value,
            "details": details,
        }
    )


print("=" * 100)
print("E-COMMERCE REVENUE & OPERATIONS ANALYTICS — KEY INTEGRITY & RELATIONSHIP AUDIT")
print("=" * 100)


# ---------------------------------------------------------------------
# 1. PRIMARY / BUSINESS KEY UNIQUENESS
# ---------------------------------------------------------------------

key_checks = [
    ("customers.customer_id", customers, "customer_id"),
    ("orders.order_id", orders, "order_id"),
    ("products.product_id", products, "product_id"),
    ("sellers.seller_id", sellers, "seller_id"),
    ("translations.product_category_name", translations, "product_category_name"),
]

print("\n1. KEY UNIQUENESS")

for name, df, column in key_checks:
    duplicate_count = int(df[column].duplicated().sum())
    unique_count = int(df[column].nunique(dropna=True))

    add_result(
        name,
        "duplicate_key_rows",
        duplicate_count,
        f"unique_values={unique_count}; total_rows={len(df)}",
    )

    print(
        f"{name:<45} "
        f"duplicates={duplicate_count:<8} "
        f"unique={unique_count:<8} "
        f"rows={len(df)}"
    )


# ---------------------------------------------------------------------
# 2. FOREIGN KEY / RELATIONSHIP INTEGRITY
# ---------------------------------------------------------------------

print("\n2. RELATIONSHIP INTEGRITY")


def orphan_count(child_df, child_col, parent_df, parent_col):
    parent_values = set(parent_df[parent_col].dropna().unique())
    orphan_mask = ~child_df[child_col].isin(parent_values)
    return int(orphan_mask.sum()), int(child_df.loc[orphan_mask, child_col].nunique())


relationship_checks = [
    (
        "orders.customer_id -> customers.customer_id",
        orders,
        "customer_id",
        customers,
        "customer_id",
    ),
    (
        "order_items.order_id -> orders.order_id",
        order_items,
        "order_id",
        orders,
        "order_id",
    ),
    (
        "order_items.product_id -> products.product_id",
        order_items,
        "product_id",
        products,
        "product_id",
    ),
    (
        "order_items.seller_id -> sellers.seller_id",
        order_items,
        "seller_id",
        sellers,
        "seller_id",
    ),
    (
        "payments.order_id -> orders.order_id",
        payments,
        "order_id",
        orders,
        "order_id",
    ),
    (
        "reviews.order_id -> orders.order_id",
        reviews,
        "order_id",
        orders,
        "order_id",
    ),
]

for name, child_df, child_col, parent_df, parent_col in relationship_checks:
    orphan_rows, orphan_keys = orphan_count(
        child_df,
        child_col,
        parent_df,
        parent_col,
    )

    add_result(
        name,
        "orphan_rows",
        orphan_rows,
        f"distinct_orphan_keys={orphan_keys}",
    )

    print(
        f"{name:<60} "
        f"orphan_rows={orphan_rows:<8} "
        f"orphan_keys={orphan_keys}"
    )


# ---------------------------------------------------------------------
# 3. GEOLOCATION DUPLICATES
# ---------------------------------------------------------------------

print("\n3. GEOLOCATION DUPLICATES")

geo_exact_duplicates = int(geolocation.duplicated().sum())
geo_rows_after_exact_dedup = len(geolocation.drop_duplicates())
geo_unique_zip_codes = int(
    geolocation["geolocation_zip_code_prefix"].nunique()
)

add_result(
    "geolocation",
    "exact_duplicate_rows",
    geo_exact_duplicates,
    f"rows_after_exact_dedup={geo_rows_after_exact_dedup}",
)

add_result(
    "geolocation_zip_code_prefix",
    "unique_zip_codes",
    geo_unique_zip_codes,
    f"total_rows={len(geolocation)}",
)

print(f"Exact duplicate rows: {geo_exact_duplicates:,}")
print(f"Rows before deduplication: {len(geolocation):,}")
print(f"Rows after exact deduplication: {geo_rows_after_exact_dedup:,}")
print(f"Unique ZIP prefixes: {geo_unique_zip_codes:,}")


# ---------------------------------------------------------------------
# 4. ORDER MISSING DATES BY STATUS
# ---------------------------------------------------------------------

print("\n4. ORDER MISSING DATES BY STATUS")

date_columns = [
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
]

order_status_missing_rows = []

for date_column in date_columns:
    missing_subset = orders[orders[date_column].isna()]

    grouped = (
        missing_subset
        .groupby("order_status", dropna=False)
        .size()
        .reset_index(name="missing_rows")
    )

    for _, row in grouped.iterrows():
        order_status_missing_rows.append(
            {
                "date_column": date_column,
                "order_status": row["order_status"],
                "missing_rows": int(row["missing_rows"]),
            }
        )

    print(f"\n{date_column}")
    print(grouped.to_string(index=False))


order_status_missing_df = pd.DataFrame(order_status_missing_rows)


# ---------------------------------------------------------------------
# 5. PRODUCT METADATA MISSINGNESS
# ---------------------------------------------------------------------

print("\n5. PRODUCT METADATA MISSINGNESS")

product_metadata_columns = [
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
]

all_metadata_missing_mask = products[product_metadata_columns].isna().all(axis=1)
all_metadata_missing_count = int(all_metadata_missing_mask.sum())

any_metadata_missing_mask = products[product_metadata_columns].isna().any(axis=1)
any_metadata_missing_count = int(any_metadata_missing_mask.sum())

add_result(
    "products",
    "all_core_metadata_missing_rows",
    all_metadata_missing_count,
)

add_result(
    "products",
    "any_core_metadata_missing_rows",
    any_metadata_missing_count,
)

print(f"Rows with ALL four core metadata fields missing: {all_metadata_missing_count:,}")
print(f"Rows with ANY core metadata field missing: {any_metadata_missing_count:,}")


# ---------------------------------------------------------------------
# 6. CATEGORY TRANSLATION COVERAGE
# ---------------------------------------------------------------------

print("\n6. CATEGORY TRANSLATION COVERAGE")

product_categories = set(
    products["product_category_name"].dropna().unique()
)

translated_categories = set(
    translations["product_category_name"].dropna().unique()
)

untranslated_categories = sorted(
    product_categories - translated_categories
)

unused_translation_categories = sorted(
    translated_categories - product_categories
)

add_result(
    "product_category_translation",
    "untranslated_categories",
    len(untranslated_categories),
    ", ".join(untranslated_categories),
)

add_result(
    "product_category_translation",
    "unused_translation_categories",
    len(unused_translation_categories),
    ", ".join(unused_translation_categories),
)

print(f"Product categories: {len(product_categories)}")
print(f"Translated categories: {len(translated_categories)}")
print(f"Missing translations: {len(untranslated_categories)}")

for category in untranslated_categories:
    print(f"  - {category}")


# ---------------------------------------------------------------------
# SAVE OUTPUTS
# ---------------------------------------------------------------------

audit_df = pd.DataFrame(audit_rows)

audit_output = REPORTS_DIR / "03_key_integrity_audit.csv"
audit_df.to_csv(audit_output, index=False)

order_status_output = (
    REPORTS_DIR / "03_order_missing_dates_by_status.csv"
)
order_status_missing_df.to_csv(order_status_output, index=False)

print("\n" + "=" * 100)
print("KEY INTEGRITY & RELATIONSHIP AUDIT COMPLETE")
print("=" * 100)
print(f"Saved report to: {audit_output}")
print(f"Saved report to: {order_status_output}")
