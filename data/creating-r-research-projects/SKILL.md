---
name: creating-r-research-projects
description: Set up a reproducible R research workspace, install required packages, run statistical or bioinformatics analysis, and generate publication-ready reports and visualizations.
---

# Creating R Research Projects

This skill helps create and manage a complete R-based research analysis workflow. It is designed for scientific computing, statistical modeling, bioinformatics, and data visualization tasks.

Use this skill when the user wants to:
- Analyze datasets using R
- Perform statistical tests or modeling
- Run bioinformatics or omics analysis in R
- Generate plots, figures, or reports
- Create a reproducible R project structure
- Install and manage R package dependencies

---

## What This Skill Does

When activated, this skill will:

1. **Create a structured R project**
   - `data/` for raw and processed data
   - `scripts/` for analysis code
   - `results/` for outputs
   - `reports/` for R Markdown or Quarto reports

2. **Set up environment**
   - Initialize `.Rproj` (if using RStudio)
   - Create `renv` environment for reproducibility
   - Install required CRAN/Bioconductor packages

3. **Generate analysis scripts**
   - Data loading and cleaning
   - Statistical analysis or modeling
   - Visualization with `ggplot2`
   - Save outputs (CSV, plots, model summaries)

4. **Create a report**
   - R Markdown / Quarto document
   - Includes methods, results, and figures
   - Render to HTML or PDF

---

## Example User Requests That Should Trigger This Skill

- "Use R to analyze this CSV and generate plots"
- "Run differential expression analysis in R"
- "Create a statistical report for this dataset"
- "Build an R project for microbiome analysis"
- "Fit a regression model in R and summarize results"

---

## Example Workflow

**User:** Analyze this gene expression dataset and produce figures.

**Skill actions:**
- Create project structure
- Install `tidyverse`, `DESeq2`, `ggplot2`
- Write analysis script
- Generate PCA plot and volcano plot
- Produce an HTML report

---

## Tools & Packages Commonly Used

| Purpose | R Packages |
|--------|------------|
| Data wrangling | tidyverse, data.table |
| Visualization | ggplot2, patchwork |
| Statistics | stats, lme4, survival |
| Bioinformatics | Bioconductor packages (DESeq2, edgeR, limma) |
| Reporting | rmarkdown, quarto |
| Reproducibility | renv |

---

## Notes

- Prefer reproducible workflows (`renv`, scripted analysis)
- Avoid interactive-only steps unless requested
- All outputs should be saved to files, not just printed to console
