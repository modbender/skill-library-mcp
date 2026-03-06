---
name: employee-skills-importer
description: Parse employee skills CSV files, identify skill categories and individual skills, look up employee IDs from an employees table, and generate idempotent SQL INSERT statements for skill_categories, skills, and employee_skills tables.
---

# Employee Skills Importer

This skill automates the process of importing employee skills from CSV files into a Supabase database. It parses the CSV, checks what already exists in the database, and generates idempotent SQL scripts to insert missing data.

## Overview

The skill performs a 3-step process:
1. **Identify and insert missing skill categories** - Extract categories from CSV headers, check database, generate INSERT script
2. **Identify and insert missing skills** - Extract skills with their categories, check database, generate INSERT script  
3. **Generate employee_skills INSERT script** - Map employees by name, link skills, create final INSERT statements

## CSV Format Requirements

The CSV must have:
- **Row 1**: Empty or metadata (ignored)
- **Row 2**: Skill category names spanning multiple columns
- **Row 3+**: Individual skill names (column headers, may span multiple rows due to line breaks)
- **Employee data rows**: Employee data with First Name, Last Name in first two columns, followed by skill experience values

Example structure:
```
,,,,,,.NET,,,,,Front-end,,,Java,,,
First Name,Last Name,Full Name,Unit,...,C#,ASP.net,MVC,...,JavaScript,HTML,CSS,...,Java,Spring,...
John,Doe,John Doe,Unit 1,...,5,4,3,...,6,6,5,...,0,0,...
```

## Workflow

### Step 1: Skill Categories

1. Parse row 2 to extract unique category names
2. Query the database to check existing categories:
   ```sql
   SELECT name FROM skill_categories
   ```
3. Generate idempotent INSERT for missing categories:
   ```sql
   INSERT INTO skill_categories (name) 
   VALUES ('Category1'), ('Category2'), ('Category3')
   ON CONFLICT (name) DO NOTHING;
   ```

### Step 2: Skills

1. Parse skill name rows and map to categories from row 2
2. Query database for existing skills:
   ```sql
   SELECT s.name, sc.name as category_name 
   FROM skills s 
   LEFT JOIN skill_categories sc ON s.category_id = sc.id
   ```
3. For each skill to insert:
   - Find the category_id using a subquery
   - Generate idempotent INSERT:
   ```sql
   INSERT INTO skills (name, category_id)
   VALUES 
     ('C#', (SELECT id FROM skill_categories WHERE name = '.NET')),
     ('JavaScript', (SELECT id FROM skill_categories WHERE name = 'Front-end'))
   ON CONFLICT (name) DO NOTHING;
   ```

### Step 3: Employee Skills

1. Parse employee rows (first_name, last_name, skill values)
2. Query employees table to get employee IDs:
   ```sql
   SELECT id, first_name, last_name FROM employees
   ```
3. For each employee, for each skill with non-zero experience:
   - Look up employee_id by matching first_name + last_name
   - Look up skill_id using subquery
   - **CRITICAL: Use TRIM() in WHERE clause to handle whitespace variations in database**
   - Generate INSERT:
   ```sql
   INSERT INTO employee_skills (employee_id, skill_id, years_of_experience)
   VALUES 
     (
       (SELECT id FROM employees WHERE TRIM(first_name) = 'John' AND TRIM(last_name) = 'Doe'),
       (SELECT id FROM skills WHERE name = 'C#'),
       5
     )
   ON CONFLICT (employee_id, skill_id) DO UPDATE 
   SET years_of_experience = EXCLUDED.years_of_experience;
   ```

## Important Notes

### Database Schema
- `skill_categories` table: id (uuid), name (text, unique)
- `skills` table: id (uuid), name (text, unique), category_id (uuid FK to skill_categories)
- `employees` table: id (uuid), first_name (text), last_name (text)
- `employee_skills` table: id (uuid), employee_id (uuid FK), skill_id (uuid FK), years_of_experience (real)

### Idempotency
All generated SQL scripts use `ON CONFLICT` clauses to ensure they can be run multiple times without errors:
- For categories and skills: `ON CONFLICT (name) DO NOTHING`
- For employee_skills: `ON CONFLICT (employee_id, skill_id) DO UPDATE SET years_of_experience = EXCLUDED.years_of_experience`

