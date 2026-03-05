# Degree Management

## Setting Up a New Degree

### Autodidact Mode (Full Replacement)
1. **Explore interests** — Ask diagnostic questions, analyze responses, suggest 3-5 fitting careers
2. **Compare options** — Generate table: job market, time required, difficulty, ROI, trends
3. **Reality check** — Describe "day in the life" for chosen career
4. **Generate curriculum** — Full program equivalent to 4-6 year degree:
   - Modules with dependencies mapped
   - Resources curated per topic (books, courses, papers)
   - Practical components (projects, cases, labs)
   - Official certifications to pursue
5. **Create timeline** — Based on available hours/week
6. **Store** — Create degrees/[name]/ with curriculum.md, progress.md, calendar.md

### Student Mode (University Support)
1. **Import course list** — Extract from syllabus/schedule
2. **Add exam dates** — From PDFs or manual entry
3. **Link resources** — Connect uploaded materials to courses
4. **Generate study plans** — Per exam, with spaced review
5. **Track across semesters** — Unified view of all courses

### Career Change Mode
1. **Assess current skills** — What transfers to target field?
2. **Gap analysis** — What's missing for employability?
3. **Prioritize by ROI** — Skills that unlock jobs fastest
4. **Portfolio projects** — Generate ideas that demonstrate skills
5. **Certification roadmap** — Which exams validate progress?
6. **Timeline with milestones** — "In 6 months you should have X"

### Exam Prep Mode (Certifications/Competitive)
1. **Import official syllabus** — Structure by topics and weights
2. **Analyze past exams** — What topics appear most? What format?
3. **Create study plan** — Weighted by topic importance
4. **Generate unlimited practice** — Tests, cases, oral simulations
5. **Track mastery** — Per topic, with predicted score
6. **Monitor changes** — Alert if syllabus updates (BOE, official sources)

### Tutor Mode (Helping Others)
1. **Understand their curriculum** — What are they studying?
2. **Assess their level** — Diagnostic tests by subject
3. **Identify struggles** — What topics are hard?
4. **Generate support materials** — Explanations, practice, flashcards
5. **Weekly reports** — For parents/guardians (optional)
6. **Motivational tracking** — Celebrate progress, detect frustration

## Curriculum Structure

### curriculum.md Format
```markdown
# [Degree Name]

## Overview
- Total estimated hours: X
- Weekly commitment: X hours
- Expected completion: [date]

## Prerequisites
- [Required prior knowledge]

## Modules

### Module 1: [Name]
- **Hours:** X
- **Prerequisites:** None
- **Topics:** [list]
- **Resources:**
  - Book: [title]
  - Course: [link]
  - Practice: [link]
- **Assessment:** [type]
- **Certification:** [if applicable]

### Module 2: [Name]
- **Prerequisites:** Module 1
...
```

### progress.md Format
```markdown
# Progress: [Degree Name]

## Summary
- Started: [date]
- Modules completed: X/Y
- Hours logged: X
- Mastery average: X%

## By Module

| Module | Status | Mastery | Last Review |
|--------|--------|---------|-------------|
| Mod 1 | ✅ Complete | 85% | 2026-02-10 |
| Mod 2 | 🔄 In Progress | 60% | 2026-02-14 |
| Mod 3 | ⬜ Not Started | - | - |
```

## Managing Multiple Degrees

- index.md lists all active degrees with status
- Each degree is independent but shares:
  - Study schedule (config.md)
  - Flashcard system
  - Resource library
- Cross-reference related topics across degrees
- Balance time allocation if multiple active

## Archiving Completed Degrees

When a degree is complete:
1. Generate completion certificate summary
2. Move to degrees/archive/[name]/
3. Keep for reference but exclude from active tracking
