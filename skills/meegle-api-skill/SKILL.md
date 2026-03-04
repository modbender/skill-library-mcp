---
name: meegle-api
description: |
  Meegle Open API skills (index). Read the specific skill for your need. Order: Credentials, Users, Space, Work Items, Setting, Comments, Views & Measurement.
  When required credentials (e.g. user_key, project_key) are missing, remind the user which are needed and where to get them (see meegle-api-credentials); do not only report an error.
metadata:
  openclaw: {}
---

# Meegle API (index)

Meegle OpenAPI is split into the following skills. Read **meegle-api-credentials** first for domain, token, context, and request headers; then read the skill that matches your task.

| Order | Sub-skill (path) | When to read |
|-------|------------------|--------------|
| 1 | **meegle-api-credentials/SKILL.md** | Domain, token, context (project_key, user_key), request headers. Read this before any other Meegle API call. |
| 2 | **meegle-api-users/SKILL.md** | User-related OpenAPIs (e.g. user groups, members). |
| 3 | **meegle-api-space/SKILL.md** | Space (project) operations. |
| 4 | **meegle-api-work-items/SKILL.md** | Create, get, update work items (tasks, stories, bugs). |
| 5 | **meegle-api-setting/SKILL.md** | Settings, work item types, fields, process configuration. |
| 6 | **meegle-api-comments/SKILL.md** | Comments on work items or other entities. |
| 7 | **meegle-api-views-measurement/SKILL.md** | Views, kanban, Gantt, charts, measurement. |

Each sub-skill lives under `meegle-api-skill/` (e.g. `meegle-api-users/SKILL.md`). Use the `Read` tool on the relevant path when you need that API area.
