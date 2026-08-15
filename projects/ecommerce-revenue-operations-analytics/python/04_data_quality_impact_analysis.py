from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_csv(filename):
    return pd.read_csv(RAW_DIR / filename)


def safe_pct(part, total):
    if total == 0:
        return 0.0
    return round((part / total) * 100, 4)


customers = load_csv("olist_customers_dataset.csv")
geolocation = load_csv("olist_geolocation_dataset.csv")
order_items = load_csv("olist_order_items_dataset.csv")
orders = load_csv("olist_orders_dataset.csv")
products = load_csv("olist_products_dataset.csv")
sellers = load_csv("olist_sellers_dataset.csv")
translations = load_csv("product_category_name_translation.csv")


summary_rows = []


def add_metric(section, metric, value, details=""):
    summary_rows.append(
        {
            "section": section,
            "metric": metric,
            "value": value,
            "details": details,
        }
    )


print("=" * 100)
print("E-COMMERCE REVENUE & OPERATIONS ANALYTICS — DATA QUALITY IMPACT ANALYSIS")
print("=" * 100)


# =====================================================================
# 1. DELIVERED ORDERS WITH MISSING LIFECYCLE DATES
# =====================================================================

print("\n1. DELIVERED ORDER LIFECYCLE COMPLETENESS")

lifecycle_columns = [
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
]

delivered_orders = orders[
    orders["order_status"].eq("delivered")
].copy()

delivered_orders["missing_lifecycle_fields"] = (
    delivered_orders[lifecycle_columns]
    .isna()
    .sum(axis=1)
)

delivered_anomalies = delivered_orders[
    delivered_orders["missing_lifecycle_fields"] > 0
].copy()

for column in lifecycle_columns:
    count = int(delivered_orders[column].isna().sum())

    add_metric(
        "delivered_lifecycle",
        f"delivered_missing_{column}",
        count,
        f"share_of_delivered_orders={safe_pct(count, len(delivered_orders))}%",
    )

    print(
        f"{column:<40} "
        f"missing={count:<6} "
        f"share={safe_pct(count, len(delivered_orders)):.4f}%"
    )

add_metric(
    "delivered_lifecycle",
    "delivered_orders_with_any_missing_lifecycle_date",
    len(delivered_anomalies),
    f"total_delivered_orders={len(delivered_orders)}",
)

print(
    f"\nDelivered orders with ANY lifecycle date missing: "
    f"{len(delivered_anomalies):,}"
)


# =====================================================================
# 2. TEMPORAL SEQUENCE VALIDATION
# =====================================================================

print("\n2. TEMPORAL SEQUENCE VALIDATION")

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

orders_dates = orders.copy()

for column in date_columns:
    orders_dates[column] = pd.to_datetime(
        orders_dates[column],
        errors="coerce",
    )


temporal_checks = {
    "approval_before_purchase": (
        orders_dates["order_approved_at"].notna()
        & (
            orders_dates["order_approved_at"]
            < orders_dates["order_purchase_timestamp"]
        )
    ),
    "carrier_before_approval": (
        orders_dates["order_delivered_carrier_date"].notna()
        & orders_dates["order_approved_at"].notna()
        & (
            orders_dates["order_delivered_carrier_date"]
            < orders_dates["order_approved_at"]
        )
    ),
    "customer_delivery_before_carrier": (
        orders_dates["order_delivered_customer_date"].notna()
        & orders_dates["order_delivered_carrier_date"].notna()
        & (
            orders_dates["order_delivered_customer_date"]
            < orders_dates["order_delivered_carrier_date"]
        )
    ),
    "customer_delivery_before_purchase": (
        orders_dates["order_delivered_customer_date"].notna()
        & (
            orders_dates["order_delivered_customer_date"]
            < orders_dates["order_purchase_timestamp"]
        )
    ),
    "estimated_delivery_before_purchase": (
        orders_dates["order_estimated_delivery_date"].notna()
        & (
            orders_dates["order_estimated_delivery_date"]
            < orders_dates["order_purchase_timestamp"]
        )
    ),
}


temporal_anomaly_frames = []

for check_name, mask in temporal_checks.items():
    count = int(mask.sum())

    add_metric(
        "temporal_integrity",
        check_name,
        count,
        f"share_of_orders={safe_pct(count, len(orders_dates))}%",
    )

    print(
        f"{check_name:<40} "
        f"rows={count:<6} "
        f"share={safe_pct(count, len(orders_dates)):.4f}%"
    )

    if count > 0:
        temp = orders_dates.loc[
            mask,
            [
                "order_id",
                "order_status",
                *date_columns,
            ],
        ].copy()

        temp.insert(0, "anomaly_type", check_name)
        temporal_anomaly_frames.append(temp)


if temporal_anomaly_frames:
    temporal_anomalies = pd.concat(
        temporal_anomaly_frames,
        ignore_index=True,
    )
