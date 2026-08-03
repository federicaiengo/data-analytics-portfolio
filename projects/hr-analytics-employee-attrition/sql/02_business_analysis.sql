-- ==========================================================
-- Project: HR Analytics - Employee Attrition & Workforce Insights
-- Repository: data-analytics-portfolio
-- File: 02_business_analysis.sql
-- Author: Federica Iengo
-- Status: In Progress
-- Last Updated: 2026-08-02
-- ==========================================================

/*
BUSINESS ANALYSIS

Purpose:
Answer defined business questions using SQL and connect each
analysis directly to its documented business insight.

Related document:
insights/business_findings.md

Reference system:
BQ-XXX = Business Question
BI-XXX = Business Insight
*/

-- ==========================================================
-- BQ-001
-- Business Question:
-- Are employees working overtime more likely to leave
-- the company?
--
-- Related Business Insight:
-- BI-001 - Overtime and Employee Attrition
-- ==========================================================

SELECT
    OverTime,
    Attrition,
    COUNT(*) AS Employees
FROM employee_attrition
GROUP BY OverTime, Attrition
ORDER BY OverTime, Attrition;

-- Result:
-- No   No    944
-- No   Yes   110
-- Yes  No    289
-- Yes  Yes   127
--
-- Derived attrition rates:
-- No overtime:  10.44%
-- Overtime:     30.53%
--
-- Interpretation:
-- Employees working overtime show an attrition rate
-- approximately three times higher than employees who do
-- not work overtime.
--
-- Full interpretation:
-- See BI-001 in insights/business_findings.md.


-- ==========================================================
-- BQ-002
-- Business Question:
-- Which job roles experience the highest employee attrition?
--
-- Related Business Insight:
-- BI-002 - Job Roles with Highest Attrition
-- ==========================================================

SELECT
    JobRole,
    COUNT(*) AS Employees,
    SUM(
        CASE
            WHEN Attrition = 'Yes' THEN 1
            ELSE 0
        END
    ) AS AttritionCount,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN Attrition = 'Yes' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS AttritionRate
FROM employee_attrition
GROUP BY JobRole
ORDER BY AttritionRate DESC;

-- Result:
-- Sales Representative       83 employees   33 attrition   39.76%
-- Laboratory Technician     259 employees   62 attrition   23.94%
-- Human Resources            52 employees   12 attrition   23.08%
-- Sales Executive           326 employees   57 attrition   17.48%
-- Research Scientist        292 employees   47 attrition   16.10%
-- Manufacturing Director    145 employees   10 attrition    6.90%
-- Healthcare Representative 131 employees    9 attrition    6.87%
-- Manager                    102 employees    5 attrition    4.90%
-- Research Director           80 employees    2 attrition    2.50%
--
-- Interpretation:
-- Employee attrition is not uniformly distributed across
-- job roles. Sales Representatives show the highest observed
-- attrition rate.
--
-- Full interpretation:
-- See BI-002 in insights/business_findings.md.


-- ==========================================================
-- BQ-003
-- Business Question:
-- Which departments experience the highest employee
-- attrition?
--
-- Related Business Insight:
-- BI-003 - Department Attrition Analysis
-- ==========================================================

SELECT
    Department,
    COUNT(*) AS Employees,
    SUM(
        CASE
            WHEN Attrition = 'Yes' THEN 1
            ELSE 0
        END
    ) AS AttritionCount,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN Attrition = 'Yes' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS AttritionRate
FROM employee_attrition
GROUP BY Department
ORDER BY AttritionRate DESC;

-- Result:
-- Sales                    446 employees   92 attrition   20.63%
-- Human Resources           63 employees   12 attrition   19.05%
-- Research & Development   961 employees  133 attrition   13.84%
--
-- Interpretation:
-- Sales shows the highest departmental attrition rate.
-- Human Resources also shows elevated attrition, but its
-- smaller sample requires greater interpretive caution.
--
-- Full interpretation:
-- See BI-003 in insights/business_findings.md.
-- ==========================================================
-- BQ-004
-- Business Question:
-- Is job satisfaction associated with employee attrition?
--
-- Related Business Insight:
-- BI-004 - Job Satisfaction and Employee Attrition
-- ==========================================================

SELECT
    JobSatisfaction,
    Attrition,
    COUNT(*) AS Employees
FROM employee_attrition
GROUP BY JobSatisfaction, Attrition
ORDER BY JobSatisfaction, Attrition;

-- Result:
--
-- Satisfaction 1   No 223   Yes 66
-- Satisfaction 2   No 234   Yes 46
-- Satisfaction 3   No 369   Yes 73
-- Satisfaction 4   No 407   Yes 52
--
-- Attrition Rates
--
-- Level 1 -> 22.84%
-- Level 2 -> 16.43%
-- Level 3 -> 16.52%
-- Level 4 -> 11.33%
--
-- Interpretation:
--
-- Lower job satisfaction is associated with
-- higher employee attrition.
--
-- Full interpretation:
-- See BI-004 in insights/business_findings.md.


-- ==========================================================
-- BQ-005
-- Business Question:
-- Is work-life balance associated with employee attrition?
--
-- Related Business Insight:
-- BI-005 - Work-Life Balance and Employee Attrition
-- ==========================================================

SELECT
    WorkLifeBalance,
    Attrition,
    COUNT(*) AS Employees
FROM employee_attrition
GROUP BY WorkLifeBalance, Attrition
ORDER BY WorkLifeBalance, Attrition;

