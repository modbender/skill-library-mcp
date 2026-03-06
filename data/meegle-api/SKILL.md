---
name: meegle-api
description: Meegle Open API skills index. Read credentials first; missing credentials → see meegle-api-credentials and remind user where to get them.
metadata: {"openclaw":{"requires":{"env":["MEEGLE_PLUGIN_ID","MEEGLE_PLUGIN_SECRET","MEEGLE_DOMAIN","MEEGLE_PROJECT_KEY","MEEGLE_USER_KEY"]}}}
---

# Meegle API (index)

Read **meegle-api-credentials** first (domain, token, context, headers); then the skill that matches your task. Use read-file on **Path**; `{baseDir}` = skill pack root.

| Order | Path | When to read |
|-------|------|--------------|
| 1 | **{baseDir}/meegle-api-credentials/SKILL.md** | Domain, token, context, headers — before any Meegle API call |
| 2 | **{baseDir}/meegle-api-users/SKILL.md** | User APIs (groups, members) |
| 3 | **{baseDir}/meegle-api-space/SKILL.md** | Space (project) operations |
| 4 | **{baseDir}/meegle-api-work-items/SKILL.md** | Work items CRUD, list, search |
| 5 | **{baseDir}/meegle-api-setting/SKILL.md** | Settings, types, fields, process |
| 6 | **{baseDir}/meegle-api-comments/SKILL.md** | Comments on work items |
| 7 | **{baseDir}/meegle-api-views-measurement/SKILL.md** | Views, kanban, Gantt, charts |
