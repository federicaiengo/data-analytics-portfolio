# Business Findings

**Project:** HR Analytics – Employee Attrition & Workforce Insights  
**Repository:** data-analytics-portfolio  
**Document:** Business Findings  
**Author:** Federica Iengo  
**Status:** In Progress  
**Last Updated:** 2026-08-02  

This document records the business insights identified during the analysis of the IBM HR Analytics Employee Attrition & Performance dataset.

Each insight includes:

- Business Question
- Results
- Interpretation
- Business Impact
- Evidence Strength
- Reasoning
- Next Investigation

Reference system:

- `BQ-XXX` = Business Question
- `BI-XXX` = Business Insight

The findings describe associations observed in the dataset and must not be interpreted as proof of causality unless explicitly stated.

---

# BI-001 — Overtime and Employee Attrition

## Business Question

**BQ-001**

Are employees working overtime more likely to leave the company?

## Results

| OverTime | Employees | Attrition | Attrition Rate |
|----------|----------:|----------:|---------------:|
| No | 1054 | 110 | 10.44% |
| Yes | 416 | 127 | 30.53% |

## Interpretation

Employees working overtime show an attrition rate approximately three times higher than employees who do not work overtime.

The dataset shows a strong association between overtime and employee attrition.

This observation does not demonstrate causality.

## Business Impact

Overtime should be monitored as a potential employee-retention risk indicator.

Possible areas for further investigation include:

- workload distribution;
- staffing levels;
- management practices;
- work-life balance initiatives.

## Evidence Strength

**Strong**

## Reasoning

The difference between the two groups is substantial: 30.53% compared with 10.44%.

Both groups contain a meaningful number of observations, supporting the relevance of the association within this dataset.

## Next Investigation

Evaluate whether the association between overtime and attrition remains consistent across:

- job roles;
- departments;
- income levels;
- years at the company;
- job satisfaction levels.

---

# BI-002 — Job Roles with Highest Attrition

## Business Question

**BQ-002**

Which job roles experience the highest employee attrition?

## Results

| Job Role | Employees | Attrition | Attrition Rate |
|----------|----------:|----------:|---------------:|
| Sales Representative | 83 | 33 | 39.76% |
| Laboratory Technician | 259 | 62 | 23.94% |
| Human Resources | 52 | 12 | 23.08% |
| Sales Executive | 326 | 57 | 17.48% |
| Research Scientist | 292 | 47 | 16.10% |
| Manufacturing Director | 145 | 10 | 6.90% |
| Healthcare Representative | 131 | 9 | 6.87% |
| Manager | 102 | 5 | 4.90% |
| Research Director | 80 | 2 | 2.50% |

## Interpretation

Sales Representatives exhibit the highest attrition rate in the dataset.

Research Directors and Managers show the lowest observed turnover.

Employee attrition is therefore not uniformly distributed across job roles.

## Business Impact

Retention initiatives should initially focus on job roles experiencing the highest turnover.

Additional analyses should investigate whether workload, compensation, career progression or organizational factors contribute to these differences.

## Evidence Strength

**Strong**

## Reasoning

Every job role is represented in the dataset, and the ranking is calculated directly from observed attrition rates.

Smaller groups, such as Human Resources, should still be interpreted with appropriate caution.

## Next Investigation

Examine whether differences between job roles are associated with:

- overtime;
- monthly income;
- job level;
- years at the company;
- job satisfaction;
- career progression.

---

# BI-003 — Department Attrition Analysis

## Business Question

**BQ-003**

Which departments experience the highest employee attrition?

## Results

| Department | Employees | Attrition | Attrition Rate |
|------------|----------:|----------:|---------------:|
| Sales | 446 | 92 | 20.63% |
| Human Resources | 63 | 12 | 19.05% |
| Research & Development | 961 | 133 | 13.84% |

## Interpretation

Sales exhibits the highest attrition rate among all departments.

Human Resources also shows relatively high turnover, although the department contains considerably fewer employees.

Research & Development is both the largest department and the one with the lowest attrition rate.

## Business Impact

Departments with elevated turnover should be prioritized for further investigation.

Potential contributing factors include:

- workload;
- incentive structure;
- leadership;
- career development opportunities;
- department-specific organizational culture.

## Evidence Strength

**Moderate**

## Reasoning

The overall ranking is clear.

