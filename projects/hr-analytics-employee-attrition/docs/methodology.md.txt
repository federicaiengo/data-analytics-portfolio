# Methodology

**Project:** HR Analytics – Employee Attrition & Workforce Insights  
**Repository:** data-analytics-portfolio  
**Document:** Methodology  
**Author:** Federica Iengo  
**Version:** 1.0  
**Status:** In Progress  
**Last Updated:** 2026-08-02

---

# Purpose

This document defines the analytical methodology used throughout the project.

Its purpose is to ensure that every analysis is:

- reproducible;
- traceable;
- internally consistent;
- business-oriented;
- scalable to future projects.

---

# Analytical Workflow

Each analysis follows the same workflow.

1. Define a business question.
2. Write the SQL query.
3. Validate the query result.
4. Interpret the business meaning.
5. Evaluate the evidence.
6. Decide the analytical outcome.
7. Document the result.

No analysis is discarded.

---

# Analysis Classification

Every completed analysis belongs to exactly one category.

## Business Insight (BI)

An analysis that:

- is supported by the data;
- has business value;
- can be clearly explained to stakeholders.

Business Insights are documented in:

```
insights/business_findings.md
```

---

## Exploratory Analysis (EA)

Useful analyses that improve understanding of the dataset but do not satisfy all Business Insight acceptance criteria.

Document:

```
insights/exploratory_analysis.md
```

---

## Rejected Hypothesis (RH)

An initial hypothesis that is not supported by the data.

Rejected hypotheses remain documented because they demonstrate the analytical reasoning process.

---

## Methodological Check (MC)

Analyses performed to validate assumptions, identify confounding variables or verify analytical robustness.

---

# Acceptance Criteria for Business Insights

A Business Insight must satisfy all of the following:

1. Supported by the available data.
2. Relevant for business decision-making.
3. Clearly explainable during a technical or business interview.

Otherwise, the analysis is classified as EA or RH.

---

# Coding Convention

Business Question

```
BQ-001
BQ-002
...
```

Business Insight

```
BI-001
BI-002
...
```

Exploratory Analysis

```
EA-001
EA-002
...
```

Rejected Hypothesis

```
RH-001
RH-002
...
```

Methodological Check

```
MC-001
MC-002
...
```

---

# Pattern Types

Every Business Insight is assigned a Pattern Type.

## Gradient

Risk changes progressively across categories.

Example:

Job Involvement

---

## Threshold

Risk is concentrated in the lowest or highest category.

Example:

Work-Life Balance

Environment Satisfaction

Relationship Satisfaction

---

## Clustered

Risk is concentrated within specific groups.

Example:

Department

Job Role

---

## Lifecycle

Risk changes according to employee tenure or career stage.

Example:

Years at Company

Years in Current Role

---

# Evidence Strength

Every Business Insight receives an Evidence Strength assessment.

Available values:

- Strong
- Moderate
- Limited

Evidence Strength evaluates the quality of the observed evidence, not causal certainty.

---

# Standard Structure of a Business Insight

Every Business Insight contains:

1. Pattern Type
2. Business Question
3. Results
4. Interpretation
5. Business Impact
6. Evidence Strength
7. Reasoning
8. Next Investigation

---

# Standard Structure of SQL Analyses

Each Business Question contains:

- Business Question
- SQL Query
- Results
- Interpretation
- Pattern Type
- Decision
- Link to Business Insight

---

# Decision Outcomes

Every completed analysis ends with one of the following decisions:

- Promoted to Business Insight
- Requires Further Investigation
- Rejected
- Merged into Another Insight
- Methodological Validation Completed

---

# Documentation Principles

The project documents both positive and negative findings.

No completed analysis is removed.

Negative findings strengthen the credibility of the analytical process.

---

# Project Philosophy

The objective is not to maximize the number of Business Insights.

The objective is to produce reliable, reproducible and business-relevant analyses.

Analytical rigor takes priority over the number of reported findings.

Every conclusion must be supported by evidence.

Every analytical decision must remain traceable.

No work performed during the project is lost.
