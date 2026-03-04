---
name: opdscli
description: Browse, search, and download ebooks from OPDS catalogs using the opdscli CLI. Use when adding/managing catalogs, searching for books, downloading ebooks, or browsing latest additions.
homepage: https://github.com/rafadc/opdscli
metadata: {"clawdbot":{"emoji":"📚","requires":{"bins":["opdscli"]},"install":[{"id":"brew","kind":"brew","tap":"rafadc/opdscli","formula":"opdscli","bins":["opdscli"],"label":"Install opdscli (brew)"}]}}
---

# opdscli

OPDS catalog browser and ebook downloader. Follow the CLI reference below.

## References

- `references/cli-reference.md` (commands, flags, and examples)

## Workflow

1. Verify CLI present: `opdscli --version`.
2. Check configured catalogs: `opdscli catalog list`.
3. If no catalogs configured, add one (see cli-reference for auth options).
4. Set a default catalog if needed: `opdscli catalog set-default <name>`.
5. Search, browse, or download as requested.

## Common patterns

### Add a public catalog

```bash
opdscli catalog add gutenberg https://m.gutenberg.org/ebooks.opds/
```

### Add a catalog with authentication

```bash
# Basic auth (will prompt for credentials)
opdscli catalog add mylib https://my-library.example.com/opds --auth-type basic

# Bearer token
opdscli catalog add mylib https://my-library.example.com/opds --auth-type bearer
```

### Search and download

```bash
opdscli search "don quixote"
opdscli download "Don Quixote"
opdscli download "Don Quixote" --format pdf --output ~/Books
```

### Browse latest additions

```bash
opdscli latest
opdscli latest --limit 50
```

## Guardrails

- Config lives at `~/.config/opdscli.yaml`. Do not edit it directly; use `opdscli catalog` subcommands.
- Credentials stored in config are plaintext. Never log or echo catalog config that may contain passwords or tokens.
- When downloading, respect the user's preferred format and output directory.
- If a search returns no results, suggest increasing `--depth` or checking the catalog URL.
- Use `--verbose` for debugging connection issues, `--quiet` when piping output.
