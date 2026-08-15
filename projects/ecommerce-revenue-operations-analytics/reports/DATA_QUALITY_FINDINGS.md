# Data Quality Findings

## Purpose

This document summarizes the material data-quality issues identified during the initial profiling, integrity checks, and impact analysis of the Olist e-commerce dataset.

A potential issue is promoted to a Data Quality Finding only when the analysis shows that it can materially affect analytical results, KPI reliability, data modeling, or business interpretation.

---

## DQF-001 — Geolocation Join Multiplication Risk

### Observation

The raw geolocation dataset contains:

* 1,000,163 rows
* 261,831 exact duplicate rows
* 19,015 unique ZIP-code prefixes

After removing exact duplicate rows, 738,332 geolocation records remain.

However, exact deduplication does not make `geolocation_zip_code_prefix` unique.

### Impact Analysis

A direct join between customer records and raw geolocation data using ZIP-code prefix would increase:

* 99,441 customer rows to approximately 15,083,733 rows
* multiplication factor: **151.69x**

Even after exact deduplication:

* 99,441 customer rows would become approximately 10,328,006 rows
* multiplication factor: **103.86x**

The same issue affects seller-level joins through order items:

* 112,650 order-item rows
* approximately 16,252,672 rows after joining raw geolocation data
* multiplication factor: **144.28x**

After exact geolocation deduplication:

* approximately 12,241,964 rows
* multiplication factor: **108.67x**

### Risk

Using ZIP-code prefix as though it were a unique geographic key would produce severe row multiplication.

This could inflate:

* order counts
* customer counts
* sales values
* freight values
* seller metrics
* geographic KPIs

The issue cannot be solved by exact duplicate removal alone.

### Analytical Decision

Do not join the transactional model directly to the raw geolocation dataset using ZIP-code prefix.

A geographic dimension with an explicitly defined one-row-per-ZIP grain must be created before the data is used in downstream analytical models.

### Status

**Confirmed material data-quality / modeling risk.**

---

## DQF-002 — Missing Product Metadata Has Measurable Sales Impact

### Observation

610 products have all four core descriptive metadata fields missing:

* `product_category_name`
* `product_name_lenght`
* `product_description_lenght`
* `product_photos_qty`

All 610 affected products appear in actual sales transactions.

### Impact Analysis

Affected records represent:

* 610 products sold
* 1,603 order-item rows
* 1,451 distinct orders
* BRL 179,535.28 in item sales value
* BRL 28,169.81 in freight value

The affected item sales represent approximately:

**1.3209% of total item sales value**

### Risk

Dropping products with missing descriptive metadata during cleaning or category-based modeling would remove genuine commercial activity.

This would understate revenue-related measures and could bias:

* category analysis
* product mix analysis
* order-level revenue
* customer purchasing analysis
* seller performance analysis

### Analytical Decision

Products with incomplete metadata must remain in transactional calculations.

Missing categorical attributes should be handled explicitly, for example through an `Unknown` or equivalent analytical category rather than removing the associated transactions.

### Status

**Confirmed material data-quality issue with measurable business impact.**

---

## DQF-003 — Order Lifecycle Timestamp Inconsistencies

### Observation

Temporal validation identified records whose event timestamps do not follow the expected order lifecycle sequence.

Two relevant anomaly groups were identified.

#### Carrier timestamp before approval

* 1,359 orders
* approximately 1.3666% of all orders

Difference between carrier and approval timestamps:

* median: approximately **-1,030 minutes**
* mean: approximately **-1,485 minutes**
* minimum observed difference: approximately **-246,555 minutes**

The median inversion is therefore approximately **17.2 hours**.

#### Customer delivery before carrier timestamp

* 23 orders
* approximately 0.0231% of all orders

Difference between customer-delivery and carrier timestamps:

* median: approximately **-2,392 minutes**
* mean: approximately **-4,707 minutes**
* minimum observed difference: approximately **-23,178 minutes**

The median inversion is approximately **39.9 hours**.

### Risk

These records can distort lifecycle and operational KPIs such as:

* approval-to-carrier time
* carrier-to-customer delivery time
* fulfillment duration
* logistics performance
* SLA analysis

The magnitude of several timestamp inversions indicates that the issue should not be treated as simple second-level or minute-level timestamp noise.

### Interpretation Constraint

The analysis establishes that the recorded timestamps are inconsistent with the expected analytical event sequence.

It does **not** establish that the physical business process necessarily occurred in the recorded order.

Possible explanations may include source-system semantics, delayed event registration, integration behavior, or source-data errors.

### Analytical Decision

Affected records should be flagged before lifecycle-duration metrics are calculated.

They should not be silently corrected without an independently justified business rule.

### Status

**Confirmed temporal data-quality issue affecting lifecycle analytics.**

---

# Secondary Data Quality Observations

## Delivered Orders with Missing Lifecycle Dates

Among 96,478 delivered orders, 23 contain at least one missing lifecycle timestamp.

Observed missing values include:

* 14 missing `order_approved_at`
* 2 missing `order_delivered_carrier_date`
* 8 missing `order_delivered_customer_date`

The incidence is very small relative to total delivered-order volume.

### Classification

Valid data-quality issue, but currently considered **low materiality** compared with the primary findings.

---

## Product Category Translation Coverage

The product dataset contains 73 non-null category values, while the translation table contains 71 categories.

Two product categories are not represented in the translation table:

* `pc_gamer`
* `portateis_cozinha_e_preparadores_de_alimentos`

Impact:

* 13 products
* 22 affected orders
* BRL 5,514.48 in item sales value
* approximately 0.0406% of total item sales

### Classification

Confirmed mapping gap, but currently considered **low materiality**.

The categories should still be handled explicitly during transformation to prevent null English-category labels.

---

# Integrity Checks with No Material Issue Identified

The key-integrity audit found no orphan records in the tested core relationships:

* orders → customers
* order items → orders
* order items → products
* order items → sellers
* payments → orders
* reviews → orders

The principal master keys tested were also unique:

* `customer_id`
* `order_id`
* `product_id`
* `seller_id`
* translation `product_category_name`

These results provide a strong basis for building the subsequent analytical data model.

---

# Current Data Quality Decisions

The following transformation principles will be carried into the warehouse/modeling stage:

1. Preserve genuine sales transactions even when product descriptive metadata is incomplete.
2. Do not use raw geolocation ZIP prefixes as a unique join key.
3. Create an explicitly defined geographic analytical grain before joining location data.
4. Flag temporal lifecycle anomalies before duration-based KPI calculations.
5. Do not silently repair inconsistent timestamps without a defensible business rule.
6. Preserve untranslated categories and handle missing mappings explicitly.
7. Maintain a clear distinction between source-data observations, confirmed issues, and business findings.
