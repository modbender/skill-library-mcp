# Example: Extending an Existing R Project

This example demonstrates how the `running-r-analysis-in-existing-projects` skill works with an already-established R project.

## The Existing Project

This is a **basic** analysis project that contains:
- A simple dataset with control/treatment groups
- Basic t-test analysis
- A single boxplot visualization
- A basic Quarto report

## What This Skill Would Do

When activated in this project, the skill can:

### 1. Add New Analysis
- "Add correlation analysis between value1 and value2"
- "Include ANOVA for multiple group comparisons"
- "Add effect size calculations"

### 2. Extend Visualizations
- "Create a scatter plot showing value1 vs value2"
- "Add violin plots to compare distributions"
- "Create a combined multi-panel figure"

### 3. Enhance Reports
- "Update the report with new correlation section"
- "Add a methods section"
- "Include interactive plots with plotly"

### 4. Debug Issues
- "Fix the error when running the analysis"
- "Install missing packages"

### 5. Update After Data Changes
- "Re-run everything after I added new rows to the data"
- "Regenerate all plots with updated data"

## Example Workflow

**User request:** "Add a correlation analysis and scatter plot, then update the report."

**Skill actions:**
1. Reads `scripts/basic_analysis.R` to understand current approach
2. Adds correlation test (`cor.test()`) and scatter plot code
3. Creates new output file `results/correlation_analysis.csv`
4. Saves scatter plot to `results/scatterplot.png`
5. Updates `reports/basic_report.qmd` with new section
6. Re-renders the report to HTML

## Key Difference from Creating New Projects

| Creating New Projects | Extending Existing Projects |
|----------------------|----------------------------|
| Starts from scratch | Works with existing code |
| Creates all folders | Uses existing structure |
| Sets up dependencies | Adds to existing dependencies |
| Writes first draft | Extends/modifies existing code |
| "Create an R project..." | "Add X to this R project..." |
