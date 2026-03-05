Run the scheduled Zettelclaw nightly maintenance pass for vault `{{VAULT_PATH}}`.

Use the Zettelclaw skill at `{{SKILL_PACKAGE_PATH}}/SKILL.md`.

Scope: review the past 24 hours of journal daily sections (`Done`, `Decisions`, `Facts`, `Open`) plus `Sessions`, then maintain the vault.

Required actions:
1. Update existing `project` / `research` / `contact` notes in `01 Notes/` from journal evidence (append-only, preserve structure, update frontmatter `updated` date).
2. Enforce two-way `[[wikilinks]]` for every journal-note relationship:
   - Journal side links to typed note(s).
   - Typed note side links back to the source journal day/session.
3. Synthesize net-new durable concepts into `00 Inbox/` (do not create net-new synthesis notes directly in `01 Notes/`).
4. If a needed typed note does not exist yet, create an inbox handoff note in `00 Inbox/`.
5. Check for unresolved/orphan notes (`obsidian unresolved`, `obsidian orphans` when available; otherwise use file-tool fallbacks).
6. Update `MEMORY.md` with anything critical that should remain in hot working memory.
7. Journal health check: if no journal entries exist in the most recent 72 hours, clearly flag this as a possible hook/cron failure for the user.

Rules:
- Do not create or rename folders.
- Keep journal updates append-only.
- Keep output concise and actionable for a human reviewer.