However, Human Resources contains only 63 employees, making its estimated attrition rate less robust than those of the larger departments.

## Next Investigation

Determine whether departmental differences are explained by:

- job-role composition;
- overtime;
- compensation;
- job satisfaction;
- management relationships;
- years at the company.
---

# BI-004 — Job Satisfaction and Employee Attrition

## Business Question

**BQ-004**

Is job satisfaction associated with employee attrition?

## Results

| Job Satisfaction | Employees | Attrition | Attrition Rate |
|-----------------:|----------:|----------:|---------------:|
| 1 | 289 | 66 | 22.84% |
| 2 | 280 | 46 | 16.43% |
| 3 | 442 | 73 | 16.52% |
| 4 | 459 | 52 | 11.33% |

## Interpretation

Employees reporting the lowest job satisfaction show the highest attrition rate.

Employees reporting the highest job satisfaction show the lowest attrition rate.

The middle satisfaction levels are similar to one another, so the relationship is not perfectly linear, but the contrast between the lowest and highest levels is clear.

## Business Impact

Job satisfaction should be included in employee-retention monitoring.

Potential actions include:

- targeted employee surveys;
- manager feedback reviews;
- role-design assessments;
- career-development discussions;
- intervention plans for teams reporting low satisfaction.

## Evidence Strength

**Moderate**

## Reasoning

The difference between the lowest and highest satisfaction groups is meaningful: 22.84% compared with 11.33%.

However, levels 2 and 3 show almost identical attrition rates, so the pattern should not be described as a strictly linear relationship.

## Next Investigation

Evaluate whether the relationship between job satisfaction and attrition differs by:

- job role;
- department;
- overtime status;
- monthly income;
- years at the company.

---

# BI-005 — Work-Life Balance and Employee Attrition

## Business Question

**BQ-005**

Is work-life balance associated with employee attrition?

## Results

| Work-Life Balance | Employees | Attrition | Attrition Rate |
|------------------:|----------:|----------:|---------------:|
| 1 | 80 | 25 | 31.25% |
| 2 | 344 | 58 | 16.86% |
| 3 | 893 | 127 | 14.22% |
| 4 | 153 | 27 | 17.65% |

## Interpretation

Employees reporting the lowest work-life balance show a substantially higher attrition rate than the other groups.

The remaining levels are relatively close to one another.

The data therefore supports the conclusion that very poor work-life balance is associated with elevated attrition, but it does not support a simple linear relationship in which every improvement in work-life balance produces lower attrition.

## Business Impact

A very low work-life balance score may serve as an early warning indicator for retention risk.

Potential actions include:

- workload reviews;
- staffing assessments;
- flexible-work policies;
- overtime monitoring;
- manager intervention;
- employee-support initiatives.

## Evidence Strength

**Moderate**

## Reasoning

The level-1 group has an attrition rate of 31.25%, which is substantially higher than the other groups.

However, the group contains only 80 employees, and level 4 does not perform better than level 3. The evidence supports a specific risk associated with the lowest score, not a fully linear trend.

## Next Investigation

Assess whether the elevated attrition among employees with the lowest work-life balance is concentrated in:

- overtime employees;
- specific job roles;
- specific departments;
- lower job-satisfaction groups;
- employees with longer commuting distances.
---

# BI-006 — Early Employee Lifecycle and Employee Attrition

## Business Question

**BQ-006**

Is employee attrition concentrated during the early stages of the employee lifecycle?

## Results

### Attrition by Years at Company

| Years at Company | Employees | Attrition | Attrition Rate |
|----------------:|----------:|----------:|---------------:|
| 0 | 44 | 16 | 36.36% |
| 1 | 171 | 59 | 34.50% |
| 2 | 127 | 27 | 21.26% |
| 3 | 128 | 20 | 15.63% |
| 4 | 110 | 19 | 17.27% |
| 5 | 196 | 21 | 10.71% |

### Attrition by Years in Current Role

| Years in Current Role | Employees | Attrition | Attrition Rate |
|----------------------:|----------:|----------:|---------------:|
| 0 | 244 | 73 | 29.92% |
| 1 | 57 | 11 | 19.30% |
| 2 | 372 | 68 | 18.28% |
| 3 | 135 | 16 | 11.85% |
| 4 | 104 | 15 | 14.42% |
| 5 | 36 | 1 | 2.78% |

