---
name: running-r-analysis-in-existing-projects
description: Work inside an existing R project to extend analyses, modify scripts, run statistical models, update visualizations, and regenerate reports.
---

# Running R Analysis in Existing Projects

This skill operates inside an already structured R project. It helps extend, debug, or enhance existing analyses without recreating the project from scratch.

Use this skill when the user wants to:
- Continue analysis in an existing R project
- Modify or extend R scripts
- Add new statistical models or tests
- Update plots or figures
- Regenerate reports after data or code changes
- Debug R errors in a project

---

## What This Skill Does

When activated, this skill will:

1. **Understand the project structure**
   - Detect folders like `data/`, `scripts/`, `results/`, `reports/`
   - Identify `.Rproj`, `.Rmd`, `.qmd`, or `.R` files

2. **Inspect existing analysis**
   - Read current scripts and reports
   - Identify which packages and methods are being used
   - Avoid rewriting working components unnecessarily

3. **Extend or modify analysis**
   - Add new models or statistical tests
   - Introduce new plots using `ggplot2`
   - Add new data processing steps
   - Improve code structure or reproducibility

4. **Re-run and update outputs**
   - Recompute results
   - Overwrite or version new outputs in `results/`
   - Re-render R Markdown or Quarto reports

5. **Debug issues**
   - Fix missing packages
   - Resolve file path problems
   - Handle common R errors and warnings

---

## Example User Requests That Should Trigger This Skill

- "Add a survival analysis to this R project"
- "Update the plots in my report"
- "This R Markdown file throws an error, fix it"
- "Extend this analysis with a mixed-effects model"
- "Re-run everything after I updated the data"

---

## Example Workflow

**User:** Add a logistic regression model and update the report.

**Skill actions:**
- Locate main analysis script
- Add logistic regression using `glm()`
- Save model summary to `results/`
- Update report with new section and plot
- Re-render HTML/PDF report

---

## Tools & Packages Commonly Used

| Purpose | R Packages |
|--------|------------|
| Data wrangling | tidyverse, dplyr |
| Modeling | stats, lme4, glmnet |
| Visualization | ggplot2 |
| Reporting | rmarkdown, quarto |
| Project management | here, renv |

---

## Notes

- Respect the existing project structure and style
- Do not delete user code unless explicitly requested
- Prefer incremental updates over full rewrites
- Always regenerate reports after modifying analysis
