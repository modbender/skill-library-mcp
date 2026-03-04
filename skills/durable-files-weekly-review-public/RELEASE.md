# Release Notes

## Package
- Slug: `durable-files-weekly-review-public`
- Version: `1.0.0`
- Scope: public/generic weekly durable-file token-optimization audit skill

## Included files
- `SKILL.md`
- `scripts/durable_files_review_generic.py`
- `references/publish-safety.md`

## Smoke checks completed
- Python syntax check (`py_compile`) passed
- Script execution smoke test passed
- Sensitive-string grep check passed (no private paths/secrets)

## Publish command
```bash
clawhub publish skills/durable-files-weekly-review-public \
  --slug durable-files-weekly-review-public \
  --name "Durable Files Weekly Review (Public)" \
  --version 1.0.0 \
  --changelog "Initial public release: generic weekly durable-file audit with approval-gated cleanup workflow." \
  --tags "openclaw,ops,token-optimization,documentation"
```

## Built artifact
- `dist/durable-files-weekly-review-public-1.0.0.tgz`
- `dist/durable-files-weekly-review-public-1.0.0.tgz.sha256`
