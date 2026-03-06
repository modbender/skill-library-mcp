---
name: growthx-bx-submit
description: Submit your project to Built at GrowthX — the community builder showcase for GrowthX members. Requires a GrowthX API key.
metadata: {"openclaw":{"emoji":"🚀","requires":{"env":["GROWTHX_API_KEY"],"bins":["curl","jq","git"]},"primaryEnv":"GROWTHX_API_KEY"}}
---

# Built at GrowthX — Project Submission

Submit a project to **Built at GrowthX**, the community builder showcase for GrowthX members.

## When to Use

Activate this skill when the user wants to:

- Push, submit, or share a project to Built at GrowthX
- Post a project to the GrowthX builder showcase
- Publish their build on GrowthX

## Getting an API Key

If the user hasn't configured their API key yet, direct them to:

1. Go to **Built at GrowthX** on the GrowthX platform
2. Navigate to their profile / API key settings
3. Click **Generate API Key** — the raw key is shown once, copy it immediately
4. Set the key in OpenClaw config: add it under `skills.entries.growthx-bx-submit.apiKey` in `~/.openclaw/openclaw.json`, or set the `GROWTHX_API_KEY` environment variable

The key is tied to the user's GrowthX membership. If their membership lapses, the key stops working.

## API Endpoint

```
POST https://backend.growthx.club/api/v1/bx/projects/agent
```

### Authentication

Send the API key in the `x-api-key` header:

```
x-api-key: <GROWTHX_API_KEY>
```

### Request Body (JSON)

**Required fields:**

| Field | Type | Constraints |
|-------|------|-------------|
| `name` | string | Max 100 characters. The project name. |
| `tagline` | string | Max 200 characters. A short one-liner about the project. |

**Optional fields:**

| Field | Type | Default | Constraints |
|-------|------|---------|-------------|
| `description` | string | `""` | Max 2000 characters. Longer project description. |
| `category` | string | `"SaaS"` | e.g. SaaS, Fintech, Marketplace, EdTech, HealthTech, AI/ML, Developer Tools, E-commerce |
| `stack` | string[] | `[]` | Tech stack tags, e.g. `["React", "Node.js", "MongoDB"]` |
| `url` | string | `null` | Project URL (must be a valid URI) |
| `status` | string | `"shipped"` | One of: `shipped`, `idea`, `prototyping`, `beta` |
| `buildathon` | string | `null` | Name of a buildathon if this project was built during one |

### Example Request

```bash
curl -X POST "https://backend.growthx.club/api/v1/bx/projects/agent" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $GROWTHX_API_KEY" \
  -d '{
    "name": "TaskFlow",
    "tagline": "AI-powered task management for remote teams",
    "description": "TaskFlow uses AI to automatically prioritize and assign tasks based on team capacity and deadlines.",
    "category": "SaaS",
    "stack": ["React", "Node.js", "OpenAI", "PostgreSQL"],
    "url": "https://taskflow.app",
    "status": "shipped"
  }' | jq .
```

### Success Response (201)

```json
{
  "project": {
    "_id": "...",
    "name": "TaskFlow",
    "tagline": "AI-powered task management for remote teams",
    "status": "shipped",
    "creator": { "name": "...", "avatar_url": "..." },
    "weighted_votes": 0,
    "raw_votes": 0
  }
}
```

## Agent Behavior

When the user asks to submit a project, follow these steps in order:

### Step 1 — Detect Projects in the Workspace

Scan standard project files in the current workspace to discover what the user has built. Only read these files:

**Project manifest files:**

- `package.json` — `name`, `description`, `keywords`, `homepage`, `repository`
- `pyproject.toml` / `setup.py` / `setup.cfg` — `name`, `description`, `urls`
- `Cargo.toml` — `name`, `description`, `repository`, `keywords`
- `go.mod` — module name
- `pubspec.yaml` — `name`, `description`, `homepage`

**Documentation:**

- `README.md` — project title (first `#` heading) and opening paragraph
- `git remote -v` — repository URL

**Monorepo detection:**

For monorepos, check for workspace configs (`workspaces` in root `package.json`, `pnpm-workspace.yaml`, `turbo.json`, `nx.json`) or subdirectories with their own manifest files. Each workspace package with its own `name`/`description` is a candidate project.

**How to infer fields:**

| Field | How to Infer |
|-------|-------------|
| `name` | `name` field from manifest file, or first heading in README |
| `tagline` | `description` field from manifest, or first sentence of README |
| `description` | Summarize from README content and manifest description (1-3 sentences) |
| `stack` | Dependencies and devDependencies from manifest (e.g. `react` → "React", `express` → "Express", `django` → "Django") |
| `url` | `homepage` field from manifest, or repository URL from git remote |
| `category` | Infer from dependencies and README (e.g. `stripe` → "Fintech", `next` → "SaaS", ML libraries → "AI/ML") |
| `status` | Default to `"shipped"`. If README explicitly says WIP/prototype/beta, use that instead. |

### Step 2 — Present Discovered Projects

Show the user what you found. If multiple projects were detected (e.g. monorepo packages), list them and ask which one to submit:

> I found these projects in your workspace:
> 1. **project-name** — short description
> 2. **other-project** — short description
>
> Which one would you like to submit to Built at GrowthX?

If only one project is detected, present its details directly and ask to confirm.

### Step 3 — Fill in Missing Details

For the selected project, show what was auto-detected and ask the user to fill in or correct anything:

- `name` and `tagline` are **required** — if the tagline can't be inferred, ask for it
- Show the auto-detected `stack`, `category`, `url`, `description`, and `status` and let the user adjust
- Default `status` to `"shipped"` unless README or context suggests it's still in progress

### Step 4 — Confirm and Submit

Show a final summary of all fields that will be sent:

> **Submitting to Built at GrowthX:**
> - Name: TaskFlow
> - Tagline: AI-powered task management for remote teams
> - Category: SaaS
> - Stack: React, Node.js, OpenAI, PostgreSQL
> - URL: https://taskflow.app
> - Status: shipped
>
> Submit this?

Only after the user confirms, make the API call using curl with the `x-api-key` header.

### Step 5 — Report Result

On success, tell the user their project was submitted and share the project link if available. On failure, explain the error (see below).

## Error Handling

| Status | Meaning | What to Tell the User |
|--------|---------|----------------------|
| `401` | Invalid or revoked API key | "Your API key is invalid or has been revoked. Please generate a new one from the Built at GrowthX settings." |
| `403` | Membership not active | "Your GrowthX membership is not active. An active membership is required to submit projects." |
| `400` | Validation error (missing name/tagline, field too long, etc.) | Show the specific validation error from the response body. |
