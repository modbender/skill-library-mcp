---
name: Data
slug: data
version: 1.0.1
changelog: Minor refinements for consistency
description: Work with data across the full lifecycle from extraction and cleaning to analysis, visualization, and reporting.
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs to: extract data from sources (databases, APIs, files), clean and transform messy datasets, analyze and find patterns, visualize results, or automate recurring data tasks. Agent handles the full data workflow.

## Quick Reference

| Area | File | Focus |
|------|------|-------|
| Querying & Extraction | `querying.md` | SQL generation, API fetching, multi-source |
| Cleaning & Transformation | `cleaning.md` | Nulls, duplicates, normalization, joins |
| Analysis & Statistics | `analysis.md` | EDA, statistical tests, insights |
| Visualization & Reporting | `visualization.md` | Charts, dashboards, exports |
| Quality & Validation | `quality.md` | Data checks, anomaly detection, drift |
| Workflow Patterns | `patterns.md` | Common data workflows, automation |

## Core Operations

**Query generation:** User describes what data they need → Agent writes SQL/query, handles joins, filters, aggregations → Returns results or explains execution plan.

**Data cleaning:** Load messy dataset → Detect issues (nulls, duplicates, outliers, inconsistent formats) → Apply appropriate fixes → Document transformations.

**Exploratory analysis:** New dataset arrives → Generate descriptive stats, distributions, correlations → Surface interesting patterns and anomalies → Produce summary with key findings.

**Visualization:** Analysis complete → Generate appropriate chart type → Export in requested format (PNG, SVG, interactive HTML) → Ready for stakeholders.

**Recurring reports:** Define report once → Agent runs on schedule → Updates charts and metrics → Delivers summary with highlights.

## Critical Rules

- Always preview transformations before applying — show sample of what will change
- Document every data transformation with source, operation, and rationale
- Validate data types and ranges before analysis — garbage in, garbage out
- Use appropriate statistical tests — check assumptions first
- Generate reproducible outputs — include seeds, versions, timestamps
- Handle missing data explicitly — document chosen strategy (drop, impute, flag)
- Match chart type to data type — categorical, continuous, time series

## User Modes

| Mode | Focus | Trigger |
|------|-------|---------|
| Analyst | SQL, exploration, insights | "What does this data tell us?" |
| Engineer | Pipelines, transformations, quality | "Clean this and load it there" |
| Business | KPIs, dashboards, plain language | "How are we doing vs last quarter?" |
| Researcher | Statistical rigor, reproducibility | "Is this difference significant?" |
| Developer | Schema design, API data, types | "Generate types from this JSON" |

See `patterns.md` for workflows per mode.

## On First Use

1. Identify data source (database, file, API)
2. Establish connection or load file
3. Initial EDA — shape, types, quality issues
4. Clean and transform as needed
5. Analyze or visualize per user goal
