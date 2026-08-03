-- ==========================================================
-- Project: HR Analytics - Employee Attrition & Workforce Insights
-- File: 01_data_audit.sql
-- Author: Federica Iengo
-- ==========================================================

/*
DATA AUDIT

Purpose:
Verify the integrity and quality of the imported dataset before
performing any cleaning, transformation or business analysis.

Dataset:
IBM HR Analytics Employee Attrition & Performance

Database:
employee_attrition.db

Table:
employee_attrition
*/

-- ==========================================================
-- 1. Verify total number of records
-- Expected: 1470
-- Result: 1470
-- Status: PASS
-- ==========================================================

SELECT COUNT(*) AS total_records
FROM employee_attrition;

-- ==========================================================
-- 2. Check NULL values in key columns
--
-- Expected:
-- Age = 0
-- Attrition = 0
-- Department = 0
-- JobRole = 0
-- MonthlyIncome = 0
-- OverTime = 0
--
-- Status: PASS
-- ==========================================================

SELECT
    SUM(CASE WHEN Age IS NULL THEN 1 ELSE 0 END) AS age_nulls,
    SUM(CASE WHEN Attrition IS NULL THEN 1 ELSE 0 END) AS attrition_nulls,
    SUM(CASE WHEN Department IS NULL THEN 1 ELSE 0 END) AS department_nulls,
    SUM(CASE WHEN JobRole IS NULL THEN 1 ELSE 0 END) AS jobrole_nulls,
    SUM(CASE WHEN MonthlyIncome IS NULL THEN 1 ELSE 0 END) AS monthlyincome_nulls,
    SUM(CASE WHEN OverTime IS NULL THEN 1 ELSE 0 END) AS overtime_nulls
FROM employee_attrition;

-- ==========================================================
-- 3. Check duplicate records
--
-- Expected: 0
-- Result: 0
-- Status: PASS
-- ==========================================================

SELECT COUNT(*) AS duplicate_groups
FROM (
    SELECT *
    FROM employee_attrition
    GROUP BY
        Age, Attrition, BusinessTravel, DailyRate, Department,
        DistanceFromHome, Education, EducationField, EmployeeCount,
        EmployeeNumber, EnvironmentSatisfaction, Gender, HourlyRate,
        JobInvolvement, JobLevel, JobRole, JobSatisfaction,
        MaritalStatus, MonthlyIncome, MonthlyRate, NumCompaniesWorked,
        Over18, OverTime, PercentSalaryHike, PerformanceRating,
        RelationshipSatisfaction, StandardHours, StockOptionLevel,
        TotalWorkingYears, TrainingTimesLastYear, WorkLifeBalance,
        YearsAtCompany, YearsInCurrentRole, YearsSinceLastPromotion,
        YearsWithCurrManager
    HAVING COUNT(*) > 1
);

-- ==========================================================
-- 4. Identify constant-value columns
--
-- EmployeeCount -> constant
-- Over18 -> constant
-- StandardHours -> constant
--
-- These columns do not provide analytical value and are
-- candidates for removal from the cleaned dataset while
-- remaining in the raw dataset.
--
-- Status: PASS
-- ==========================================================

SELECT
    COUNT(DISTINCT EmployeeCount) AS employee_count_values,
    COUNT(DISTINCT Over18) AS over18_values,
    COUNT(DISTINCT StandardHours) AS standard_hours_values
FROM employee_attrition;

-- ==========================================================
-- 5. Verify values of constant columns
--
-- EmployeeCount = 1
-- Over18 = Y
-- StandardHours = 80
--
-- Interpretation:
-- These columns contain the same value for every record and
-- therefore do not contribute to analytical models.
--
-- Recommendation:
-- Remove them from the cleaned dataset while preserving them
-- in the raw dataset.
--
-- Status: PASS
-- ==========================================================

SELECT
    MIN(EmployeeCount) AS employee_count_value,
    MIN(Over18) AS over18_value,
    MIN(StandardHours) AS standard_hours_value
FROM employee_attrition;
