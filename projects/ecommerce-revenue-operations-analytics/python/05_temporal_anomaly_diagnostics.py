from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

orders = pd.read_csv(
    RAW_DIR / "olist_orders_dataset.csv"
)

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce",
    )


results = []


def summarize_anomaly(name, mask, earlier_col, later_col):
    subset = orders.loc[mask].copy()

    subset["difference_minutes"] = (
        (
            subset[later_col]
            - subset[earlier_col]
        )
        .dt.total_seconds()
        / 60
    )

    count = len(subset)

    if count == 0:
        return

    summary = {
        "anomaly_type": name,
        "rows": count,
        "min_difference_minutes": round(
            subset["difference_minutes"].min(), 2
        ),
        "median_difference_minutes": round(
            subset["difference_minutes"].median(), 2
        ),
        "mean_difference_minutes": round(
            subset["difference_minutes"].mean(), 2
        ),
        "max_difference_minutes": round(
            subset["difference_minutes"].max(), 2
        ),
    }

    results.append(summary)

    print("\n" + "=" * 90)
    print(name)
    print("=" * 90)

    print(f"Rows: {count:,}")

    print(
        "\nDifference in minutes "
        "(negative means timestamp order is reversed):"
    )

    print(
        subset["difference_minutes"]
        .describe()
        .round(2)
        .to_string()
    )

    print("\nBy order status:")

    print(
        subset["order_status"]
        .value_counts()
        .to_string()
    )

    print("\nFirst 10 examples:")

    print(
        subset[
            [
                "order_id",
                "order_status",
                earlier_col,
                later_col,
                "difference_minutes",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


# Carrier timestamp earlier than approval timestamp
mask_carrier_before_approval = (
    orders["order_delivered_carrier_date"].notna()
    & orders["order_approved_at"].notna()
    & (
        orders["order_delivered_carrier_date"]
        < orders["order_approved_at"]
    )
)

summarize_anomaly(
    "carrier_before_approval",
    mask_carrier_before_approval,
    "order_approved_at",
    "order_delivered_carrier_date",
)


# Customer delivery timestamp earlier than carrier timestamp
mask_customer_before_carrier = (
    orders["order_delivered_customer_date"].notna()
    & orders["order_delivered_carrier_date"].notna()
    & (
        orders["order_delivered_customer_date"]
        < orders["order_delivered_carrier_date"]
    )
)

summarize_anomaly(
    "customer_delivery_before_carrier",
    mask_customer_before_carrier,
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
)


summary_df = pd.DataFrame(results)

output_path = (
    REPORTS_DIR
    / "05_temporal_anomaly_diagnostics.csv"
)

summary_df.to_csv(
    output_path,
    index=False,
)

print("\n" + "=" * 90)
print("TEMPORAL ANOMALY DIAGNOSTICS COMPLETE")
print("=" * 90)
print(summary_df.to_string(index=False))
print(f"\nSaved report to: {output_path}")
