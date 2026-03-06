# Example: Demo Statistical Analysis

This is a complete example demonstrating the R research project workflow.

## Project Structure

```
demo-analysis/
├── data/
│   └── raw/
│       └── sample_data.csv      # Sample dataset with control/treatment groups
├── scripts/
│   └── demo_analysis.R          # Complete analysis script
├── results/
│   └── figures/                  # Generated plots (after running)
└── reports/
    └── demo_report.qmd           # Quarto report template
```

## How to Run

### Option 1: Run the analysis script

```r
# Navigate to the example directory
setwd("examples/demo-analysis")

# Run the analysis
source("scripts/demo_analysis.R")
```

This will:
- Load the sample data
- Calculate descriptive statistics
- Perform a t-test
- Generate box plot and scatter plot
- Save results to `results/figures/`

### Option 2: Generate the report

```bash
cd examples/demo-analysis
quarto render reports/demo_report.qmd
```

This creates `reports/demo_report.html` with formatted results.

## Sample Data

The `sample_data.csv` contains simulated data with:
- 15 observations
- 2 groups (control, treatment)
- 3 numeric variables (value1, value2, value3)

## Analysis Workflow

1. **Load data** - Import CSV with `read_csv()`
2. **Summarize** - Group-wise statistics with `dplyr`
3. **Test** - t-test for group comparison
4. **Visualize** - ggplot2 box plots and scatter plots
5. **Report** - Quarto document combining code and narrative

## Expected Output

After running the analysis:

```
results/figures/
├── boxplot.png       # Box plot by group
└── scatterplot.png   # Correlation scatter plot

reports/
└── demo_report.html  # Formatted report (if rendered)
```

## Extending This Example

Try modifying the script to:
- Add more statistical tests (ANOVA, correlation)
- Create additional visualizations (violin plots, heatmaps)
- Include data transformation steps
- Add a methods section to the report
