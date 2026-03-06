# .somaco -> Factory Droid Unification Map

How the existing `.somaco` directive system maps to Factory skills and droids.

## Current .somaco Commands -> Factory Skills

| .somaco Command | SOM ID | Factory Skill | Status |
|----------------|--------|---------------|--------|
| `/preflight-check` | SOM-CMD-0004 | **ghost-catalog** (scan + validate) | REPLACED - Ghost Catalog's scan/validate covers header compliance; agent registration handled by skill auto-invocation |
| `/stats` | SOM-CMD-0006 | **ghost-catalog** (stats command) | REPLACED - catalog stats + git status + project structure in one skill |
| `/project-status` | SOM-CMD-0001 | **ghost-catalog** (stats + report) | REPLACED - catalog DB provides richer project health than file-by-file inspection |
| `/db-inspect` | SOM-CMD-0003 | Keep as standalone skill | MIGRATE - useful for any SQLite DB, not just catalog |
| `/new-project` | SOM-CMD-0002 | Keep as standalone skill | MIGRATE - scaffolding with auto-catalog registration |
| `/think` | SOM-CMD-0005 | N/A | DROP - Factory Droid has its own thinking mode |

## Current .somaco Rule Modules -> Factory Configuration

| Module | SOM ID | Factory Equivalent | Action |
|--------|--------|-------------------|--------|
| `file-headers.md` | SOM-DOC-0010 | **ghost-catalog** skill | ABSORBED - the skill IS the header system |
| `coding-standards.md` | SOM-DOC-0011 | `CLAUDE.md` / `AGENTS.md` | KEEP - belongs in project-level agent instructions |
| `agent-context.md` | SOM-DOC-0012 | Factory Droid memory system | SUPERSEDED - Factory handles session continuity via summaries |
| `failure-prevention.md` | SOM-DOC-0013 | Custom droid config | MIGRATE - encode as droid behavioral constraints |

## Current .somaco Stack Rules -> Factory Droids

| Stack | Projects | Factory Approach |
|-------|----------|-----------------|
| `nextjs.md` | aqua_attack, astro_chart, austinsays | Project-level `CLAUDE.md` already handles this |
| `flask.md` | gyst_02s | Project-level `CLAUDE.md` |
| `godot.md` | hxodot | Project-level `CLAUDE.md` |
| `python-cli.md` | Oligarchology, dossier | Project-level `CLAUDE.md` |

## Recommended Factory Skill Portfolio

### Tier 1: Built (This Session)
- **ghost-catalog** — Scan, tag, validate, search, stats, report

### Tier 2: Migrate from .somaco
- **db-inspect** — SQLite inspection (port from SOM-CMD-0003)
- **new-project** — Scaffold new project with catalog registration (port from SOM-CMD-0002)

### Tier 3: New Skills from Protocol
- **gyst-uuid** — Generate/parse/validate GYST UUID v8 identifiers
- **data-weave** — Scan workspace, map projects, discover cross-domain relationships
- **molting** — 5-stage structured analysis workflow
