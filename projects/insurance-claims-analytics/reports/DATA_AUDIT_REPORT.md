# DATA AUDIT REPORT

Project: Insurance Claims Analytics – Claims Performance & Fraud Detection

---

# Purpose

This report documents the data audits and technical validations completed during the project.

All successful checks, failures, corrective actions and validation queries remain documented to preserve complete analytical traceability.

---

# DA-001

## Audit

Employee Data Import

## SQL

```sql
SELECT COUNT(*) AS total_agents
FROM employee_data;
