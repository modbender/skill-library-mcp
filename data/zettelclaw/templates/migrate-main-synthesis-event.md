# Zettelclaw Migration Final Synthesis

You are the final synthesis agent for a Zettelclaw migration run.
All per-file migration work has already been completed by sub-agents.
Do not delegate.

## Paths
- Vault: `{{VAULT_PATH}}`
- Workspace: `{{WORKSPACE_PATH}}`
- Notes folder: `{{VAULT_PATH}}/{{NOTES_FOLDER}}`
- Journal folder: `{{VAULT_PATH}}/{{JOURNAL_FOLDER}}`
- MEMORY.md: `{{WORKSPACE_PATH}}/MEMORY.md`
- USER.md: `{{WORKSPACE_PATH}}/USER.md`
- IDENTITY.md: `{{WORKSPACE_PATH}}/IDENTITY.md`
- Model: `{{MODEL}}`

## Inputs From Sub-Agents
{{SUBAGENT_SUMMARIES}}

## Required Actions
1. Read current `MEMORY.md`, `USER.md`, and `IDENTITY.md` (when present).
2. Update `MEMORY.md` as hot working memory only:
   - Include current focus, active projects, immediate constraints, and actionable context.
   - Keep concise and high-signal.
3. Update `USER.md` with durable user context only when warranted by migration evidence.
4. Enforce separation of concerns:
   - `MEMORY.md` must NOT duplicate identity/profile details already in `USER.md` or `IDENTITY.md`.
   - If needed, MEMORY may reference USER/IDENTITY briefly instead of repeating content.
5. Preserve existing useful content where possible (append or refine rather than destructive rewrite unless clearly needed).

## Output
After completing file edits, reply with a short bullet list:
- `MEMORY.md:` what changed
- `USER.md:` what changed
- `Separation:` confirmation that MEMORY no longer overlaps USER/IDENTITY
