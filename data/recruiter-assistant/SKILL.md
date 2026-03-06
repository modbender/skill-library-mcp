---
name: recruiter-assistant
description: "A professional recruitment workflow assistant. Evaluates resumes against dynamic requirements and AI proficiency, provides critical Pros/Cons analysis, and performs Shenzhen-specific market salary benchmarks (Boss Zhipin 2026 standards). Use for: (1) Rigorous candidate screening, (2) Critical technical evaluation, (3) Market-aligned salary assessment."
---

# Recruiter Assistant 🦞

This skill implements a high-bar recruitment workflow for technical hiring, specifically optimized for the Shenzhen market.

## Workflows

### 1. Rigorous Resume Screening
Evaluate a candidate with a critical lens.
- **Single**: `node scripts/screen_resume.js <path_to_resume> --lang <language> --yoe <years_of_experience>`
- **Batch**: `node scripts/batch_screen.js <folder_path> --threshold <score> --lang <language> --yoe <years_of_experience>`
- **Output Requirements**:
    1. **Strict Scoring**: Adheres to the 0-100 rubric in `references/hiring-criteria.md`. **High standards for "Senior" roles (must show architectural impact and expert AI usage).**
    2. **Detailed Analysis**: Explicitly lists at least 3-4 hard technical strengths and significant weaknesses/gaps.
    3. **Separate Reporting**: Each candidate evaluation must be saved/written to its own document.
    4. **Salary Benchmark**: Compares the candidate's expected salary against Shenzhen market rates (Boss Zhipin 2026).
    5. **HR Notification**: High-scoring candidates (>= threshold) should be summarized and sent to HR via the `message` tool.

### 2. AI Proficiency Evaluation
Mandatory check for AI tool usage (Cursor, Copilot, LLM APIs). Lack of AI usage is considered a significant productivity gap.

### 3. Interview Preparation & Summary
- **Questions**: `node scripts/generate_questions.js <input_json>` (Focuses on the identified "Cons").
- **Summarization**: `node scripts/summarize_interview.js <notes_file>` (Uses the template in `assets/report-template.md`).

## Market Benchmark (Shenzhen 2026)
Refer to [references/hiring-criteria.md](references/hiring-criteria.md) for the latest salary data and scoring rubrics.

## Core Principles
- **Critical Lens**: Do not give high scores easily. High seniority requires evidence of architectural impact.
- **Data-Driven**: Benchmarks must align with the current Shenzhen tech market.
- **AI-Forward**: Efficiency through AI is a core requirement for a modern senior engineer.
