---
name: magic-quill
description: Generate OpenClaw Spellbook YAML theme mappings from a topic (game/movie/franchise/etc.) or a URL. Use when you need to create or refresh a themed spell mapping file under /spells with broad coverage of popular skills (default top 50). The generator now performs dynamic spell-list reference discovery first (searching for spell lists/APIs and parsing discovered JSON/HTML sources), then uses lore/context as secondary style input and falls back to heuristic spell names when references fail. NOTE: This skill generates YAML mapping files — to use the spells in agent sessions, you need the openclaw-spellbook hook installed (see wynnsu/openclaw-spellbook).
---

# Magic Quill

A magical quill that inscribes themed spell mappings for OpenClaw Spellbook with high coverage for popular skills.

## Inputs

- `--topic <name>` or `--url <https://...>` (primary inputs; spell-list lookup searches by topic/theme first, and `--url` is treated as a high-priority reference candidate when provided)
- Optional `--theme <name>` to override the final theme name (or run heuristic-only mode with just `--theme`)
- Optional `--out <path>` (alias: `--output`) (default: `spells/<theme-slug>.yaml`)
- Optional `--limit <n>` (alias: `--top`) for top-N coverage (default: `50`)
- Optional `--author <name>` (default: `@magic-quill`)

## What To Do

1. Gather popular skills from both sources when possible:
   - `skills.sh` trending installs
   - ClawHub downloads API endpoint
2. Merge and de-duplicate the results into a target set (fill gaps from built-in fallback skills if fetch fails).
3. Gather spell-list references first (primary spell source):
   - Build dynamic web search queries from topic/theme (for example `<topic> spell list` and `<topic> spells api`)
   - Parse top search result links (DuckDuckGo HTML results) into candidate reference URLs
   - Include `--url` as a high-priority candidate when present
   - Fetch discovered JSON/HTML references (for example `dnd5eapi.co` if discovered), extract spell names, and merge/de-duplicate names from successful references
4. Gather lore/context (secondary style keywords only):
   - If `--url` is provided, fetch and extract page text
   - Else if `--topic` is provided, try Wikipedia summary API
   - If fetch fails, use built-in theme lexicon/heuristics
5. If spell-list references fail or do not produce enough names, generate spell mappings with the built-in heuristic spell-name generator.
6. Write YAML to the requested output path (usually under `spells/`), including `# spell-list-references:` comment links for successful dynamically discovered spell-list sources/endpoints when available.
7. Validate with `npm run validate:spells` if the output file is under `spells/`.

## Commands (Users)

```bash
npm run generate:spellbook-theme -- --theme "Studio Ghibli" --limit 50 --author "@you"
npm run generate:spellbook-theme -- --topic "Cyberpunk 2077" --limit 75 --out spells/cyberpunk-2077.yaml --author "@you"
npm run generate:spellbook-theme -- --url "https://en.wikipedia.org/wiki/The_Lord_of_the_Rings" --limit 50 --author "@you"
npm run generate:spellbook-theme -- --topic "DnD 5e" --limit 20 --author "@you"
```

## Commands (Agents)

```bash
node magic-quill/scripts/generate-spell-mapping.mjs --theme "The Legend of Zelda" --topic "The Legend of Zelda" --limit 50 --out spells/zelda.yaml --author "@example"
node scripts/validate-spells.mjs
```

## Install From This Repo (Subpath)

Use a repo subpath source with `npx skills add`, for example:

```bash
npx skills add wynnsu/openclaw-spellbook/magic-quill
```

## ⚠️ Requires Hook for Use

This skill **generates** spell YAML mapping files — to actually use the themed spells in agent sessions, you need the **openclaw-spellbook hook** installed. Install the full spellbook package:

```bash
# Install the spellbook hook (includes magic-quill skill)
npx skills add wynnsu/openclaw-spellbook
```

Or install just the hook directly from the repo:
```bash
npx skills add wynnsu/openclaw-spellbook/hooks/spellbook
```

The hook handles the translation between magical spell names and actual skill IDs at runtime.

Usage after install (example prompt):

```text
Use magic-quill to create a Star Wars spell mapping with top 50 coverage and write it to spells/star-wars.yaml.
```
