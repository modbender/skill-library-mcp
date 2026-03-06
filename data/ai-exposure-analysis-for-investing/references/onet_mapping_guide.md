# O*NET Mapping Guide

How to use the bundled O*NET datasets to map company workforce to AI exposure scores.

## Available O*NET Datasets

The following datasets are bundled in the skill's `data/` directory:

### 1. Occupation_Data.txt (~1,016 occupations)
- **Columns:** O*NET-SOC Code, Title, Description
- **Use:** Look up occupation codes and descriptions to match company job categories

### 2. Task_Statements.txt (~18,796 tasks)
- **Columns:** O*NET-SOC Code, Title, Task ID, Task, Task Type
- **Use:** See the specific tasks performed by each occupation. Assess which tasks are AI-automatable.

### 3. Task_Ratings.txt (~35,902 ratings)
- **Columns:** O*NET-SOC Code, Title, Task ID, Scale ID, Data Value
- **Scale IDs:** `IM` (Importance, 1–5) and `RT` (Relevance of Task, 0–100%)
- **Use:** Get importance and relevance ratings for each task. Higher-importance, higher-relevance tasks that are AI-automatable have the greatest impact.

### 4. Work_Activities.txt (~36,654 entries)
- **Columns:** O*NET-SOC Code, Title, Element ID, Element Name, Data Value
- **Scale:** Importance only (IM, 1–5)
- **Use:** Understand the work activities for each occupation (e.g., "Getting Information", "Analyzing Data", "Making Decisions"). Activities involving information processing, data analysis, and communication are more AI-exposed.

### 5. Abilities.txt (~46,488 entries)
- **Columns:** O*NET-SOC Code, Title, Element ID, Element Name, Data Value
- **Scale:** Importance only (IM, 1–5)
- **Use:** Understand the cognitive and physical abilities required. Occupations relying heavily on cognitive abilities (oral comprehension, written expression, deductive reasoning) are more AI-exposed than those requiring physical abilities (manual dexterity, stamina, spatial orientation).

## Mapping Workflow

### Step 1: Identify Company Job Categories

From the 10-K Human Capital and Business Description sections, identify the major job categories. Most companies disclose categories like:
- Engineers / developers
- Sales and marketing
- Customer support / service
- General & administrative
- Operations / manufacturing
- Research & development
- Professional services / consulting

### Step 2: Map to O*NET-SOC Codes

Use Occupation_Data.txt to find matching O*NET occupations. Common mappings:

| Company Job Category | Likely O*NET Codes |
|---------------------|-------------------|
| Software Engineers | 15-1252.00 (Software Developers), 15-1254.00 (Web Developers) |
| Data Scientists/Analysts | 15-2051.00 (Data Scientists), 13-1111.00 (Management Analysts) |
| Customer Support | 43-4051.00 (Customer Service Representatives) |
| Sales Representatives | 41-3091.00 (Sales Representatives) |
| Marketing | 11-2021.00 (Marketing Managers), 13-1161.00 (Market Research Analysts) |
| Accountants/Finance | 13-2011.00 (Accountants and Auditors) |
| HR | 13-1071.00 (Human Resources Specialists) |
| Legal | 23-1011.00 (Lawyers), 23-2011.00 (Paralegals) |
| Manufacturing/Production | 51-XXXX.00 series (Production Occupations) |
| Warehouse/Logistics | 53-7062.00 (Laborers), 43-5071.00 (Shipping Clerks) |
| Executives/Management | 11-1011.00 (Chief Executives), 11-1021.00 (General Managers) |
| Nurses | 29-1141.00 (Registered Nurses) |
| Physicians | 29-1210 series (Physicians) |
| Teachers | 25-XXXX.00 series (Education Occupations) |

### Step 3: Assess AI Exposure per Occupation

For each mapped occupation, use the datasets to estimate AI exposure:

**Method A — Task-Level Analysis (most rigorous):**
1. Pull all tasks from Task_Statements.txt for the O*NET-SOC code
2. For each task, assess: Can current AI (LLMs, computer vision, etc.) perform this task at comparable quality?
3. Weight by task importance/relevance from Task_Ratings.txt
4. Calculate % of task-weighted work that is AI-automatable

