---
name: gitignore-sync
description: "Context-aware .gitignore generation backed by gitignore.io, not
  vibes. Make it boring again: accurate, idempotent, context-aware."
---


# Gitignore Sync

Generate high-confidence `.gitignore` rules from real repo signals and gitignore.io, then update safely via a managed block so manual rules stay untouched.

## Execution Rule

Use `scripts/update_gitignore.py` as the only execution path.
Do not fetch from the API directly in ad-hoc commands.
Do not manually compose or rewrite `.gitignore` when this skill is selected.

## Workflow

1. Infer requested templates from the user prompt.
2. Detect likely templates from repository files and folders.
3. Run `scripts/update_gitignore.py` with `--prompt-text` and/or `--services`.
4. Let the script fetch combined template rules from `https://www.toptal.com/developers/gitignore/api/<templates>`.
5. Let the script write or update a managed block in `.gitignore`.
6. Preserve non-managed user sections in `.gitignore`.

## Run

From the target repository root, run:

```bash
python3 <skill-path>/scripts/update_gitignore.py \
  --prompt-text "create .gitignore for flutter firebase vscode" \
  --repo .
```

Use explicit templates when the user names exact services:

```bash
python3 <skill-path>/scripts/update_gitignore.py \
  --services flutter,firebase,visualstudiocode \
  --repo .
```

## Notes

- Prefer passing both `--prompt-text` and `--services` when available.
- Keep manual custom rules outside the managed block markers.
- Re-run safely; the script replaces only the managed block.
- Use `--rules-file` for offline/local testing when network access is blocked.
