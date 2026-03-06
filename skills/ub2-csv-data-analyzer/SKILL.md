---
name: CSV Data Analyzer
description: A skill that enables Claw to load, explore, analyze, and visualize
  CSV datasets, providing statistical insights and answering questions about the
  data.
---

# CSV Data Analyzer

A skill that enables Claw to load, explore, analyze, and visualize CSV datasets, providing statistical insights and answering questions about the data.

## What This Skill Does

This skill equips Claw with a structured approach to CSV data analysis:

1. **Data Loading & Inspection** — Read CSV files, detect column types, and display basic structure (shape, columns, sample rows)
2. **Data Cleaning** — Identify and handle missing values, duplicates, and type inconsistencies
3. **Statistical Summary** — Compute descriptive statistics (mean, median, mode, standard deviation, percentiles) for numeric columns
4. **Filtering & Grouping** — Slice data by conditions and aggregate by categories
5. **Correlation Analysis** — Find relationships between numeric variables
6. **Visualization** — Generate charts (bar, line, scatter, histogram) to illustrate patterns

## How to Use

Provide a CSV file and ask Claw to analyze it:

- "Analyze this sales data and tell me which product category has the highest revenue"
- "Find outliers in the temperature column of this dataset"
- "Create a chart showing monthly trends from this CSV"
- "Compare group A vs group B performance in this experiment data"

## Requirements

- Input must be a valid CSV file (comma-separated by default; other delimiters can be specified)
- Python with pandas and matplotlib should be available in the environment

## Output

- Summary statistics table
- Key insights in plain language
- Charts saved as PNG files when visualization is requested
- Cleaned dataset exported as a new CSV if data cleaning was performed