-- Result:
--
-- Level 1   No 55   Yes 25
-- Level 2   No 286  Yes 58
-- Level 3   No 766  Yes 127
-- Level 4   No 126  Yes 27
--
-- Attrition Rates
--
-- Level 1 -> 31.25%
-- Level 2 -> 16.86%
-- Level 3 -> 14.22%
-- Level 4 -> 17.65%
--
-- Interpretation:
--
-- Employees reporting the lowest work-life balance
-- exhibit substantially higher attrition.
--
-- Full interpretation:
-- See BI-005 in insights/business_findings.md.
-- ==========================================================
-- BQ-006
-- Business Question:
-- Is employee attrition concentrated during the early stages
-- of the employee lifecycle?
--
-- Related Business Insight:
-- BI-006 - Early Employee Lifecycle and Attrition
-- ==========================================================

-- Analysis 1:
-- Years at Company

SELECT
    YearsAtCompany,
    COUNT(*) AS Employees,
    SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) AS AttritionCount,
    ROUND(
        100.0 * SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS AttritionRate
FROM employee_attrition
GROUP BY YearsAtCompany
ORDER BY YearsAtCompany;

-- Key Findings
--
-- Year 0 -> 36.36%
-- Year 1 -> 34.50%
-- Year 2 -> 21.26%
-- Year 3 -> 15.63%
-- Year 5 -> 10.71%
--
-- Observation:
-- Attrition decreases substantially after the first years
-- of employment.


-- Analysis 2:
-- Years in Current Role

SELECT
    YearsInCurrentRole,
    COUNT(*) AS Employees,
    SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) AS AttritionCount,
    ROUND(
        100.0 * SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS AttritionRate
FROM employee_attrition
GROUP BY YearsInCurrentRole
ORDER BY YearsInCurrentRole;

-- Key Findings
--
-- Year 0 -> 29.92%
-- Year 1 -> 19.30%
-- Year 2 -> 18.28%
-- Year 3 -> 11.85%
--
-- Observation:
-- Employees in the earliest stages of their current role
-- also exhibit substantially higher attrition.
--
-- Full interpretation:
-- See BI-006 in insights/business_findings.md.
-- ==========================================================
-- BQ-007
-- Business Question:
-- Is job involvement associated with employee attrition?
--
-- Related Business Insight:
-- BI-007 - Job Involvement and Employee Attrition
-- ==========================================================

SELECT
    JobInvolvement,
    COUNT(*) AS Employees,
    SUM(
        CASE
            WHEN Attrition = 'Yes' THEN 1
            ELSE 0
        END
    ) AS AttritionCount,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN Attrition = 'Yes' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS AttritionRate
FROM employee_attrition
GROUP BY JobInvolvement
ORDER BY JobInvolvement;

-- Result:
--
-- Level 1   83 employees   28 attrition   33.73%
-- Level 2  375 employees   71 attrition   18.93%
-- Level 3  868 employees  125 attrition   14.40%
-- Level 4  144 employees   13 attrition    9.03%
--
-- Interpretation:
-- Attrition decreases progressively as Job Involvement
-- increases.
--
-- Pattern Type:
-- Gradient
--
-- Decision:
-- Promoted to Business Insight.
--
-- Full interpretation:
-- See BI-007 in insights/business_findings.md.


-- ==========================================================
-- BQ-008
-- Business Question:
-- Is environment satisfaction associated with employee
-- attrition?
--
-- Related Business Insight:
-- BI-008 - Environment Satisfaction and Employee Attrition
-- ==========================================================

SELECT
    EnvironmentSatisfaction,
    COUNT(*) AS Employees,
    SUM(
        CASE
            WHEN Attrition = 'Yes' THEN 1
            ELSE 0
        END
    ) AS AttritionCount,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN Attrition = 'Yes' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS AttritionRate
FROM employee_attrition
GROUP BY EnvironmentSatisfaction
ORDER BY EnvironmentSatisfaction;

-- Result:
--
-- Level 1  284 employees   72 attrition   25.35%
-- Level 2  287 employees   43 attrition   14.98%
-- Level 3  453 employees   62 attrition   13.69%
-- Level 4  446 employees   60 attrition   13.45%
--
-- Interpretation:
-- Employees reporting the lowest environment satisfaction
-- show substantially higher attrition. Levels 2-4 are
-- comparatively similar.
--
-- Pattern Type:
-- Threshold
--
-- Decision:
-- Promoted to Business Insight.
--
-- Full interpretation:
-- See BI-008 in insights/business_findings.md.


-- ==========================================================
-- BQ-009
-- Business Question:
-- Is relationship satisfaction associated with employee
-- attrition?
--
-- Related Business Insight:
-- BI-009 - Relationship Satisfaction and Employee Attrition
-- ==========================================================

SELECT
    RelationshipSatisfaction,
    COUNT(*) AS Employees,
    SUM(
        CASE
            WHEN Attrition = 'Yes' THEN 1
            ELSE 0
        END
    ) AS AttritionCount,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN Attrition = 'Yes' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS AttritionRate
FROM employee_attrition
GROUP BY RelationshipSatisfaction
ORDER BY RelationshipSatisfaction;

-- Result:
--
-- Level 1  276 employees   57 attrition   20.65%
-- Level 2  303 employees   45 attrition   14.85%
-- Level 3  459 employees   71 attrition   15.47%
-- Level 4  432 employees   64 attrition   14.81%
--
-- Interpretation:
-- Employees reporting the lowest relationship satisfaction
-- show higher attrition. Levels 2-4 are nearly identical.
--
-- Pattern Type:
-- Threshold
--
-- Decision:
-- Promoted to Business Insight.
--
-- Full
