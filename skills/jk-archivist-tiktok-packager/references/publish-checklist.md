# Publish Checklist

## Before packaging

- Run: `npm test`
- Run: `npm run validate:bundle`
- Confirm `SKILL.md` frontmatter is present and valid.
- Confirm no secrets in files.

## Build upload zip

`npm run pack`

Output:

- `dist/jk-archivist-tiktok-skill.zip`

## One-command release prep

```bash
npm run release -- --version 1.2.0
```

This updates local version fields, runs tests, validates bundle, and generates zip output.

## ClawHub validation pitfalls

- Remove runtime artifacts (`*.pyc`, `__pycache__`, `outbox/` files)
- Keep only text/source files in upload bundle
- Rebuild zip from tracked files after each validation error
