# dbt Staging Validation

## Scope

This validation confirms successful execution and testing of the dbt staging layer for the E-Commerce Revenue & Operations Analytics project.

Architecture validated:

RAW Snowflake tables  
→ dbt sources  
→ dbt staging models  
→ automated data tests

---

## Environment

- dbt Core: 1.12.2
- dbt-snowflake: 1.12.0
- Warehouse: `ECOMMERCE_WH`
- Database: `ECOMMERCE_ANALYTICS`
- Target schema: `ANALYTICS`

---

## Staging Model Execution

All nine staging models were successfully materialized as Snowflake views.

| Model | Status |
|---|---|
| stg_customers | PASS |
| stg_geolocation | PASS |
| stg_order_items | PASS |
| stg_order_payments | PASS |
| stg_order_reviews | PASS |
| stg_orders | PASS |
| stg_product_category_name_translation | PASS |
| stg_products | PASS |
| stg_sellers | PASS |

### dbt run result

- Models executed: 9
- PASS: 9
- WARN: 0
- ERROR: 0
- SKIP: 0

---

## Automated Data Tests

The staging layer was tested using dbt generic data tests covering:

- primary identifier uniqueness where appropriate
- required-field completeness
- referential integrity between related entities
- required numeric fields
- required geographic coordinates
- translation-reference integrity

### dbt test result

- Tests executed: 32
- PASS: 32
- WARN: 0
- ERROR: 0
- SKIP: 0

---

## Validation Decisions

Uniqueness tests were applied only where the source grain supports uniqueness.

They were deliberately not applied to fields such as:

- review IDs where duplicate review identifiers are present in the source
- order IDs in order-item, payment and review datasets
- geolocation ZIP prefixes, which contain multiple observations per ZIP

This prevents invalid assumptions about source grain from being encoded as artificial data-quality requirements.

---

## Geolocation Constraint

The staging geolocation model preserves source-level granularity.

No direct one-to-one ZIP assumption is introduced at this layer.

Previous source auditing demonstrated severe row multiplication when customer or seller records are joined directly to the raw geolocation dataset by ZIP prefix.

Therefore, geographic consolidation will be handled explicitly in a downstream model that produces a controlled one-row-per-ZIP representation before geographic enrichment is used in analytical marts.

---

## Result

**STAGING VALIDATION: PASS**

The complete Snowflake staging layer:

- compiles successfully
- executes successfully
- preserves source lineage
- applies analytical data types
- passes all 32 defined automated data tests
- is ready for downstream transformation and dimensional modeling