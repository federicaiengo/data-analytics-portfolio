-- ============================================================
-- E-COMMERCE REVENUE & OPERATIONS ANALYTICS
-- Snowflake RAW CSV file format
-- ============================================================

USE WAREHOUSE ECOMMERCE_WH;
USE DATABASE ECOMMERCE_ANALYTICS;
USE SCHEMA RAW;

CREATE FILE FORMAT IF NOT EXISTS CSV_OLIST_FORMAT
    TYPE = CSV
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    EMPTY_FIELD_AS_NULL = TRUE
    NULL_IF = ('NULL', 'null', '')
    ENCODING = 'UTF8'
    SKIP_BLANK_LINES = TRUE
    ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE;

DESCRIBE FILE FORMAT CSV_OLIST_FORMAT;