**Method B — Work Activity Analysis (faster):**
1. Pull work activities from Work_Activities.txt for the occupation
2. Categorize activities as:
   - **High AI exposure:** Getting Information, Processing Information, Analyzing Data, Documenting/Recording Information, Communicating (written), Scheduling, Estimating
   - **Moderate AI exposure:** Making Decisions, Judging Qualities, Updating Knowledge, Interpreting Information, Creative Thinking
   - **Low AI exposure:** Handling/Moving Objects, Operating Vehicles, Performing Physical Activities, Repairing, Inspecting Equipment
3. Weight by importance scores (IM scale) to get overall exposure

**Method C — Ability Profile Analysis (supplementary):**
1. Pull abilities from Abilities.txt
2. Cognitive abilities (oral/written comprehension, deductive reasoning, information ordering) → higher AI exposure
3. Physical abilities (manual dexterity, stamina, trunk strength) → lower AI exposure
4. The ratio of cognitive-to-physical ability importance indicates exposure level

### Step 4: Cross-Reference with Academic Scores

After your O*NET-based assessment, validate against published academic exposure scores:

- **Eloundou et al. "GPTs are GPTs" (arXiv 2023):** Provides E1 (direct LLM exposure) and E2 (LLM + tools exposure) for 800+ occupations. Use E1 + 0.5×E2 as the composite score. Web search for the paper's supplementary data.
- **Felten/Raj/Seamans AIOE Index:** Scores occupations based on overlap between AI capabilities and occupation abilities. Higher AIOE = more exposed.
- **Pew Research AI Exposure Tables:** Classification of occupations into high/medium/low AI exposure with workforce counts.

### Step 5: Calculate Company-Level Exposure

1. Estimate the workforce distribution across mapped occupations (use 10-K headcount data, proportional estimates)
2. Weight each occupation's AI exposure score by its share of the workforce
3. Adjust by labor cost-to-revenue ratio (from financial statements)
4. The result feeds directly into Dimension 1 scoring

### Example Calculation

A mid-cap software company with 5,000 employees:
- 2,000 software engineers (40%): Eloundou E1+E2 ≈ 0.65 → high exposure
- 800 sales reps (16%): Eloundou ≈ 0.45 → moderate exposure
- 500 customer support (10%): Eloundou ≈ 0.75 → very high exposure
- 400 product managers (8%): Eloundou ≈ 0.55 → high exposure
- 300 marketing (6%): Eloundou ≈ 0.60 → high exposure
- 500 G&A (10%): Eloundou ≈ 0.50 → moderate-high exposure
- 500 other/management (10%): Eloundou ≈ 0.40 → moderate exposure

Weighted exposure: (0.40×0.65 + 0.16×0.45 + 0.10×0.75 + 0.08×0.55 + 0.06×0.60 + 0.10×0.50 + 0.10×0.40) = 0.575

With SGA at 62% of revenue → amplified impact.
Result: ~57.5% weighted exposure, high labor costs → Dimension 1 Score: 4

## Programmatic Access

To query the O*NET datasets programmatically, use Python with openpyxl or pandas:

```python
import pandas as pd
import os

# Data is bundled in the skill's data/ directory
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_DIR, "data")

# Load datasets
occupations = pd.read_csv(os.path.join(DATA_DIR, 'Occupation_Data.txt'), sep='\t')
tasks = pd.read_csv(os.path.join(DATA_DIR, 'Task_Statements.txt'), sep='\t')
task_ratings = pd.read_csv(os.path.join(DATA_DIR, 'Task_Ratings.txt'), sep='\t')
work_activities = pd.read_csv(os.path.join(DATA_DIR, 'Work_Activities.txt'), sep='\t')
abilities = pd.read_csv(os.path.join(DATA_DIR, 'Abilities.txt'), sep='\t')

# Find an occupation
occ = occupations[occupations['Title'].str.contains('Software Developer', case=False)]

# Get tasks for that occupation
soc_code = occ.iloc[0]['O*NET-SOC Code']
occ_tasks = tasks[tasks['O*NET-SOC Code'] == soc_code]

# Get work activities (importance scores)
occ_activities = work_activities[work_activities['O*NET-SOC Code'] == soc_code]

# Get abilities (importance scores)
occ_abilities = abilities[abilities['O*NET-SOC Code'] == soc_code]
```

This code can be run during analysis to pull specific occupation data for the company being evaluated.
