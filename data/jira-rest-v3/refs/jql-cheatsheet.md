# File: skills/jira-rest-v3/refs/jql-cheatsheet.md

# JQL Cheat Sheet (daily triage patterns)

## My open work
- `assignee = currentUser() AND statusCategory != Done ORDER BY priority DESC, updated DESC`

## Recently updated in a project
- `project = PROJ ORDER BY updated DESC`

## Unassigned issues
- `project = PROJ AND assignee IS EMPTY AND statusCategory != Done ORDER BY created DESC`

## “Needs review” label
- `project = PROJ AND labels = needs-review AND statusCategory != Done ORDER BY updated DESC`

## Updated in last 7 days
- `project = PROJ AND updated >= -7d ORDER BY updated DESC`

## Issues in a sprint (if Sprint field is present in your instance)
- `project = PROJ AND Sprint = "Sprint 42" ORDER BY Rank ASC`

## Text search
- `project = PROJ AND text ~ "timeout" ORDER BY updated DESC`

## Component-based triage
- `project = PROJ AND component = Backend AND statusCategory != Done ORDER BY priority DESC`