# DATA MODEL

Project: Insurance Claims Analytics – Claims Performance & Fraud Detection

---

# Purpose

This document describes the relational structure of the project database and the relationships between its tables.

It serves as the reference for SQL development, business analysis and documentation.

---

# Database Overview

The project uses a relational database composed of three main tables.

## insurance_data

Contains one record for each insurance claim.

Primary Key:

- transaction_id

Foreign Keys:

- agent_id → employee_data.agent_id
- vendor_id → vendor_data.vendor_id (nullable)

Business Role:

Central fact table used for all business analyses.

---

## employee_data

Contains information about insurance agents.

Primary Key:

- agent_id

Business Role:

Reference table used to analyse agent performance and claim allocation.

---

## vendor_data

Contains information about vendors involved in insurance claims.

Primary Key:

- vendor_id

Business Role:

Reference table used to evaluate vendor participation and operational performance.

---

# Entity Relationships

employee_data (1)
        │
        │ agent_id
        ▼
insurance_data
        ▲
        │ vendor_id (nullable)
        │
vendor_data (1)

---

# Relationship Notes

- Every insurance claim is associated with a valid agent.
- Vendor assignment is optional.
- Claims without a vendor are considered valid business records and are not treated as referential integrity violations.

---

# Current Validation Status

Validated:

- Primary key uniqueness
- Referential integrity
- Nullable vendor relationship

The relational model has been verified during the Data Audit phase.