### Data Handling
- Skip employees with zero or empty experience values for a skill
- Handle numeric experience values (can be integers or decimals like 0.5, 1.7, etc.)
- Clean up skill names by trimming whitespace and removing line breaks
- Skip rows where employee lookup fails (employee not found in database)
- Handle multi-line CSV cells properly
- **CRITICAL: Deduplicate employee-skill pairs before generating SQL** - Keep the highest years value when duplicates exist
- **CRITICAL: Automatically correct employee name spellings** - Use fuzzy matching to find and correct minor spelling differences (e.g., "Victoriia" → "Viktoriia")
- **CRITICAL: Trim all employee names** - Remove leading/trailing whitespace from all names
- **CRITICAL: Use TRIM() in SQL WHERE clauses** - Database may have extra spaces (e.g., "Yurii   Solokha" with 3 spaces)
- **CRITICAL: Skip employees with no match** - If no close match found in database, exclude those records and report them

### Error Prevention
- Always use subqueries for foreign key lookups rather than hardcoding UUIDs
- Validate that category names match between row 2 and skill lookups
- Report any employees from CSV not found in the database
- Report any skills that couldn't be mapped to categories

**CRITICAL - Prevent Duplicate Key Violations:**
1. Before generating the employee_skills INSERT, deduplicate all records by (first_name, last_name, skill)
2. When duplicates exist, keep the record with the highest years_of_experience value
3. This prevents: `ON CONFLICT DO UPDATE command cannot affect row a second time`

**CRITICAL - Automatic Name Correction:**
1. Before generating SQL, validate ALL employees exist in the database
2. For employees not found by exact match:
   - Use fuzzy matching (Levenshtein distance or similar) to find close matches in database
   - If a close match is found (e.g., "Victoriia" → "Viktoriia"), automatically use the database spelling
   - If no close match is found, skip the employee entirely
3. Generate a report showing:
   - Employees with automatic corrections applied: "CSV name → Database name"
   - Employees skipped (no match found): List with number of skills skipped
4. This prevents: `null value in column "employee_id" violates not-null constraint`

## Output Format

The skill produces three SQL scripts plus one report file:

**1_insert_categories.sql**
```sql
-- Insert missing skill categories
INSERT INTO skill_categories (name) 
VALUES ('.NET'), ('Front-end'), ('Java')
ON CONFLICT (name) DO NOTHING;
```

**2_insert_skills.sql**
```sql
-- Insert missing skills with category mapping
INSERT INTO skills (name, category_id)
VALUES 
  ('C#', (SELECT id FROM skill_categories WHERE name = '.NET')),
  ('ASP.net', (SELECT id FROM skill_categories WHERE name = '.NET')),
  ('JavaScript', (SELECT id FROM skill_categories WHERE name = 'Front-end'))
ON CONFLICT (name) DO NOTHING;
```

**3_insert_employee_skills.sql**
```sql
-- Insert employee skills
-- Records have been deduplicated and filtered for valid employees only
-- Using TRIM() in WHERE clause to handle whitespace in database
INSERT INTO employee_skills (employee_id, skill_id, years_of_experience)
VALUES 
  (
    (SELECT id FROM employees WHERE TRIM(first_name) = 'John' AND TRIM(last_name) = 'Doe'),
    (SELECT id FROM skills WHERE name = 'C#'),
    5
  ),
  (
    (SELECT id FROM employees WHERE TRIM(first_name) = 'John' AND TRIM(last_name) = 'Doe'),
    (SELECT id FROM skills WHERE name = 'JavaScript'),
    6
  )
ON CONFLICT (employee_id, skill_id) DO UPDATE 
SET years_of_experience = EXCLUDED.years_of_experience;
```

## Execution Steps

When the user provides a CSV file:

1. **Parse the CSV structure**
   - Read the file and validate format
   - Extract category names from row 2
   - Extract skill names from subsequent rows (handling multi-line cells)
   - Map each skill to its category based on column positions

