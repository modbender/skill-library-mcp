---
name: rstudio-research-agent
description: Interact with R and RStudio environments for scientific research tasks including creating projects, running analyses, managing dependencies, and generating publication-quality plots.
---

# RStudio Research Agent

A Claude Code skill for comprehensive R-based research workflow automation. This skill enables interaction with R and RStudio environments for scientific computing, statistical analysis, bioinformatics, and data visualization.

## Overview

This skill helps researchers and data scientists:
- Create structured, reproducible R research projects
- Execute R scripts and RMarkdown analyses
- Debug environment and dependency issues
- Generate publication-quality plots and reports
- Manage R packages with renv for reproducibility

Use this skill when the user wants to:
- Create a new R project with standard structure
- Run R analyses on existing projects
- Troubleshoot R package dependencies
- Generate statistical reports or visualizations
- Set up reproducible R workflows

---

## What This Skill Does

When activated, this skill provides four main capabilities:

### 1. Create R Research Projects
- Scaffold new R projects with standard folder structure
- Initialize Git repositories (optional)
- Set up `renv` for package management
- Generate template scripts and reports
- Create `.Rproj` files for RStudio

### 2. Run Analyses in Existing Projects
- Execute R scripts and RMarkdown files
- Handle parameterized analyses
- Return results, tables, and plots
- Generate HTML/PDF reports

### 3. Debug Environment and Dependencies
- Check for missing R packages
- Resolve library conflicts
- Suggest fixes for environment issues
- Verify R version compatibility

### 4. Generate Publication-Quality Plots
- Create figures with ggplot2 and other visualization libraries
- Export to PDF/PNG/SVG/TIFF formats
- Follow journal-specific formatting guidelines
- Support multi-panel composite figures
- Use color-blind friendly palettes

---

## Example User Requests That Should Trigger This Skill

- "Create a new R project for my genomics data analysis"
- "Run `analysis.R` in my existing project and show results"
- "Check if all required packages are installed"
- "Generate a scatter plot with regression line from my dataset"
- "Set up a reproducible R workflow for RNA-seq analysis"
- "Debug my R environment - packages won't load"
- "Create a statistical report for this clinical trial data"

---

## Project Structure

Projects created by this skill follow this standardized structure:

```
my-research-project/
├── data/
│   ├── raw/               # Original, immutable data files
│   └── processed/         # Cleaned, transformed data
├── scripts/               # Analysis and processing scripts
├── results/
│   ├── figures/           # Plots and visualizations
│   ├── tables/            # Summary tables
│   └── models/            # Saved model objects (.rds files)
├── reports/               # R Markdown/Quarto documents
├── renv.lock              # Package version lock file
├── .Rproj                 # RStudio project file
└── README.md              # Project documentation
```

---

## Tools & Packages Commonly Used

| Purpose | R Packages |
|--------|------------|
| Data wrangling | tidyverse, data.table |
| Visualization | ggplot2, patchwork, scales |
| Statistics | stats, lme4, survival, broom |
| Bioinformatics | Bioconductor (DESeq2, edgeR, limma) |
| Reporting | rmarkdown, quarto |
| Reproducibility | renv |

---

## Example Workflows

### Creating a New Project

**User:** Create a new R project for gene expression analysis with Git initialized.

**Skill actions:**
1. Create directory structure (data/, scripts/, results/, reports/)
2. Initialize Git repository
3. Set up renv environment
4. Install DESeq2, tidyverse, ggplot2
5. Generate analysis template scripts
6. Create R Markdown report template

### Running an Analysis

**User:** Run the differential expression analysis and return results.

**Skill actions:**
1. Activate project environment (renv)
2. Execute analysis script
3. Capture console output and plots
4. Return summary tables and model statistics
5. Generate report if requested

### Debugging Dependencies

**User:** My R script fails with "package not found" errors.

**Skill actions:**
1. Check R version and package library paths
2. Scan script for required packages
3. Compare with installed packages
4. Generate installation commands
5. Check for version conflicts

---

## Notes

- Requires R >= 4.0.0
- Supports both RStudio and command-line R
- Uses `renv` for reproducible package management
- All outputs saved to files (not just console)
- Follows R best practices and modern conventions

---

## Sub-Skills

This skill includes specialized sub-skills:

- **create-project**: Scaffold new R research projects
- **run-analysis**: Execute R scripts and generate reports
- **debug-env**: Troubleshoot R environments and dependencies
- **generate-plots**: Create publication-quality figures with journal formatting

Each sub-skill can be invoked independently or as part of a complete workflow.
