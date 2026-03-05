---
name: resume-analyzer
description: "Professional resume analysis and optimization for UK job market. Use when user needs to (1) Analyze resume quality against a job description, (2) Get ATS compatibility score and keyword suggestions, (3) Optimize bullet points with quantifiable achievements, (4) Generate an improved version with tracked changes and annotations. Supports .docx format input/output."
---

# Resume Analyzer

Analyze resumes against job descriptions and generate optimized versions with detailed annotations.

## When to Use

- User provides a resume file (.docx) and wants analysis
- User provides both resume and JD for matching analysis  
- User wants ATS optimization suggestions
- User wants quantified achievements and stronger bullet points
- User wants an optimized version with explanations

## Workflow

### Step 1: Load & Parse Resume

Use `scripts/parse_resume.py` to extract content from .docx:
```bash
python scripts/parse_resume.py <input.docx> --output parsed_resume.json
```

### Step 2: Five-Dimension Analysis

Run analysis script with JD (if provided):
```bash
python scripts/analyze_resume.py parsed_resume.json [--jd job_description.txt] --output analysis_report.json
```

The analysis covers:
1. **JD Match Score** (0-100): Keyword overlap, skills alignment
2. **Quantification Score** (0-100): Presence of metrics, numbers, percentages
3. **Structure Logic** (0-100): Section order, readability, hierarchy
4. **Language Professionalism** (0-100): Action verbs, clarity, conciseness
5. **ATS-Friendliness** (0-100): Format, keywords, standard sections

### Step 3: Interactive Q&A

Present the 5-dimension report and ask follow-up questions:

**Questions to ask (user can select or type):**
- Which role at [Company X] had the biggest impact? What were the measurable results?
- Any specific project with quantifiable outcomes (revenue, users, efficiency)?
- Tools/technologies used that aren't mentioned?
- Any awards, recognition, or leadership experiences to highlight?
- Education details: GPA, relevant coursework, projects?

Store answers in `supplemental_data.json`.

### Step 4: Generate Optimized Version

```bash
python scripts/generate_optimized.py \
  parsed_resume.json \
  analysis_report.json \
  supplemental_data.json \
  --output optimized_resume.docx \
  --backup original_backup.docx
```

**Output files:**
- `original_backup.docx`: Clean copy of original
- `optimized_resume.docx`: Optimized version with **Word comments** explaining every change

### Step 5: Summary Output

Present to user:
- Original vs Optimized comparison (key changes)
- Score improvements (Before → After for each dimension)
- File locations

## Key Principles

### CAR Method for Bullet Points
Transform vague descriptions into CAR format:
- **C**ontext: What was the situation?
- **A**ction: What did YOU specifically do?
- **R**esult: What was the measurable outcome?

Example transformation:
- ❌ "Responsible for managing team and improving processes"
- ✅ "Led 8-person logistics team (Context), implemented new WSSI forecasting system (Action), reducing stockouts by 35% and saving £120K annually (Result)"

### ATS Optimization Rules

1. **Use standard section headers**: Experience, Education, Skills (not fancy variations)
2. **Include full keywords from JD**: If JD says "Supply Chain Optimization", use exact phrase
3. **Avoid tables, headers/footers, graphics**: ATS may not parse them
4. **File format**: .docx preferred over PDF for ATS

### Quantification Guidelines

Always seek numbers:
- Revenue: £X, $X, % growth
- Scale: X team members, X regions, X SKUs
- Efficiency: X% faster, X% cost reduction, X hours saved
- Impact: X customers, X users, X% satisfaction improvement

## Reference Materials

- **ATS Keywords**: See [references/ats_keywords.md](references/ats_keywords.md) for industry-specific keyword lists
- **Resume Templates**: See [references/resume_templates.md](references/resume_templates.md) for UK professional format examples
- **Action Verbs**: See [references/action_verbs.md](references/action_verbs.md) for strong starters

## Output Format

The optimized resume should:
1. Maintain user's original structure (unless severely flawed)
2. Add quantifiable metrics where possible
3. Use CAR format for bullet points
4. Include all JD keywords naturally
5. Have Word comments on EVERY change explaining the rationale

Comment format in Word:
- **Location**: [Section - Bullet Point]
- **Change**: [Original → Modified]
- **Reason**: [Why this improves the resume]
- **Evidence**: [Based on user's answer / JD requirement / Best practice]
