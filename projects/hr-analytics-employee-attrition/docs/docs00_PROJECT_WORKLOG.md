# PROJECT WORKLOG

Version: 1.0
Project: HR Analytics – Employee Attrition & Workforce Insights

---

# PURPOSE

This document is the operational reference for the entire project.

It defines:

- project rules
- file organization
- naming conventions
- documentation standards
- SQL standards
- workflow
- permanent decisions
- restore points

Every contributor should read this document before modifying the project.

---
---

# TECHNICAL DEBT

## TD-001

Title

Repository Path Refactoring

Status

Pending

Priority

Medium

Description

Some documentation still references the previous repository structure (`insights/`).

The current project standard defines:

- docs/
- reports/

All internal links must be updated after the repository structure is finalized.

Reason

Avoid broken references and keep documentation consistent with the official project structure.

Affected Documents

- Methodology.md
- Any future document referencing `insights/`

Resolution

Perform a global review of internal document references before the repository reaches Version 1.0.


# PROJECT STRUCTURE

```
README.md
│
├── data
│   ├── raw
│   └── cleaned
│
├── sql
│
├── docs
│
├── reports
│
└── assets
```

Rules

- Never mix SQL and documentation.
- Never place reports inside docs.
- Raw data is immutable.

---

# SQL FILES

Naming:

01_data_audit.sql

02_business_analysis.sql

03_exploratory_analysis.sql

...

Rules

- Sequential numbering.
- Never rename existing files.
- Never change numbering already assigned.

---

# DOCUMENTS

One topic = one document.

Never duplicate information.

Documents reference each other.

---

# SQL STANDARD

Each SQL file contains:

Header

Purpose

Queries

Expected Result

Actual Result

Status

Every analysis must be reproducible.

---

# QUERY COMMENTS

Standard:

Purpose

Expected Result

Actual Result

Status

Status values:

PASS

FAIL

---

# DATA RULES

Raw dataset

Never modified.

Clean dataset

Derived from raw.

Every transformation must include:

- reason
- SQL
- validation
- effect

---

# BUSINESS ANALYSIS

Every query answers a business question.

Never write SQL without business purpose.

Workflow:

Business Question

↓

SQL

↓

Evidence

↓

Finding

↓

Business Impact

↓

Recommendation

---

# BUSINESS FINDINGS

Each finding contains:

ID

Title

Business Question

Finding

Evidence

Business Impact

Recommendation

Priority

Confidence

---

# BUSINESS FINDING IDS

Format

BF-001

BF-002

BF-003

...

Rules

Never reuse IDs.

Never renumber.

Deleted IDs remain unused.

---

# REJECTED FINDINGS

Rejected analyses are never deleted.

Store them separately.

Each rejected finding contains:

ID

Query

Reason

Possible future value

---

# EXPLORATORY ANALYSIS

Exploratory work may produce:

accepted findings

rejected findings

future hypotheses

Nothing is discarded.

---

# README RULES

Every folder explains:

Purpose

Contents

Dependencies

---

# REPORTING RULES

Conclusions always follow evidence.

Never present unsupported claims.

Every chart or conclusion must be reproducible.

---

# QUALITY CHECKLIST

Before completing a project:

□ SQL formatted

□ Documentation updated

□ Findings documented

□ IDs verified

□ Evidence linked

□ README updated

□ Reports updated

□ Repository structure verified

---

# DECISION LOG

Permanent decisions

• Raw data never changes.

• Every analysis has business value.

• Findings use progressive IDs.

• Rejected work is archived.

• SQL and documentation remain separated.

• Portfolio must look client-ready.

• Every document should be understandable independently.

• Never lose completed work.

• Produce first, refine later.

---

# WORKFLOW

1.

Understand business problem.

2.

Validate data.

3.

Perform business analysis.

4.

Perform exploratory analysis.

5.

Document findings.

6.

Archive rejected analyses.

7.

Update documentation.

8.

Update reports.

---

# CHANGELOG

Version 1.0

Initial operational standard created.

---

# RESTORE POINTS

Whenever important project decisions are made:

Update this document.

This document is the primary recovery point for methodology, workflow and standards.
---

# PORTFOLIO EVOLUTION PROTOCOL

## Purpose

This project is developed as a client-ready professional portfolio.

Every completed asset must strengthen one or more of the following:

- GitHub portfolio
- CV
- LinkedIn profile
- Job applications
- Technical interviews
- Freelance opportunities

No completed work should remain unpublished without a specific reason.

---

## Asset Lifecycle

Draft

↓

Validated

↓

Published on GitHub

↓

Referenced in README

↓

Referenced in CV (when relevant)

↓

Used in job applications

---

## Repository Philosophy

The repository documents not only the final results but also the analytical process.

Documentation, SQL, reports and project structure should demonstrate professional working methodology.

The repository should appear suitable for delivery to a real client.

---

## Continuous Improvement

The repository is continuously improved.

Existing work is refined when justified, but previous completed work is never discarded.

New documentation should increase clarity without introducing duplication.

---

## Publication Rule

Whenever a significant project component is completed:

1. Update the repository.
2. Update the README if needed.
3. Verify document references.
4. Use the new asset in future applications.
