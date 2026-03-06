# Running R Analysis in Existing Projects

A Claude Code skill for extending, modifying, and debugging analyses within existing R projects.

## Features

- 🔍 **Understand Existing Code** - Reads and analyzes current scripts and reports
- ➕ **Incremental Extensions** - Adds new models, tests, and visualizations
- 🐛 **Debug Errors** - Fixes common R errors and missing packages
- 🔄 **Regenerate Reports** - Re-renders R Markdown/Quarto after changes
- 📦 **Respects Structure** - Works within existing project conventions
- 📊 **Update Visualizations** - Enhances or creates new ggplot2 figures

## Quick Start

Navigate to your existing R project and invoke the skill:

```
Add a survival analysis to this R project
```

```
Update the plots in my report with violin plots
```

```
This R Markdown file throws an error, fix it
```

```
Extend this analysis with a mixed-effects model
```

## Project Structure

The skill works with standard R project structures:

```
my-r-project/
├── data/
│   ├── raw/               # Original, immutable data files
│   └── processed/         # Cleaned, transformed data
├── scripts/               # R analysis scripts
├── results/
│   ├── figures/           # Plots and visualizations
│   ├── tables/            # Summary tables
│   └── models/            # Saved model objects
├── reports/               # R Markdown/Quarto documents
├── renv.lock              # Package version lock file
└── myproject.Rproj        # RStudio project file
```

## Usage Examples

### Example 1: Adding New Analysis

```
Add a logistic regression model to predict outcomes
```

The skill will:
- Read existing scripts to understand data structure
- Add `glm()` model with appropriate formula
- Save model summary to `results/models/`
- Create diagnostic plots
- Update report with new section

### Example 2: Updating Visualizations

```
Replace the boxplots with violin plots and add significance tests
```

The skill will:
- Locate existing plotting code
- Replace `geom_boxplot()` with `geom_violin()`
- Add statistical annotations (e.g., `stat_compare_means()`)
- Regenerate figures in `results/figures/`
- Re-render affected reports

### Example 3: Debugging

```
This script has an error when loading the data
```

The skill will:
- Read the error message
- Identify the issue (file path, missing package, etc.)
- Fix the code
- Verify the fix works

### Example 4: Data Update Workflow

```
I added new rows to the CSV, re-run everything
```

The skill will:
- Re-run data loading scripts
- Recompute all analyses
- Regenerate all plots
- Re-render reports with updated results

## Common Workflows

### Extending Analysis

```r
# Skill will add to existing scripts
# Example: Adding correlation analysis
cor_result <- cor.test(df$value1, df$value2)
# Save results
write_csv(as.data.frame(cor_result$estimate),
          here("results", "tables", "correlation.csv"))
```

### Updating Reports

```bash
# Skill re-renders after code changes
quarto render reports/analysis_report.qmd
# or
rmarkdown::render("report.Rmd")
```

### Installing Missing Packages

```r
# Skill detects and installs missing packages
install.packages("lme4")  # For mixed models
# Or Bioconductor
BiocManager::install("DESeq2")
```

## Supported Extensions

This skill can add:

- **Models**: Linear, logistic, mixed-effects, survival, GLM
- **Tests**: ANOVA, chi-square, Wilcoxon, correlation
- **Visualizations**: Violin plots, heatmaps, scatter plots, multi-panel figures
- **Data Processing**: Filtering, transformations, feature engineering
- **Report Sections**: Methods, discussion, appendices

## Best Practices

1. **Read before writing** - Understand existing code structure first
2. **Respect conventions** - Match existing coding style and folder organization
3. **Incremental changes** - Add without rewriting working code
4. **Test after changes** - Verify code runs before updating reports
5. **Document additions** - Add comments explaining new code

## Requirements

- Existing R project with standard structure
- R >= 4.0.0
- Required packages vary by analysis type

## Related Skills

- `creating-r-research-projects` - For starting new R projects from scratch

## License

MIT
