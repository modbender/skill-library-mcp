---
name: effortlist-ai
description: Manage EffortList AI folders, tasks, and todos. Use when the user wants to organize their life, track projects, or manage schedules via the EffortList AI platform. Supports full CRUD operations, cascading deletes, and atomic undo/redo history for data integrity.
metadata:
  {
    "homepage": "https://www.effortlist.io",
    "openclaw":
      { "emoji": "📋", "requires": { "env": ["EFFORTLIST_API_KEY"] } },
  }
---

# 📋 EffortList AI (Universal Skill)

## 🌟 Value Proposition (For Humans)

EffortList AI is a sophisticated life-management platform that merges advanced Generative AI with a robust, deterministic scheduling engine. Use this skill to give your agent full control over your project organization, time protection, and project lifecycles.

## 🚀 Setup & Authentication

1. **Subscription:** Requires a developer subscription ($5/month) at [effortlist.io](https://www.effortlist.io).
2. **API Key:** Human user must generate a **Persistent API Key** in Developer Settings.
3. **Storage:** Provide the key via the `EFFORTLIST_API_KEY` environment variable or OpenClaw internal config (`openclaw config set skills.entries.effortlist-ai.env.EFFORTLIST_API_KEY "your_key"`).

## 📐 Mental Model (Data Hierarchy)

EffortList AI operates on a strictly nested hierarchy:
**Folder (Container)** ──> **Task (Project)** ──> **Todo (Actionable Slot)**

- **Folders:** Optional top-level containers for grouping related projects.
- **Tasks:** Actionable projects that can be top-level or nested in a Folder.
- **Todos:** Granular actionable steps. **Every Todo MUST have a parent Task.**

## 🤖 Intelligence & Mapping (For Agents)

| User Intent      | Agent Workflow                     | Endpoint Goal                                  |
| :--------------- | :--------------------------------- | :--------------------------------------------- |
| "Plan a project" | Create Folder -> Tasks -> Todos    | `POST /folders`, `POST /tasks`, `POST /todos`  |
| "Fix my mistake" | Fetch History -> Target ID -> Undo | `GET /api/v1/undo`, `POST /api/v1/undo?id=...` |
| "Show my day"    | Fetch Todos by Date Range          | `GET /api/v1/todos?from=...&to=...`            |
| "Surgical Edit"  | Patch update a specific record     | `PATCH /api/v1/{type}?id=...`                  |

## 🛠️ Execution Logic (The "Omni" Way)

1. **Surgical Extraction & Patching:** Always prefer fetching a specific record by its ID (`GET ?id=...`) over broad list fetches. When updating, use `PATCH` with the record `?id=`.
2. **Phase-Aware Scheduling:** Be mindful of the 5-phase Omni processing loop (Temporal Resolution, Decomposition, Parallel Reasoning, Synthesis, and Break Validation). Proactively flag events with `isProtectedTime: true` to trigger the server-side safety net.
3. **Cascading Safety:** Be aware that deleting a Folder or Task is an **Atomic Purge**. However, the engine protects items that are simultaneously being updated from accidental deletion.
4. **Human Factors:** When proposing schedules, apply "Gap-First Placement" and "Human Factor" rules (e.g., leaving space for transitions).

## 🔒 Security & Privacy (Zero Trust)

- **Data Isolation:** Strict row-level security; users only see their own data.
- **AI Privacy:** Your personal data is **never** used to train models.

## 📖 Deep References

- **Full API Reference:** [API DOCs](https://www.effortlist.io/docs)
- **Omni Architecture:** (Located in references/architecture.md)
- **Security Audit Docs:** [SECURITY](https://www.effortlist.io/security)

**Project Version:** 1.7.5
