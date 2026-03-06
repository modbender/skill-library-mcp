# Creating R Research Projects

A Claude Code skill for creating reproducible, publication-ready R research projects with proper structure, package management, and automated reporting.

## Features

- 📁 **Standardized Project Structure** - Organized directories for data, scripts, results, and reports
- 📦 **Package Management** - Uses `renv` for reproducible R environments
- 📊 **Automated Analysis** - Template scripts for common statistical and bioinformatics tasks
- 📄 **Publication Reports** - R Markdown and Quarto templates for professional reports
- 🔄 **Version Control Ready** - Pre-configured `.gitignore` for R projects

## Quick Start

Invoke the skill by asking Claude to create an R research project:

```
Create an R project for analyzing my gene expression data
```

```
Set up a statistical analysis project in R for the clinical trial data
```

```
Build a reproducible R workflow for microbiome analysis
```

## Project Structure

When activated, this skill creates the following structure:

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
├── docs/                  # Additional documentation
├── renv.lock              # Package version lock file
├── .Rproj                 # RStudio project file
└── README.md              # Project documentation
```

## Usage Examples

### Example 1: Gene Expression Analysis

```
Create an R project to analyze RNA-seq differential expression

The skill will:
- Create project structure
- Install DESeq2, tidyverse, ggplot2
- Generate analysis script with DESeq2 workflow
- Create PCA and volcano plot templates
- Set up Quarto report for results
```

### Example 2: Statistical Modeling

```
Build an R project for regression analysis on this dataset

The skill will:
- Set up project directories
- Install stats, lme4, broom packages
- Create modeling script template
- Generate diagnostic plot functions
- Create report template for model summary
```

### Example 3: Data Visualization Dashboard

```
Create an R visualization project for the sales data

The skill will:
- Initialize ggplot2, patchwork, scales
- Create plotting templates
- Set up multi-panel figure layouts
- Generate export functions for different formats
```

## Common Workflows

### Starting a New Project

```r
# Run the initialization script
source("templates/project_template.R")

# Or manually:
renv::init()
# Install packages as needed
renv::snapshot()  # Save package state
```

### Running Analysis

```r
# Set working directory
setwd("my-project")
renv::activate()  # Load project-specific library

# Run analysis
source("scripts/01_data_preparation.R")
source("scripts/02_analysis.R")

# Generate report
quarto::quarto_render("reports/report.qmd")
```

### Restoring on Another Machine

```r
setwd("my-project")
renv::restore()  # Install exact package versions
```

## Templates Included

| Template | Description |
|----------|-------------|
| `project_template.R` | Complete project initialization script |
| `analysis.R` | Standard analysis script template |
| `report.qmd` | Quarto report template |
| `renv.lock.example` | Example package lock file |

## Supported Analyses

This skill supports creating workflows for:

- **Differential Expression**: DESeq2, edgeR, limma
- **Statistical Tests**: t-tests, ANOVA, chi-square, Wilcoxon
- **Regression Models**: Linear, logistic, mixed-effects (lme4)
- **Time Series**: Forecasting, decomposition
- **Clustering**: PCA, t-SNE, UMAP, hierarchical clustering
- **Visualization**: ggplot2, patchwork, complex multi-panel figures

## Best Practices

1. **Never modify raw data** - Always work on copies in `data/processed/`
2. **Use `renv::snapshot()`** after installing new packages
3. **Script everything** - Avoid interactive-only analysis
4. **Save all outputs** - Plots, tables, and model objects
5. **Document with reports** - Use Quarto/R Markdown for reproducibility

## Requirements

- R >= 4.0.0
- renv package: `install.packages("renv")`
- (Optional) RStudio for `.Rproj` support
- (Optional) Quarto CLI for advanced reports

## License

MIT

## Contributing

Suggestions and improvements welcome! This skill is designed to be a template for reproducible R research workflows.
