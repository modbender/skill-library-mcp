---
name: openclaw-default-agent-backstory
description: Build, bootstrap, and maintain a stable OpenClaw default agent identity by interviewing the user, updating IDENTITY.md, and seeding core context files (AGENTS.md, SOUL.md, TOOLS.md, USER.md, HEARTBEAT.md, BOOTSTRAP.md). Use when users want to create a new agent baseline, onboard a fresh workspace, or refine long-term personality and behavior.
---

# OpenClaw Default Agent Backstory

Use this skill to define or refine a default OpenClaw agent identity and its supporting context files.

Reference model: OpenClaw context and bootstrap behavior from https://docs.openclaw.ai/concepts/context.

## Core Rules

- Ask five questions every time unless the user explicitly asks to skip, shorten, or focus.
- Use ranked questions from `references/question-bank.md`.
- Prefer unanswered or weakly defined areas first.
- Keep content practical and stable for daily use.
- Preserve user-authored content unless the user asks for replacement.
- If user asks for a default memory policy, apply the `Primary Daily Driver` policy in `references/bootstrap-core-files.md`.

## Mode Selection

Select one mode before writing files:

1. `bootstrap` mode:
- Use when user asks to bootstrap/onboard/start fresh.
- Use when core files are missing or mostly placeholders.
- Create or refresh baseline content for all core context files.

2. `identity-refresh` mode:
- Use when user asks for personality/backstory updates only.
- Update `IDENTITY.md` sections without rewriting unrelated core files.

## Core Context Files

In `bootstrap` mode, ensure these files exist at workspace root with usable starter content:

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`

Use guidance and starter structure in `references/bootstrap-core-files.md`.
Also ensure memory scaffolding exists:

- `MEMORY.md`
- `memory/` directory for daily notes
- `MEMORY.md` must be a standalone workspace-root file, not a section inside `AGENTS.md`.

## Bootstrap Interview Flow

1. Read existing core files if they exist.
2. Ask exactly five bootstrap-priority questions from `references/question-bank.md`.
3. Synthesize answers into practical defaults.
4. Write or refresh all core files listed above.
5. Set rational session-management and memory defaults:
- session startup read order
- when to create/update daily memory notes
- what belongs in `MEMORY.md` vs daily files
- heartbeat cadence and quiet-hour behavior
6. Keep `BOOTSTRAP.md` short, with current setup status and next steps.
7. Summarize what was created, what was updated, and any remaining gaps.

## Identity Refresh Flow

1. Read `IDENTITY.md`.
2. Ask exactly five identity-priority questions from `references/question-bank.md`.
3. Update `IDENTITY.md` with:
- `## Backstory`
- `## Behavioral Guardrails`
- `## Growth Arc`
4. Map each update directly to user answers.
5. Summarize changes and open questions.

## Writing Constraints

- For `IDENTITY.md`, preserve existing header fields unless asked to change them.
- Keep sections concise and concrete.
- Explicitly document boundaries/refusals.
- Do not invent personal history if user input is missing; mark assumptions clearly.

## Completion Criteria

Finish only when:

- five questions were asked (unless user requested otherwise), and
- required target files for the selected mode were updated with concrete, non-placeholder content.
