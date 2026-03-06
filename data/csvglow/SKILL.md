---
name: csvglow
description: Generate beautiful interactive HTML dashboards from CSV/Excel files with smart insights, auto-detected charts, correlations, and statistics.
version: 0.1.0
metadata:
  openclaw:
    requires:
      bins:
        - csvglow
    emoji: "✨"
    homepage: https://github.com/ratnaditya-j/csvglow
---

# csvglow

Generate a beautiful, interactive HTML dashboard from any CSV or Excel file. Auto-detects column types and relationships, generates smart multi-column insights, histograms, bar charts, cross-analysis crosstabs, time series, correlation heatmaps, scatter plots, and a sortable data table — all in a single self-contained HTML file with a dark gradient theme.

Use this skill when the user wants to:
- Visualize a CSV or Excel file
- Create a dashboard from tabular data
- Explore or analyze a dataset visually
- Generate charts from a spreadsheet
- Get insights about their data

## Usage

```bash
csvglow <file>                       # Generate dashboard and open in browser
csvglow data.csv                     # CSV file
csvglow report.xlsx                  # Excel file
csvglow data.csv -o dashboard.html   # Custom output path
csvglow data.csv --no-open           # Don't auto-open browser
```

## What it generates

- **Smart insights**: Multi-column narrative analysis that cross-references metrics (e.g. "Gadget Y has the highest discount yet lowest revenue despite lowest cost — consider discontinuing")
- **Summary stats**: Row count, column count, data types, missing values
- **Numeric columns**: Histograms with stats sidebar (mean, median, std, quartiles, outlier count)
- **Categorical columns**: Gradient bar charts of top values
- **Cross analysis**: Automatic categorical x numeric crosstabs with overall mean lines
- **Date columns**: Time series line charts with area fill
- **Correlation heatmap**: Auto-detected correlations between numeric columns
- **Scatter plots**: Auto-generated for highly correlated pairs (|r| > 0.7)
- **Data table**: Sortable, filterable preview of first 1000 rows
- **Copy button**: Each chart has a "Copy" button for pasting into slide decks

## Notes

- Output is a self-contained HTML file — no server, no CDN, works offline
- Supports CSV, TSV, XLS, and XLSX files
- Auto-detects delimiters and encodings
- Large files (100k+ rows) are smart-sampled for visualizations while keeping full stats
- Also available as an MCP server: `csvglow --mcp`
