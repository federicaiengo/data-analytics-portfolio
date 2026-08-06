# DATA QUALITY RULES

Project: Insurance Claims Analytics – Claims Performance & Fraud Detection

---

# Purpose

This document defines the data quality rules applied throughout the project.

The objective is to ensure that every business analysis is based on reliable and validated data.

---

# Rule DQ-001

## Name

Dataset Import Validation

Requirement

All expected datasets must be successfully imported before any analysis begins.

Validation

Record count verification.

Status

Implemented.

---

# Rule DQ-002

## Name

Primary Key Uniqueness

Requirement

Primary keys must contain no duplicate values.

Validation

Duplicate detection queries.

Status

Implemented.

---

# Rule DQ-003

## Name

Referential Integrity

Requirement

Every populated foreign key must reference an existing parent record.

Validation

LEFT JOIN integrity checks.

Status

Implemented.

---

# Rule DQ-004

## Name

Nullable Vendor Relationship

Requirement

A NULL vendor_id is considered a valid business condition.

It does not represent a referential integrity violation.

Validation

Confirmed during Data Audit.

Status

Implemented.

---

# Rule DQ-005

## Name

Business Evidence

Requirement

Every business conclusion must be supported by SQL evidence.

Validation

Business Findings reference SQL analyses.

Status

Implemented.

---

# Rule DQ-006

## Name

Rejected Analyses

Requirement

Analyses that do not produce actionable evidence must be documented rather than deleted.

Validation

Tracked through Business Rejected Findings.

Status

Implemented.

---

# Notes

These rules represent the minimum data quality standards required before producing business recommendations.