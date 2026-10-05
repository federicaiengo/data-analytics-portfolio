# Federica Iengo — Data Analytics Portfolio

Data Analyst focused on **SQL, Snowflake, dbt, Power BI, analytics engineering, data quality and business intelligence**.

This portfolio contains practical end-to-end projects covering source-data validation, warehouse loading, dimensional modeling, incremental ELT workflows, automated testing, reconciliation, KPI analysis and stakeholder-oriented reporting.

## Featured Projects

### AI Search Visibility Lab
**Python · GEO/AEO · AI Search Measurement · Citation Analysis · Evidence Provenance**

Reproducible framework for measuring brand mentions, citations, source diversity, retrieval consistency and competitor share of voice across AI-generated answers. Built around immutable evidence logging and a strict **correlation ≠ causation** interpretation rule, with a science/health-tech query set.

[Open the AI Search Visibility Lab](projects/ai-search-visibility-lab/)

### E-Commerce Revenue & Operations Analytics
**Snowflake · dbt · Power BI · Python/pandas · Data Quality**

End-to-end analytics project built on nine Olist e-commerce datasets.

Highlights:
- 28-model dbt architecture across staging, intermediate, dimensional/fact and business-mart layers
- Full regression baseline: **249/249 PASS**
- Snowflake RAW ingestion metadata and historical-load provenance
- True dbt incremental order-lifecycle model using `unique_key`, `MERGE`, `_loaded_at` watermarking and schema-change handling
- Idempotent reruns empirically validated with stable row counts and no duplicate order IDs
- Financial reconciliation across **98,665 comparable orders**, with **303 mismatches (~0.3071%)**
- **1,382 temporal-sequence anomalies** identified and preserved for investigation
- Four-page Power BI report covering executive KPIs, reconciliation, operations and customer experience

[Open the E-Commerce project](projects/ecommerce-revenue-operations-analytics/)

### Insurance Claims Analytics
**PostgreSQL · SQL · Tableau · Risk & Exposure Analysis**

- Built a relational PostgreSQL database from claims, agents and vendors datasets
- Validated imports, uniqueness and referential integrity
- Developed KPI analysis using CTEs, window functions, ranking and NTILE
- Quantified exposure concentration using Pareto analysis, Lorenz Curve and Gini coefficient
- Published an executive Tableau dashboard

[Open the Insurance project](projects/insurance-claims-analytics/)

### HR Analytics
**SQL · SQLite · Workforce Analytics**

- Built an end-to-end SQL/SQLite workflow on 1,470 employee records
- Audited and validated data quality
- Analyzed attrition, overtime, role, department, tenure and satisfaction patterns
- Documented methodology and business findings in Git/GitHub

[Open the HR project](projects/hr-analytics-employee-attrition/)

## Core Technical Skills

- SQL & PostgreSQL
- Snowflake & Data Warehousing
- dbt Core / dbt-snowflake
- Incremental ELT modeling
- MERGE / upsert workflows
- Watermark-based incremental loading
- Data quality & reconciliation
- Dimensional modeling & star schema
- Python / pandas
- Power BI & DAX
- Tableau
- Git & GitHub
- Technical documentation

## Certifications

- **Dabudai Advanced GEO Specialist** — Dabudai, issued October 2026 · **29/30** · Credential ID `DABUDAI-GEO-2026-0215` · [Verify credential](https://talent.dabud.ai/c/DABUDAI-GEO-2026-0215)

## Focus Areas

Data Analytics · Analytics Engineering · Business Intelligence · Data Quality · GEO / AEO · AI Search Visibility · Reconciliation · Data Platform / Operations

---

**Federica Iengo**  
Italy · Remote International
