---
name: pms-task
description: "Create PMS tasks (bugs or features) on GitHub and sync to Google Sheets. Use when user says 'PMS Bug addition' for bugs or 'PMS Feature addition' for features. Creates GitHub issue with appropriate labels, assigns to roshanasingh4, updates PMS Task Tracker sheet and Team Daily Update sheet."
---

# PMS Task Addition (Bug & Feature)

Streamlined workflow for logging PMS bugs AND features to GitHub and Google Sheets.

## Trigger
User message contains:
- **"PMS Bug addition"** → Creates a BUG report
- **"PMS Feature addition"** → Creates a FEATURE request

## Workflow

### 1. Determine Task Type
Based on trigger phrase:
| Trigger | Type | GitHub Label | Sheet Task Type |
|---------|------|--------------|-----------------|
| "PMS Bug addition" | Bug | `bug` | `Issue` |
| "PMS Feature addition" | Feature | `enhancement` | `Feature` |

### 2. Collect Task Information
Ask the user for (if not provided):
- **Title**: Brief summary
- **Description**: What's happening (bug) or what's needed (feature)
- **Reproduction Steps**: (Bugs only) How to reproduce
- **Expected Outcome**: What should happen
- **Priority**: P0 (Critical) / P1 (High) / P2 (Medium) / P3 (Low)

### 3. Create GitHub Issue

#### For BUGS:
```bash
gh issue create --repo roshanasingh4/apni-pathshala-pms \
  --title "<title>" \
  --body "$(cat <<EOF
## Description
<description>

## Steps to Reproduce
1. <step 1>
2. <step 2>
3. <step 3>

## Expected Outcome
<expected outcome>

## Actual Outcome
<what actually happened>
EOF
)" \
  --label "bug,<priority>" \
  --assignee roshanasingh4
```

#### For FEATURES:
```bash
gh issue create --repo roshanasingh4/apni-pathshala-pms \
  --title "<title>" \
  --body "$(cat <<EOF
## Feature Request
<description>

## Expected Behavior
<expected outcome>

## Use Case
Why is this feature needed?
EOF
)" \
  --label "enhancement,<priority>" \
  --assignee roshanasingh4
```

Capture the issue URL from output for the sheet.

### 4. Update PMS Task Tracker Sheet
**Sheet ID:** `1O07SzGzQa2FwpkBE7h2SUDWZlxsUpz8DxCpyxKjRi8U`
**Tab:** `Production`

#### Column Mapping (A-K)

| Col | Name | Value |
|-----|------|-------|
| A | Task ID | `PMS-TSKXXX` (increment from last entry) |
| B | Description | Issue title |
| C | Reporter | `Tara Singh Kharwad` |
| D | Date Submitted | `DD/MM/YYYY` (issue creation date) |
| E | Status | `New` |
| F | Task type | `Issue` (bug) / `Feature` (enhancement) / `Testing` |
| G | Priority | `Critical` (P0) / `High` (P1) / `Medium` (P2) / `Low` (P3) |
| H | Assigned To | `tarasinghrajput7261@gmail.com` |
| I | Resolution Notes | GitHub issue URL |
| J | Resolution Date | (empty until closed) |
| K | Took Help from Roshan | (leave empty - Tara fills manually) |

#### Label to Sheet Mapping

| GitHub Label | Task Type | Priority |
|--------------|-----------|----------|
| bug | Issue | - |
| enhancement | Feature | - |
| P0 | - | Critical |
| P1 | - | High |
| P2 | - | Medium |
| P3 | - | Low |

#### Get Next Task ID
```bash
gog sheets get 1O07SzGzQa2FwpkBE7h2SUDWZlxsUpz8DxCpyxKjRi8U "Production!A:A" --json | jq '.values | .[-1][0]'
```
Then increment the number.

#### Append to Sheet (BUG)
```bash
gog sheets append 1O07SzGzQa2FwpkBE7h2SUDWZlxsUpz8DxCpyxKjRi8U "Production!A:K" \
  --values-json '[["PMS-TSK-XXX","<title>","Tara Singh Kharwad","DD/MM/YYYY","New","Issue","Low","tarasinghrajput7261@gmail.com","<github_url>","",""]]' \
  --insert INSERT_ROWS
```

#### Append to Sheet (FEATURE)
```bash
gog sheets append 1O07SzGzQa2FwpkBE7h2SUDWZlxsUpz8DxCpyxKjRi8U "Production!A:K" \
  --values-json '[["PMS-TSK-XXX","<title>","Tara Singh Kharwad","DD/MM/YYYY","New","Feature","Low","tarasinghrajput7261@gmail.com","<github_url>","",""]]' \
  --insert INSERT_ROWS
```

### 5. Update Team Daily Update Sheet
**Sheet ID:** `1GgRgfVBrF-ReGPRmntT6Cm2BjiLzJ3JiBaC4lMfrMQs`

Find row with today's date, append to Column B with format:
```
- PMS - <title> - <github_url>
```

#### Format for Daily Tasks
Each day's tasks are in a single cell with headings and bullet points:
```
- PMS - Fixed login button issue - https://github.com/...
- PMS - Added export feature - https://github.com/...
```

#### Get Today's Row
```bash
# Find row with today's date
gog sheets get 1GgRgfVBrF-ReGPRmntT6Cm2BjiLzJ3JiBaC4lMfrMQs "Sheet1!A:B" --json
# Look for today's date (DD/MM/YYYY) in Column A
```

#### Update Cell
```bash
# Append to existing content in Column B
gog sheets update 1GgRgfVBrF-ReGPRmntT6Cm2BjiLzJ3JiBaC4lMfrMQs "Sheet1!B<row>" \
  --values-json '[["<existing_content>\n- PMS - <title> - <github_url>"]]'
```

## Priority Guide

| Priority | Label | When to Use |
|----------|-------|-------------|
| P0 | Critical | System down, data loss, security issue |
| P1 | High | Major feature broken/needed, many users affected |
| P2 | Medium | Feature partially working/needed, workaround exists |
| P3 | Low | Minor issue, cosmetic, low impact |

## Example Usage

### Bug Example
User: "PMS Bug addition - Login page crashes on mobile"

Response:
1. Detect: **BUG** → GitHub label: `bug`, Sheet type: `Issue`
2. Ask for details (steps, expected outcome, priority)
3. Create GitHub issue with bug template → get URL
4. Get next Task ID from sheet
5. Append to PMS Task Tracker with Task type = "Issue"
6. Update Team Daily Update sheet with new entry

### Feature Example
User: "PMS Feature addition - Add dark mode support"

Response:
1. Detect: **FEATURE** → GitHub label: `enhancement`, Sheet type: `Feature`
2. Ask for details (description, expected behavior, use case, priority)
3. Create GitHub issue with feature template → get URL
4. Get next Task ID from sheet
5. Append to PMS Task Tracker with Task type = "Feature"
6. Update Team Daily Update sheet with new entry

## Quick Reference

| Trigger | GitHub Label | Sheet Task Type | Issue Template |
|---------|--------------|-----------------|----------------|
| PMS Bug addition | `bug` | `Issue` | Bug report with reproduction steps |
| PMS Feature addition | `enhancement` | `Feature` | Feature request with use case |

## Notes

- Reporter is ALWAYS "Tara Singh Kharwad"
- Assigned To is ALWAYS "tarasinghrajput7261@gmail.com"
- Resolution Notes = GitHub issue URL
- "Took Help from Roshan" is left empty (Tara fills manually)
- Date format: DD/MM/YYYY only
- Status starts as "New"
