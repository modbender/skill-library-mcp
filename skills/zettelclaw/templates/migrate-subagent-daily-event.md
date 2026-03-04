# Zettelclaw Migration Sub-Agent (Daily File)

You are migrating exactly one daily memory file into a Zettelclaw vault.
Do not delegate. Do not process any file except the one listed here.

## Paths
- Vault: `{{VAULT_PATH}}`
- Workspace: `{{WORKSPACE_PATH}}`
- Source file: `{{SOURCE_PATH}}` (relative: `{{SOURCE_RELATIVE_PATH}}`)
- Journal target: `{{VAULT_PATH}}/{{JOURNAL_FOLDER}}/{{FILE_BASENAME}}`
- Typed notes folder: `{{VAULT_PATH}}/{{NOTES_FOLDER}}`

## Existing wikilink index
{{WIKILINK_INDEX}}

## Required Actions
1. Read `{{SOURCE_PATH}}`.
2. Create or update `{{VAULT_PATH}}/{{JOURNAL_FOLDER}}/{{FILE_BASENAME}}` using date `{{DAY}}`.
   - Ensure frontmatter includes: `type: journal`, pluralized `tags`, `created`, `updated`.
   - Keep the day-level sections: `## Done`, `## Decisions`, `## Facts`, `## Open`.
   - Keep sessions footer as:
     - `---`
     - `## Sessions`
   - Do not insert a blank line between frontmatter and first content line.
3. From this file's content, update typed notes in `{{VAULT_PATH}}/{{NOTES_FOLDER}}`:
   - Prefer updating existing `project` / `research` / `contact` notes (append-only, preserve structure, update `updated`).
   - Create new typed notes only when no suitable existing note exists.
   - New project note titles MUST end with `Project`.
   - New research note titles MUST end with `Research`.
4. Enforce two-way wikilinks for every journal <-> typed note relationship:
   - Journal side links to typed note(s).
   - Typed note side links back to journal day `[[{{DAY}}]]` when relevant.
5. Delete the source file `{{SOURCE_PATH}}`.

## Output Format
Return ONLY valid JSON (no prose, no markdown fences):

{
  "sourceFile": "{{SOURCE_RELATIVE_PATH}}",
  "status": "ok",
  "summary": "One concise paragraph of what you created/updated.",
  "createdWikilinks": ["[[Link One]]", "[[Link Two]]"],
  "createdNotes": ["Note Name.md"],
  "updatedNotes": ["Existing Note.md"],
  "journalDaysTouched": ["{{DAY}}"],
  "deletedSource": true
}

If you cannot complete the task, still return JSON with:
- `"status": "error"`
- `"summary"` containing the failure reason
- `"deletedSource": false` when deletion did not happen
