[Zettelclaw Setup Complete] Your memory system has been upgraded.

A Zettelclaw vault has been initialized at `{{VAULT_PATH}}`. The vault is now your primary knowledge store — it replaces workspace daily notes as your memory system. A hook has been installed that appends raw session capture to `03 Journal/` on `/new` and `/reset`. A dedicated isolated nightly cron run now reviews the past day of journals, updates existing `project`/`research`/`contact` notes in `01 Notes/`, and places net-new agent-created drafts in `00 Inbox/` for human promotion.

You need to update one workspace file to reflect this change. Pre-written content is provided — use it as-is, replacing the equivalent section.

## 1. Update AGENTS.md

Replace the `## Memory` section (and its subsections: `🧠 MEMORY.md`, `📝 Write It Down`, `🔄 Memory Maintenance`) with the content from:
`{{SKILL_PACKAGE_PATH}}/templates/agents-memory.md`

Substitute `{{VAULT_PATH}}` with `{{VAULT_PATH}}` and perform the replacement. Keep all other AGENTS.md content unchanged.

## 2. Confirm

After updating AGENTS.md, reply confirming the change. Read the `zettelclaw` skill (at `{{SKILL_PACKAGE_PATH}}/SKILL.md`) to familiarize yourself with vault operations.