else:
    temporal_anomalies = pd.DataFrame(
        columns=[
            "anomaly_type",
            "order_id",
            "order_status",
            *date_columns,
        ]
    )


# =====================================================================
# 3. PRODUCTS WITH MISSING CORE METADATA — BUSINESS IMPACT
# =====================================================================

print("\n3. MISSING PRODUCT METADATA — SALES IMPACT")

product_metadata_columns = [
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
]

missing_product_mask = (
    products[product_metadata_columns]
    .isna()
    .all(axis=1)
)

missing_products = products.loc[
    missing_product_mask,
    ["product_id"],
].copy()

affected_items = order_items[
    order_items["product_id"].isin(
        missing_products["product_id"]
    )
].copy()

affected_products_sold = int(
    affected_items["product_id"].nunique()
)

affected_orders = int(
    affected_items["order_id"].nunique()
)

affected_sales_value = float(
    affected_items["price"].sum()
)

affected_freight_value = float(
    affected_items["freight_value"].sum()
)

total_item_sales_value = float(
    order_items["price"].sum()
)

add_metric(
    "missing_product_metadata",
    "products_with_all_core_metadata_missing",
    len(missing_products),
)

add_metric(
    "missing_product_metadata",
    "affected_products_with_sales",
    affected_products_sold,
)

add_metric(
    "missing_product_metadata",
    "affected_order_item_rows",
    len(affected_items),
)

add_metric(
    "missing_product_metadata",
    "affected_orders",
    affected_orders,
)

add_metric(
    "missing_product_metadata",
    "affected_item_sales_value",
    round(affected_sales_value, 2),
    f"share_of_total_item_sales={safe_pct(affected_sales_value, total_item_sales_value)}%",
)

add_metric(
    "missing_product_metadata",
    "affected_freight_value",
    round(affected_freight_value, 2),
)

print(f"Products with missing core metadata: {len(missing_products):,}")
print(f"Affected products actually sold: {affected_products_sold:,}")
print(f"Affected order-item rows: {len(affected_items):,}")
print(f"Affected orders: {affected_orders:,}")
print(f"Affected item sales value: {affected_sales_value:,.2f}")
print(
    "Share of total item sales value: "
    f"{safe_pct(affected_sales_value, total_item_sales_value):.4f}%"
)


# =====================================================================
# 4. UNTRANSLATED PRODUCT CATEGORIES — IMPACT
# =====================================================================

print("\n4. UNTRANSLATED PRODUCT CATEGORY IMPACT")

product_categories = set(
    products["product_category_name"]
    .dropna()
    .unique()
)

translated_categories = set(
    translations["product_category_name"]
    .dropna()
    .unique()
)

untranslated_categories = sorted(
    product_categories - translated_categories
)

untranslated_products = products[
    products["product_category_name"].isin(
        untranslated_categories
    )
].copy()

untranslated_items = order_items[
    order_items["product_id"].isin(
        untranslated_products["product_id"]
    )
].copy()

untranslated_sales_value = float(
    untranslated_items["price"].sum()
)

add_metric(
    "category_translation",
    "untranslated_categories",
    len(untranslated_categories),
    ", ".join(untranslated_categories),
)

add_metric(
    "category_translation",
    "products_in_untranslated_categories",
    int(untranslated_products["product_id"].nunique()),
)

add_metric(
    "category_translation",
    "orders_affected_by_untranslated_categories",
    int(untranslated_items["order_id"].nunique()),
)

add_metric(
    "category_translation",
    "item_sales_value_in_untranslated_categories",
    round(untranslated_sales_value, 2),
    f"share_of_total_item_sales={safe_pct(untranslated_sales_value, total_item_sales_value)}%",
)

print(f"Untranslated categories: {len(untranslated_categories)}")

for category in untranslated_categories:
    print(f"  - {category}")

print(
    "Products in untranslated categories: "
    f"{untranslated_products['product_id'].nunique():,}"
)

print(
    "Orders affected: "
    f"{untranslated_items['order_id'].nunique():,}"
)

print(
    "Item sales value affected: "
    f"{untranslated_sales_value:,.2f}"
)


# =====================================================================
# 5. GEOLOCATION JOIN MULTIPLICATION RISK
# =====================================================================

print("\n5. GEOLOCATION JOIN MULTIPLICATION RISK")

geo_deduplicated = geolocation.drop_duplicates()

geo_counts_raw = (
    geolocation
    .groupby("geolocation_zip_code_prefix")
    .size()
)

geo_counts_dedup = (
    geo_deduplicated
    .groupby("geolocation_zip_code_prefix")
    .size()
)


# Customers

customer_geo = customers[
    ["customer_id", "customer_zip_code_prefix"]
].copy()

customer_geo["raw_geo_matches"] = (
    customer_geo["customer_zip_code_prefix"]
    .map(geo_counts_raw)
    .fillna(0)
    .astype(int)
)

