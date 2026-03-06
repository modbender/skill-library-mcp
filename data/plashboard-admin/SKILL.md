---
name: plashboard-admin
description: Manage plashboard templates and autonomously convert natural-language dashboard requests into plashboard tool actions.
command-dispatch: tool
---

# Plashboard Admin

Use this skill for plashboard runtime administration.

## Use Cases
- Convert user requests like "I want dashboard X" into created/activated dashboards automatically.
- Create, update, copy, delete, and validate dashboard templates.
- Activate a template as the live dashboard source.
- Trigger immediate runs.
- Inspect runtime status and schedule health.
- Adjust display profile for layout budget checks.

## Required Tooling
Always use plugin tools:
- `plashboard_onboard`
- `plashboard_setup`
- `plashboard_exposure_guide`
- `plashboard_exposure_check`
- `plashboard_web_guide`
- `plashboard_doctor`
- `plashboard_permissions_fix`
- `plashboard_init`
- `plashboard_quickstart`
- `plashboard_template_create`
- `plashboard_template_update`
- `plashboard_template_list`
- `plashboard_template_activate`
- `plashboard_template_copy`
- `plashboard_template_delete`
- `plashboard_template_validate`
- `plashboard_run_now`
- `plashboard_status`
- `plashboard_display_profile_set`

## Guardrails
- Never edit `/var/lib/openclaw/plash-data/dashboard.json` directly.
- Never edit template/state/run JSON files directly.
- Never perform Docker, Tailscale, or systemd operations.
- Never ask the model to generate full dashboard structure when filling values.
- Do not tell end users to run slash commands when tool calls can do the action directly.

## Intent Automation
- If the user asks for a new dashboard in natural language, call `plashboard_onboard` with:
  - `description`: user request rewritten as a concrete dashboard objective
  - `force_quickstart`: `true`
  - `activate`: `true`
  - `run_now`: `true`
- If onboarding returns readiness issues, call `plashboard_web_guide` and `plashboard_exposure_guide`, then present exact operator commands.
- If the user asks to modify an existing dashboard, call `plashboard_template_list` first, then update/copy/activate/run via tools.
- Prefer tool execution over conversational planning; only ask clarifying questions if the request is ambiguous.

## Command Shortcuts
- `/plashboard onboard <description> [local_url] [https_port] [repo_dir]`
- `/plashboard quickstart <description>`
- `/plashboard setup [openclaw [agent_id]|mock|command <fill_command>]`
- `/plashboard doctor [local_url] [https_port] [repo_dir]`
- `/plashboard fix-permissions [dashboard_output_path]`
- `/plashboard web-guide [local_url] [repo_dir]`
- `/plashboard expose-guide [local_url] [https_port]`
- `/plashboard expose-check [local_url] [https_port]`
- `/plashboard init`
- `/plashboard status`
- `/plashboard list`
- `/plashboard activate <template-id>`
- `/plashboard copy <source-template-id> <new-template-id> [new-name] [activate]`
- `/plashboard delete <template-id>`
- `/plashboard run <template-id>`
- `/plashboard set-display <width> <height> <safe_top> <safe_bottom>`
