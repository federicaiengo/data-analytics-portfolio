-- ============================================================
-- E-COMMERCE REVENUE & OPERATIONS ANALYTICS
-- Load staged Olist CSV files into Snowflake RAW tables
-- ============================================================

USE WAREHOUSE ECOMMERCE_WH;
USE DATABASE ECOMMERCE_ANALYTICS;
USE SCHEMA RAW;


-- ============================================================
-- CUSTOMERS
-- ============================================================

COPY INTO OLIST_CUSTOMERS
FROM @OLIST_RAW_STAGE
FILES = ('olist_customers_dataset.csv')
FILE_FORMAT = (FORMAT_NAME = CSV_OLIST_FORMAT)
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;


-- ============================================================
-- GEOLOCATION
-- ============================================================

COPY INTO OLIST_GEOLOCATION
FROM @OLIST_RAW_STAGE
FILES = ('olist_geolocation_dataset.csv')
FILE_FORMAT = (FORMAT_NAME = CSV_OLIST_FORMAT)
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;


-- ============================================================
-- ORDER ITEMS
-- ============================================================

COPY INTO OLIST_ORDER_ITEMS
FROM @OLIST_RAW_STAGE
FILES = ('olist_order_items_dataset.csv')
FILE_FORMAT = (FORMAT_NAME = CSV_OLIST_FORMAT)
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;


-- ============================================================
-- ORDER PAYMENTS
-- ============================================================

COPY INTO OLIST_ORDER_PAYMENTS
FROM @OLIST_RAW_STAGE
FILES = ('olist_order_payments_dataset.csv')
FILE_FORMAT = (FORMAT_NAME = CSV_OLIST_FORMAT)
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;


-- ============================================================
-- ORDER REVIEWS
-- ============================================================

COPY INTO OLIST_ORDER_REVIEWS
FROM @OLIST_RAW_STAGE
FILES = ('olist_order_reviews_dataset.csv')
FILE_FORMAT = (FORMAT_NAME = CSV_OLIST_FORMAT)
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;


-- ============================================================
-- ORDERS
-- ============================================================

COPY INTO OLIST_ORDERS
FROM @OLIST_RAW_STAGE
FILES = ('olist_orders_dataset.csv')
FILE_FORMAT = (FORMAT_NAME = CSV_OLIST_FORMAT)
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;


-- ============================================================
-- PRODUCTS
-- ============================================================

COPY INTO OLIST_PRODUCTS
FROM @OLIST_RAW_STAGE
FILES = ('olist_products_dataset.csv')
FILE_FORMAT = (FORMAT_NAME = CSV_OLIST_FORMAT)
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;


-- ============================================================
-- SELLERS
-- ============================================================

COPY INTO OLIST_SELLERS
FROM @OLIST_RAW_STAGE
FILES = ('olist_sellers_dataset.csv')
FILE_FORMAT = (FORMAT_NAME = CSV_OLIST_FORMAT)
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;


-- ============================================================
-- PRODUCT CATEGORY TRANSLATION
-- ============================================================

COPY INTO PRODUCT_CATEGORY_NAME_TRANSLATION
FROM @OLIST_RAW_STAGE
FILES = ('product_category_name_translation.csv')
FILE_FORMAT = (FORMAT_NAME = CSV_OLIST_FORMAT)
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;


-- ============================================================
-- ROW COUNT VALIDATION
-- Compare Snowflake RAW counts with Python source audit
-- ============================================================

SELECT
    'OLIST_CUSTOMERS' AS table_name,
    COUNT(*) AS actual_rows,
    99441 AS expected_rows,
    COUNT(*) - 99441 AS difference
FROM OLIST_CUSTOMERS

UNION ALL

SELECT
    'OLIST_GEOLOCATION',
    COUNT(*),
    1000163,
    COUNT(*) - 1000163
FROM OLIST_GEOLOCATION

UNION ALL

SELECT
    'OLIST_ORDER_ITEMS',
    COUNT(*),
    112650,
    COUNT(*) - 112650
FROM OLIST_ORDER_ITEMS

UNION ALL

SELECT
    'OLIST_ORDER_PAYMENTS',
    COUNT(*),
    103886,
    COUNT(*) - 103886
FROM OLIST_ORDER_PAYMENTS

UNION ALL

SELECT
    'OLIST_ORDER_REVIEWS',
    COUNT(*),
    99224,
    COUNT(*) - 99224
FROM OLIST_ORDER_REVIEWS

UNION ALL

SELECT
    'OLIST_ORDERS',
    COUNT(*),
    99441,
    COUNT(*) - 99441
FROM OLIST_ORDERS

UNION ALL

SELECT
    'OLIST_PRODUCTS',
    COUNT(*),
    32951,
    COUNT(*) - 32951
FROM OLIST_PRODUCTS

UNION ALL

SELECT
    'OLIST_SELLERS',
    COUNT(*),
    3095,
    COUNT(*) - 3095
FROM OLIST_SELLERS

UNION ALL

SELECT
    'PRODUCT_CATEGORY_NAME_TRANSLATION',
    COUNT(*),
    71,
    COUNT(*) - 71
FROM PRODUCT_CATEGORY_NAME_TRANSLATION

ORDER BY table_name;