customer_geo["dedup_geo_matches"] = (
    customer_geo["customer_zip_code_prefix"]
    .map(geo_counts_dedup)
    .fillna(0)
    .astype(int)
)

customer_raw_left_join_rows = int(
    customer_geo["raw_geo_matches"]
    .clip(lower=1)
    .sum()
)

customer_dedup_left_join_rows = int(
    customer_geo["dedup_geo_matches"]
    .clip(lower=1)
    .sum()
)

add_metric(
    "geolocation_join_risk",
    "customer_base_rows",
    len(customer_geo),
)

add_metric(
    "geolocation_join_risk",
    "estimated_customer_rows_after_raw_geo_left_join",
    customer_raw_left_join_rows,
    f"multiplication_factor={round(customer_raw_left_join_rows / len(customer_geo), 2)}x",
)

add_metric(
    "geolocation_join_risk",
    "estimated_customer_rows_after_exact_dedup_geo_left_join",
    customer_dedup_left_join_rows,
    f"multiplication_factor={round(customer_dedup_left_join_rows / len(customer_geo), 2)}x",
)


# Sellers / order items

seller_geo = sellers[
    ["seller_id", "seller_zip_code_prefix"]
].copy()

items_with_seller_zip = order_items[
    ["order_id", "seller_id"]
].merge(
    seller_geo,
    on="seller_id",
    how="left",
)

items_with_seller_zip["raw_geo_matches"] = (
    items_with_seller_zip["seller_zip_code_prefix"]
    .map(geo_counts_raw)
    .fillna(0)
    .astype(int)
)

items_with_seller_zip["dedup_geo_matches"] = (
    items_with_seller_zip["seller_zip_code_prefix"]
    .map(geo_counts_dedup)
    .fillna(0)
    .astype(int)
)

seller_raw_left_join_rows = int(
    items_with_seller_zip["raw_geo_matches"]
    .clip(lower=1)
    .sum()
)

seller_dedup_left_join_rows = int(
    items_with_seller_zip["dedup_geo_matches"]
    .clip(lower=1)
    .sum()
)

add_metric(
    "geolocation_join_risk",
    "order_item_base_rows",
    len(items_with_seller_zip),
)

add_metric(
    "geolocation_join_risk",
    "estimated_order_item_rows_after_raw_geo_left_join",
    seller_raw_left_join_rows,
    f"multiplication_factor={round(seller_raw_left_join_rows / len(items_with_seller_zip), 2)}x",
)

add_metric(
    "geolocation_join_risk",
    "estimated_order_item_rows_after_exact_dedup_geo_left_join",
    seller_dedup_left_join_rows,
    f"multiplication_factor={round(seller_dedup_left_join_rows / len(items_with_seller_zip), 2)}x",
)

add_metric(
    "geolocation_join_risk",
    "maximum_raw_rows_per_zip_prefix",
    int(geo_counts_raw.max()),
)

add_metric(
    "geolocation_join_risk",
    "maximum_exact_dedup_rows_per_zip_prefix",
    int(geo_counts_dedup.max()),
)


print(f"Customer base rows: {len(customer_geo):,}")
print(
    "Estimated rows after RAW geolocation join: "
    f"{customer_raw_left_join_rows:,} "
    f"({customer_raw_left_join_rows / len(customer_geo):.2f}x)"
)

print(
    "Estimated rows after exact-deduplicated geolocation join: "
    f"{customer_dedup_left_join_rows:,} "
    f"({customer_dedup_left_join_rows / len(customer_geo):.2f}x)"
)

print()

print(f"Order-item base rows: {len(items_with_seller_zip):,}")
print(
    "Estimated rows after RAW seller-geolocation join: "
    f"{seller_raw_left_join_rows:,} "
    f"({seller_raw_left_join_rows / len(items_with_seller_zip):.2f}x)"
)

print(
    "Estimated rows after exact-deduplicated seller-geolocation join: "
    f"{seller_dedup_left_join_rows:,} "
    f"({seller_dedup_left_join_rows / len(items_with_seller_zip):.2f}x)"
)


# =====================================================================
# SAVE OUTPUTS
# =====================================================================

summary_df = pd.DataFrame(summary_rows)

summary_output = (
    REPORTS_DIR / "04_data_quality_impact_summary.csv"
)

delivered_output = (
    REPORTS_DIR / "04_delivered_lifecycle_anomalies.csv"
)

temporal_output = (
    REPORTS_DIR / "04_temporal_sequence_anomalies.csv"
)

summary_df.to_csv(
    summary_output,
    index=False,
)

delivered_anomalies.to_csv(
    delivered_output,
    index=False,
)

temporal_anomalies.to_csv(
    temporal_output,
    index=False,
)


print("\n" + "=" * 100)
print("DATA QUALITY IMPACT ANALYSIS COMPLETE")
print("=" * 100)

print(f"Saved report to: {summary_output}")
print(f"Saved report to: {delivered_output}")
print(f"Saved report to: {temporal_output}")
