# Markdown Report Generator

A skill that enables Claw to compile information from multiple sources into a polished, well-structured Markdown report with tables, sections, and optional PDF export.

## What This Skill Does

This skill provides a complete report generation workflow:

1. **Content Collection** — Gather information from provided text, files, URLs, or prior conversation context
2. **Structure Planning** — Organize content into logical sections with a table of contents
3. **Formatting** — Apply consistent Markdown formatting with headers, lists, tables, code blocks, and emphasis
4. **Table Generation** — Convert raw data into well-formatted Markdown tables
5. **Export** — Save as `.md` file, and optionally convert to PDF or HTML

## How to Use

Ask Claw to generate a report on any topic or from any data:

- "Create a project status report from these meeting notes"
- "Generate a comparison report of these three products with a feature table"
- "Write a technical documentation report for this codebase"
- "Compile a weekly summary report from these data points"

## Report Structure

Generated reports follow this template:

```
# Report Title
## Table of Contents
## Executive Summary
## Section 1: [Topic]
### Subsection with details
## Section 2: [Topic]
## Data Tables
## Conclusions & Recommendations
## Appendix (if applicable)
```

## Customization Options

- **Tone** — Formal, technical, executive summary, or casual
- **Length** — Brief (1-2 pages), standard (3-5 pages), or comprehensive (5+ pages)
- **Sections** — Specify which sections to include or exclude
- **Branding** — Add a custom header or footer text

## Output

- A `.md` file saved to the specified location
- Optional HTML or PDF conversion if requested
- Clean, consistent formatting ready for sharing or publishing
