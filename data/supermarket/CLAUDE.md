# krocli

Kroger-family grocery CLI + OpenClaw skill. Covers all Kroger-owned banners: Kroger, Ralphs, Fred Meyer, Harris Teeter, King Soopers, Fry's, QFC, Mariano's, Pick 'n Save, etc.

## Build & Run
```bash
make build        # → bin/krocli
make lint         # golangci-lint
```

## Architecture
- `cmd/krocli/main.go` → `internal/cmd.Execute()`
- Kong CLI with subcommands: auth, products, locations, cart, identity
- Two auth modes: client_credentials (search) and authorization_code (cart/identity)
- Tokens stored in OS keyring via 99designs/keyring
- Credentials in `~/.config/krocli/credentials.json`
- Output: `-j` JSON, `-p` plain/TSV, default human-friendly to stderr

## OpenClaw Skill
- Published on ClawHub as `supermarket` (slug: `supermarket`, owner: `niemesrw`)
- Install: `clawhub install supermarket`
- Skill source: `SKILL.md` (frontmatter + API instructions)
- Metadata: `_meta.json`
