---
name: content-strategy-analyzer
description: Analyzes websites to generate multi-language content strategy, keyword research, and competitor analysis. Use when user provides a URL and needs industry analysis, SEO planning, or competitor research for content marketing in specific countries and languages.
---

# Content Strategy Analyzer

## Quick Start

1. User inputs target website URL + target country/language + publish frequency
2. Use scripts/crawl_website.py to crawl website content
3. AI analysis (considering target language and country)
4. Confirm/adjust competitor list
5. Use scripts/generate_excel.py to generate content plan Excel
6. Output complete report (in target language)

## Dependencies

Required packages:
```bash
pip install requests beautifulsoup4 openpyxl
```

## Workflow

### Step 1: Collect User Requirements

Must ask user for:

1. **Target Website URL** - Website to analyze
2. **Target Country** - Country for content targeting (e.g., USA, UK, Germany, China)
3. **Target Language** - Content language (e.g., English, Chinese, German, French)
4. **Publish Frequency** - Weekly / Bi-weekly / Monthly

### Step 2: Crawl Target Website

```bash
python3 scripts/crawl_website.py <URL>
```

### Step 3: AI Analysis (Multi-language)

Use Opencode AI for analysis:
- Identify industry and competitors based on target country
- Output keywords in target language
- Include target country market in competitor analysis

### Step 4: Generate Content Plan

Based on publish frequency:
- **Weekly**: 12 weeks (3 months) × 1 topic
- **Bi-weekly**: 6 topics (one every two weeks)
- **Monthly**: 3 topics (one per month)

All content titles, topics, and ideas in target language.

### Step 5: Output Report

1. Markdown format in conversation (target language)
2. Excel file

## Scripts

### scripts/crawl_website.py

Crawls main website content, outputs structured JSON.

### scripts/generate_excel.py

Generates Excel file from analysis results.

Input: analysis_result.json
Output: content_plan.xlsx

## Output Format

### Example User Input

| Parameter | Value |
|-----------|-------|
| URL | https://example.com |
| Country | Germany |
| Language | German |
| Frequency | Weekly |

### Content Plan Output (German Example)

| Month | Week | Theme | Title | Type |
|-------|------|-------|-------|------|
| Month 1 | Week 1 | Market Launch | ... | Article |
