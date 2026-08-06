# KPI DEFINITIONS

Project: Insurance Claims Analytics – Claims Performance & Fraud Detection

---

# Purpose

This document defines the Key Performance Indicators (KPIs) used throughout the project.

Each KPI includes a business definition to ensure consistent interpretation across SQL analyses, reports and dashboards.

---

# KPI-001

## Name

Total Claims

Definition

Total number of insurance claims.

Business Purpose

Measure overall claim volume.

---

# KPI-002

## Name

Total Claim Amount

Definition

Sum of all claim amounts.

Business Purpose

Measure total financial exposure.

---

# KPI-003

## Name

Average Claim Amount

Definition

Average monetary value of claims.

Business Purpose

Evaluate claim severity.

---

# KPI-004

## Name

High-Value Claims

Definition

Claims with an amount greater than or equal to 95,000.

Business Purpose

Identify cases requiring increased financial monitoring.

---

# KPI-005

## Name

Claims by Insurance Type

Definition

Number of claims for each insurance product.

Business Purpose

Compare business volume across products.

---

# KPI-006

## Name

Average Claim Amount by Insurance Type

Definition

Average claim value calculated separately for each insurance product.

Business Purpose

Compare financial exposure between insurance products.

---

# KPI-007

## Name

Claims without Assigned Vendor

Definition

Claims where `vendor_id` is NULL.

Business Purpose

Monitor operational workflow and vendor involvement.

---

# KPI-008

## Name

Referential Integrity Rate

Definition

Percentage of populated foreign keys correctly linked to parent tables.

Business Purpose

Measure database integrity before business analysis.

---

# Notes

New KPIs must be added only when they support a concrete business question or management decision.