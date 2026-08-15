-- ============================================================
-- E-COMMERCE REVENUE & OPERATIONS ANALYTICS
-- Snowflake internal stage for RAW source files
-- ============================================================

USE WAREHOUSE ECOMMERCE_WH;
USE DATABASE ECOMMERCE_ANALYTICS;
USE SCHEMA RAW;

CREATE STAGE IF NOT EXISTS OLIST_RAW_STAGE
    FILE_FORMAT = CSV_OLIST_FORMAT;

DESCRIBE STAGE OLIST_RAW_STAGE;

LIST @OLIST_RAW_STAGE;