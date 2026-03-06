# Interview Analysis

**Dynamic Expert Routing for Candidate Assessment**

Transform interview transcripts into deep capability insights. The AI automatically selects domain-specific evaluation frameworks (Marty Cagan for PM, John Carmack for Engineering) and distinguishes genuine Battle Scars from Methodology Recitation.

---

## When to Use This Skill

Use this skill when:

- You have interview transcripts and need deep capability analysis
- You want to identify genuine "Battle Scars" vs "Methodology Recitation"
- You're evaluating candidates across diverse roles (PM, Engineering, Design, Sales, Data Science, etc.)
- You need structured output (Profile + Insights + Meta-Analysis cards) for hiring decisions

---

## How It Works: Expert Routing

| Candidate Role   | Domain Expert        | Hiring Expert | Output Focus                    |
|------------------|-----------------------|---------------|----------------------------------|
| Product Manager  | Marty Cagan / Julie Zhuo | Geoff Smart   | Product Sense + Fact Check      |
| Software Engineer| Linus Torvalds / John Carmack | Lou Adler     | Engineering Judgment + Results  |
| UX Designer      | Don Norman / Jony Ive | Lou Adler     | UX Principles + Portfolio       |
| Data Scientist   | Andrew Ng / DJ Patil  | Geoff Smart   | Technical Depth + Projects      |
| Growth / Sales   | Sean Ellis / Aaron Ross | Geoff Smart   | Methodology + Metrics Verification |

*The AI selects the most appropriate expert combination based on role context. You can override or add experts; the table is reference, not constraint.*

---

## What You Get

| Output           | Template                      | Purpose                                      |
|------------------|-------------------------------|----------------------------------------------|
| **Profile**      | `templates/profile_template.md`     | Resume verification, red flags, competency  |
| **Insight**      | `templates/insight_template.md`     | Domain-specific capability deep dive        |
| **Evaluation**   | `templates/evaluation_template.md`  | Interviewer meta-analysis & recommendations |
| **Structure Note** | `templates/structure_note_template.md` | Hub document linking all analysis cards    |

Cards are written to `people/{candidate_name}/analysis/` in Zettelkasten-friendly Markdown.

---

## Core Methodology

1. **Fact Reconstruction** — Timeline verification, consistency across rounds, red-flag annotation (vague titles, exaggerated data).
2. **Deep Decoding** — STAR episode analysis: first-principles vs SOP recitation, solution bias, technical boundary checks.
3. **Interviewer Meta-Analysis** — Depth of probing, bias control, bar-holding.

---

## Quick Reference

| Analysis Need              | Template                 | Expert Framework              |
|---------------------------|--------------------------|-------------------------------|
| Candidate credibility     | `profile_template.md`    | Geoff Smart (Topgrading)      |
| Role-specific capability  | `insight_template.md`    | Dynamic domain expert         |
| Interview quality review  | `evaluation_template.md` | Lou Adler + Kahneman          |

---

## Install

**ClawHub (OpenClaw)**:
```bash
npx clawhub@latest install interview-analysis
```

**Other (e.g. skills.sh)**:
```bash
npx skills add mikonos/interview-analysis
```

Compatible with Cursor, Claude Code, OpenClaw, and other agents that support the skills protocol.