2. **Query existing data from Supabase**
   - Fetch all existing skill_categories
   - Fetch all existing skills with their categories
   - Fetch all employees (id, first_name, last_name)

3. **Generate Script 1: Categories**
   - Compare CSV categories against database
   - Create INSERT statement for missing categories
   - Save to file and present to user

4. **Generate Script 2: Skills**
   - Compare CSV skills against database
   - For missing skills, include category lookup subquery
   - Create INSERT statement
   - Save to file and present to user

5. **Generate Script 3: Employee Skills**
   - Parse employee rows
   - **VALIDATE: Compare all CSV employees against database using exact matching**
   - **FUZZY MATCH: For non-exact matches, find closest database employee using similarity algorithm**
     - Calculate similarity score for first_name and last_name separately
     - If combined similarity is above threshold (e.g., 85%), automatically use database name
     - Track all automatic corrections for reporting
   - **CORRECT: Replace CSV names with database names for matched employees**
   - **FILTER: Skip employees with no close match found**
   - **DEDUPLICATE: Remove duplicates by (employee, skill), keeping highest years value**
   - Generate INSERT statements using corrected employee names
   - **Generate report showing corrections and skipped employees**
   - Save SQL file and report to outputs directory
   - Present both files to user

6. **Present all files to the user**
   - Three SQL scripts (1_insert_categories.sql, 2_insert_skills.sql, 3_insert_employee_skills.sql)
   - One report file (skipped_employees_report.txt) if any employees were skipped
   - User can execute SQL scripts in order: 1 → 2 → 3
   - User should review report to fix name mismatches if needed

## Usage Example

User uploads CSV file and says:
"Parse this employee skills CSV and generate SQL insert scripts"

Skill responds:
1. Analyzes the CSV structure
2. Connects to Supabase SkillsSystem project
3. Checks existing data in all three tables
4. Generates three SQL files
5. Reports summary (e.g., "Found 5 new categories, 23 new skills, generating inserts for 47 employees")
6. Presents the three SQL files for download

## Project Configuration

This skill is configured to work with the Supabase project:
- **Project Name**: SkillsSystem  
- **Project ID**: ypibfhbklinkvybgotef
- **Region**: eu-central-1

The skill automatically connects to this project when executing queries.

## Common Errors and Solutions

### Error 1: "ON CONFLICT DO UPDATE command cannot affect row a second time"
**Cause:** Duplicate employee-skill pairs in the generated INSERT statement
**Solution:** The skill now deduplicates all records before generating SQL. If you see this error, it means deduplication was not performed.
**Prevention:** Always deduplicate by (first_name, last_name, skill) and keep the highest years value

### Error 2: "null value in column 'employee_id' violates not-null constraint"
**Cause:** Employee from CSV not found in database (usually due to name spelling differences or whitespace issues)
**Solution:** The skill now:
1. Automatically corrects spelling differences using fuzzy matching
2. Trims all whitespace from names
3. Uses TRIM() in SQL WHERE clauses to match database records with extra spaces

**Common issues:**
- Spelling variations: "Victoriia"↔"Viktoriia", "Karasyov"↔"Karasov"
- Extra whitespace in database: "Yurii   Solokha" (3 spaces)
- Leading/trailing spaces

**How it works:**
- Compares CSV names against database using similarity algorithm
- If close match found (>83% similarity), automatically uses database spelling
- Trims all names before comparison
- Uses `TRIM(first_name)` and `TRIM(last_name)` in SQL to handle database whitespace
- If no close match found, skips the employee and reports it

**Result:** This error should no longer occur as names are automatically corrected and whitespace is handled

### Name Matching Algorithm
The skill uses the following approach:
1. Try exact match first (first_name AND last_name)
2. If no exact match, calculate similarity score using:
   - Levenshtein distance or similar algorithm
   - Handles common variations: "Victoriia"↔"Viktoriia", "Karasyov"↔"Karasov"
3. If similarity > 83% threshold, accept as match
4. If multiple close matches found, pick the closest one
5. If no close match, skip the employee
6. Always trim whitespace from both CSV and database names
7. Use TRIM() in SQL queries to match records with extra spaces in database
