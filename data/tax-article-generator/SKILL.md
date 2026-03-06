---
name: tax-article-generator
description: Generate South African tax/VAT/SARS compliance articles
version: 1.0.0
author: Migration from Agent Zero
---

# Tax/VAT Article Generator Skill

## Overview
Automated generation of South African tax compliance articles covering SARS deadlines, VAT, PAYE, and provisional tax.

## Purpose
- Generate SEO-optimized tax articles for PayLessTax blog
- Ensure SARS deadline accuracy and compliance information
- Create structured content with JSON schemas for automation

## Input Variables (Template Placeholders)
| Variable | Description | Example |
|----------|-------------|---------|
| ARTICLE_TITLE | Complete article title | SARS 2026 Tax Season: Essential Compliance Dates |
| MAIN_KEYWORD | Primary SEO keyword | SARS 2026 compliance |
| YEAR | Tax year | 2026 |
| DEADLINE_1_DATE | First deadline date | 31 August 2026 |
| DEADLINE_1_NAME | First deadline description | Provisional Tax First Period |
| DEADLINE_2_DATE | Second deadline date | 28 February 2027 |
| DEADLINE_3_DATE | Third deadline date | 30 September 2027 |
| PENALTY_INFO | Penalty information | 10% of tax payable |
| INTEREST_RATE | Interest rate formula | repo rate + 4% |
| CTA_TEXT | Call-to-action | Download our checklist |

## Article Types

### SARS Compliance Guide
- Year-specific deadline overview
- Provisional tax due dates
- Annual return windows
- VAT submission schedules
- Penalty information

### VAT Article
- VAT 201 form details
- Category A/B/C/D/E schedules
- Late submission penalties
- Input/output tax rules

### PAYE Article
- EMP201 submission dates
- Monthly filing requirements
- UIF/SDL components

### Provisional Tax Guide
- IRP6 form instructions
- First, second, third periods
- Estimated tax calculations
- Penalties for underestimation

## Output Schema
```json
{
  "title": "generated title",
  "author": "PayLessTax Team",
  "content": "# Markdown content...",
  "seo_metadata": {...}
}
```

## Triggers
- Scheduled tax calendar events
- Manual CLI execution
- WordPress/WooCommerce webhook (optional)

## APIs & Dependencies
- Built-in Python (no external APIs)
- No secrets required (content generation only)
- Optional: WordPress REST API for publishing

## Files
- index.py - Article generator logic
- schemas/ - JSON schemas for each article type
- templates/ - Jinja2 templates
