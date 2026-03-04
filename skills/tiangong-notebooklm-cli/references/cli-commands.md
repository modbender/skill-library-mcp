# NotebookLM CLI command catalog

Command prefix:

```bash
node {baseDir}/scripts/notebooklm.mjs
```

Notes:
- Use `--json` for machine-readable output.
- Use `--exec-timeout <seconds>` when a command might hang; `--timeout` is for wait/poll durations.
- If the CLI is not authenticated, run `login` or `status` and follow its instructions.

## Session and auth

```bash
node {baseDir}/scripts/notebooklm.mjs status
node {baseDir}/scripts/notebooklm.mjs login
node {baseDir}/scripts/notebooklm.mjs clear
node {baseDir}/scripts/notebooklm.mjs auth check --test --json
```

## Notebooks

```bash
node {baseDir}/scripts/notebooklm.mjs list
node {baseDir}/scripts/notebooklm.mjs create "Research Notebook"
node {baseDir}/scripts/notebooklm.mjs use <notebook_id>
node {baseDir}/scripts/notebooklm.mjs rename "New Title" --notebook <notebook_id>
node {baseDir}/scripts/notebooklm.mjs delete --notebook <notebook_id> --yes
node {baseDir}/scripts/notebooklm.mjs summary --notebook <notebook_id> --topics
```

## Chat

```bash
node {baseDir}/scripts/notebooklm.mjs ask "What are the top risks?" --notebook <notebook_id>
node {baseDir}/scripts/notebooklm.mjs configure --mode concise --notebook <notebook_id>
node {baseDir}/scripts/notebooklm.mjs history --notebook <notebook_id> --limit 20
```

## Sources

```bash
node {baseDir}/scripts/notebooklm.mjs source add https://example.com --notebook <notebook_id>
node {baseDir}/scripts/notebooklm.mjs source add "Inline notes" --title "Meeting" --notebook <notebook_id>
node {baseDir}/scripts/notebooklm.mjs source add-drive <file_id> "Drive Doc" --notebook <notebook_id>
node {baseDir}/scripts/notebooklm.mjs source add-research "market analysis" --mode deep --import-all
node {baseDir}/scripts/notebooklm.mjs source get <source_id>
node {baseDir}/scripts/notebooklm.mjs source guide <source_id> --json
node {baseDir}/scripts/notebooklm.mjs source fulltext <source_id> -o ./source.txt
node {baseDir}/scripts/notebooklm.mjs source rename <source_id> "New Title"
node {baseDir}/scripts/notebooklm.mjs source delete <source_id> --yes
node {baseDir}/scripts/notebooklm.mjs source refresh <source_id>
node {baseDir}/scripts/notebooklm.mjs source stale <source_id>
node {baseDir}/scripts/notebooklm.mjs source wait <source_id> --timeout 300 --exec-timeout 600
```

## Artifacts

```bash
node {baseDir}/scripts/notebooklm.mjs generate slide-deck "Create a 10-slide executive summary" --notebook <notebook_id> --wait
node {baseDir}/scripts/notebooklm.mjs artifact list --notebook <notebook_id> --json
node {baseDir}/scripts/notebooklm.mjs artifact get <artifact_id>
node {baseDir}/scripts/notebooklm.mjs artifact rename <artifact_id> "New Title"
node {baseDir}/scripts/notebooklm.mjs artifact delete <artifact_id> --yes
node {baseDir}/scripts/notebooklm.mjs artifact export <artifact_id> --title "Exec Summary" --type docs
node {baseDir}/scripts/notebooklm.mjs artifact suggestions --json
node {baseDir}/scripts/notebooklm.mjs download slide-deck ./slides.pdf --notebook <notebook_id> --latest
node {baseDir}/scripts/notebooklm.mjs artifact wait <artifact_id> --timeout 600 --exec-timeout 900
```

## Notes

```bash
node {baseDir}/scripts/notebooklm.mjs note create "Key points" --title "Highlights"
node {baseDir}/scripts/notebooklm.mjs note list --notebook <notebook_id>
node {baseDir}/scripts/notebooklm.mjs note get <note_id>
node {baseDir}/scripts/notebooklm.mjs note save <note_id> --content "Updated notes"
node {baseDir}/scripts/notebooklm.mjs note rename <note_id> "New Title"
node {baseDir}/scripts/notebooklm.mjs note delete <note_id> --yes
```

## Sharing

```bash
node {baseDir}/scripts/notebooklm.mjs share add user@example.com --permission editor
node {baseDir}/scripts/notebooklm.mjs share update user@example.com --permission viewer
node {baseDir}/scripts/notebooklm.mjs share remove user@example.com --yes
node {baseDir}/scripts/notebooklm.mjs share public --enable
node {baseDir}/scripts/notebooklm.mjs share view-level full
node {baseDir}/scripts/notebooklm.mjs share status --json
```

## Research

```bash
node {baseDir}/scripts/notebooklm.mjs research status --notebook <notebook_id>
node {baseDir}/scripts/notebooklm.mjs research wait --timeout 600 --interval 5 --exec-timeout 900
```

## Language and skill

```bash
node {baseDir}/scripts/notebooklm.mjs language list --json
node {baseDir}/scripts/notebooklm.mjs language get --json
node {baseDir}/scripts/notebooklm.mjs language set zh_Hans
node {baseDir}/scripts/notebooklm.mjs skill status
node {baseDir}/scripts/notebooklm.mjs skill install
```
