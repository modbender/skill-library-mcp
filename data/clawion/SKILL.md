---
name: clawion
description: Multi-agent collaboration powered by OpenClaw cron jobs and the clawion CLI (wake-driven workflow).
---

# Clawion (runbook)

Clawion is a **file-based mission coordinator**. Agents interact with state through the **`clawion` CLI**.

Repo: https://github.com/natllian/clawion

## Mental model

Clawion is **wake-driven** — OpenClaw cron ticks are the engine.

1. Cron fires a periodic tick.
2. Agent runs **`clawion agent wake`** → receives the authoritative prompt for this turn.
3. Agent follows the **Turn Playbook** in that wake output.
4. Agent writes back via small actions (**message / working**).
5. Next wake reflects the updated workspace state.

Key properties:

- **Wake is the only read entrypoint.**
- **Unread handling is automatic:** wake shows "Unread Mentions" and auto-acks them.

## Core invariants

- **Workers complete tasks; managers maintain the board.**
  - Worker: reports progress and asks questions via `message add`; logs process via `working add`.
  - Manager: dispatches and maintains truth via `task create/assign/update`; also logs via `working add`. When the mission is complete, **disables all related cron jobs**.
- **Identity is explicit:** every action requires global `--agent <agentId>`.

---

## Quickstart (bootstrap a new mission)

### 0. Pre-flight

Verify the CLI is available:

```bash
clawion --help
```

If the command is not found, install it by following the setup instructions in the [Clawion README](https://github.com/natllian/clawion#readme).

### 1. Create the mission

```bash
clawion mission create --id <MISSION_ID> --name "..."
```

### 2. Register the manager (bootstrap rule)

The acting `--agent` must be the manager itself.

```bash
clawion agent add \
  --mission <MISSION_ID> \
  --id <MANAGER_ID> \
  --name "Manager" \
  --system-role manager \
  --role-description "..." \
  --agent <MANAGER_ID>
```

### 3. Register worker agents

```bash
clawion agent add \
  --mission <MISSION_ID> \
  --id <WORKER_ID> \
  --name "Worker" \
  --system-role worker \
  --role-description "..." \
  --agent <MANAGER_ID>
```

Repeat per worker.

### 4. Create and assign tasks (manager-only)

```bash
clawion task create \
  --mission <MISSION_ID> \
  --id <TASK_ID> \
  --title "..." \
  --description "..." \
  --agent <MANAGER_ID>

clawion task assign \
  --mission <MISSION_ID> \
  --task <TASK_ID> \
  --to <WORKER_ID> \
  --agent <MANAGER_ID>
```

### 5. Write the roadmap (manager-only, one-shot)

```bash
clawion mission roadmap --id <MISSION_ID> --set "<markdown>" --agent <MANAGER_ID>
```

> The roadmap can only be written **once** via the CLI. Any subsequent edits must be made by a human in the Web UI.

### 6. Create cron jobs (disabled) and get user approval

Create **one isolated cron job per agent** (manager + each worker), all **disabled**. Then ask the user to review in the Clawion Web UI before enabling anything. See [Cron jobs](#cron-jobs-openclaw) for payload rules and naming.

**Web UI review checklist:**

- Mission ROADMAP (editable)
- Each agent's role description (editable)
- Dark Secret injection settings (ensure secrets don't leak into thread messages)

Only enable cron jobs after **explicit user approval**.

---

## Cron jobs (OpenClaw)

### Hard rules

| Rule                | Detail                                                                                                                                                    |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Isolation**       | Each tick runs in its **own isolated OpenClaw session** (never `main`). Context bleed makes the loop unreliable.                                          |
| **Wake interval**   | If the user didn't specify one, **ask and confirm** before creating jobs.                                                                                 |
| **Minimal payload** | Do **not** embed mission context, task lists, or SOP text. The authoritative prompt is assembled by `clawion agent wake` from workspace state at runtime. |
| **Disabled first**  | Always create jobs disabled. Enable only after the user reviews in the Web UI (quickstart step 6).                                                        |

### Recommended cron message

**Worker:**

```text
Fetch your instructions by running:

clawion agent wake --mission <MISSION_ID> --agent <AGENT_ID>

Then follow the Turn Playbook in that output.
```

**Manager:**

```text
Fetch your instructions by running:

clawion agent wake --mission <MISSION_ID> --agent <AGENT_ID>

Then follow the Turn Playbook in that output.
If the mission is complete, disable all related cron jobs.
```

### Operational tips

- **Job naming:**
  - `clawion:<MISSION_ID>:manager:<AGENT_ID>`
  - `clawion:<MISSION_ID>:worker:<AGENT_ID>`
- **Stagger ticks** when multiple agents share the same interval to avoid bursty runs.
  - Given interval = `N` minutes and `K` agents, choose offsets: `round(i * N / K)` for `i = 0..K-1`.
  - Example: `N=10`, `K=3` → offsets `0m`, `3m`, `7m`.