## Interpretation

Employee attrition is heavily concentrated during the earliest stages of the employee lifecycle.

The highest attrition rates occur during the first years at the company and among employees who have only recently entered their current role.

After the initial years, attrition generally decreases and stabilizes at considerably lower levels.

Very small groups at high tenure levels were not used to draw conclusions because they are not statistically representative.

## Business Impact

The first years of employment represent the highest-risk period for employee turnover.

Organizations should prioritize retention initiatives during onboarding and the early employment lifecycle.

Possible actions include:

- structured onboarding programs;
- early career mentoring;
- frequent manager check-ins;
- onboarding satisfaction surveys;
- early performance and engagement reviews.

## Evidence Strength

**Strong**

## Reasoning

Two independent analyses support the same conclusion:

- Years
---

# BI-007 — Job Involvement and Employee Attrition

## Pattern Type

**Gradient**

## Business Question

**BQ-007**

Is job involvement associated with employee attrition?

## Results

| Job Involvement | Employees | Attrition | Attrition Rate |
|----------------:|----------:|----------:|---------------:|
| 1 | 83 | 28 | 33.73% |
| 2 | 375 | 71 | 18.93% |
| 3 | 868 | 125 | 14.40% |
| 4 | 144 | 13 | 9.03% |

## Interpretation

Employee attrition decreases progressively as job involvement increases.

The relationship is consistent across all four involvement levels, suggesting that employees reporting stronger involvement with their work are substantially less likely to leave the organization.

This dataset demonstrates an association, not causality.

## Business Impact

Job involvement may represent an important indicator for employee retention.

Organizations should monitor employee engagement and identify individuals reporting very low involvement before turnover occurs.

## Evidence Strength

**Strong**

## Reasoning

A clear monotonic trend is observed across all four levels, with attrition decreasing from 33.73% to 9.03%.

## Next Investigation

Investigate whether Job Involvement remains associated with attrition after controlling for:

- Department
- Job Role
- Overtime
- Job Satisfaction
- Years at Company

---

# BI-008 — Environment Satisfaction and Employee Attrition

## Pattern Type

**Threshold**

## Business Question

**BQ-008**

Is environment satisfaction associated with employee attrition?

## Results

| Environment Satisfaction | Employees | Attrition | Attrition Rate |
|-------------------------:|----------:|----------:|---------------:|
| 1 | 284 | 72 | 25.35% |
| 2 | 287 | 43 | 14.98% |
| 3 | 453 | 62 | 13.69% |
| 4 | 446 | 60 | 13.45% |

## Interpretation

Employees reporting the lowest environment satisfaction exhibit substantially higher attrition.

Levels 2, 3 and 4 show very similar attrition rates, indicating that the primary difference is concentrated in the lowest satisfaction group.

## Business Impact

Employees reporting the lowest satisfaction with their work environment should receive priority attention during retention initiatives.

## Evidence Strength

**Strong**

## Reasoning

The lowest satisfaction level shows an attrition rate almost twice as high as the remaining groups.

## Next Investigation

Assess whether poor environment satisfaction is associated with:

- overtime;
- department;
- job role;
- work-life balance.

---

# BI-009 — Relationship Satisfaction and Employee Attrition

## Pattern Type

**Threshold**

## Business Question

**BQ-009**

Is relationship satisfaction associated with employee attrition?

## Results

| Relationship Satisfaction | Employees | Attrition | Attrition Rate |
|--------------------------:|----------:|----------:|---------------:|
| 1 | 276 | 57 | 20.65% |
| 2 | 303 | 45 | 14.85% |
| 3 | 459 | 71 | 15.47% |
| 4 | 432 | 64 | 14.81% |

## Interpretation

Employees reporting the lowest relationship satisfaction experience noticeably higher attrition.

The remaining satisfaction levels exhibit very similar attrition rates.

## Business Impact

Relationship satisfaction may serve as an early indicator of retention risk, particularly for employees reporting the lowest satisfaction level.

## Evidence Strength

**Strong**

## Reasoning

The increased attrition is concentrated in the lowest satisfaction category, while all remaining groups behave consistently.

## Next Investigation

Evaluate whether relationship satisfaction interacts with:

- manager relationship;
- department;
- overtime;
- job involvement;
- environment satisfaction.
