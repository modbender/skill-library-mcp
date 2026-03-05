# Envato Comment → Task → Google Sheet

## Overview

This skill analyzes ThemeForest / CodeCanyon comments and converts them into structured development tasks.

It classifies the comment type, assigns priority, extracts technical details, and outputs a JSON object designed to be pushed directly into Google Sheets.

## Input Parameters

- product_name
- product_url
- product_type (wordpress_theme | html_template | code_script)
- comment_text
- comment_url (optional)
- customer_name (optional)

## Output

Structured JSON task object formatted for Google Sheets row insertion.

## Classification Types

- bug
- feature_request
- support_question
- update_required
- refund_risk
- positive_feedback

## Priority Rules

- Fatal error / site break → critical
- Refund mention → critical
- Broken feature → high
- Feature request → medium
- Question → low

## Use Case

- Automate support workflow
- Track product health
- Improve update planning
- Reduce missed issues