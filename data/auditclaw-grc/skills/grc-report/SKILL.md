---
name: grc-report
description: Generate compliance report
user-invocable: true
metadata: {"openclaw":{"requires":{"bins":["python3"]}}}
---
# GRC Report

Generate a compliance report for a specific framework.

## What to do
Using the auditclaw-grc skill, ask which framework the user wants a report for (show active frameworks list), then generate the HTML compliance report.
Include compliance score, control status breakdown, evidence coverage, and gaps.
