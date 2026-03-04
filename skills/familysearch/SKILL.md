---
name: familysearch
description: Search, explore, and analyze family history using the FamilySearch API and offline GEDCOM files. Use when the user asks about genealogy, ancestors, family trees, family history research, pedigree charts, or wants to look up relatives. Supports live FamilySearch API queries (person search, ancestry/descendancy, relationships, historical records) and offline GEDCOM file parsing (search, profiles, narrative biographies, statistics). Trigger on: "search my family tree", "who are my ancestors", "tell me about [ancestor name]", "family tree", "GEDCOM", "genealogy", "FamilySearch".
os: [macos, linux]
credentials:
  - name: FamilySearch OAuth Token
    description: OAuth 2.0 access token for FamilySearch API (required for API mode only; GEDCOM mode works offline)
    required: false
bins:
  - python3
---

# FamilySearch Genealogy Skill

Two modes of operation:
1. **Live API** (primary) — Query FamilySearch directly for person search, pedigree, descendants, historical records
2. **Offline GEDCOM** — Parse exported `.ged` files for local exploration, narratives, and statistics

## Mode 1: FamilySearch API (Primary)

### Prerequisites

1. **FamilySearch Account** — Free at <https://www.familysearch.org>
2. **Developer App Key** — Register at <https://www.familysearch.org/developers/>
3. **OAuth 2.0 Access Token** — Via authentication flow below

Store credentials:

**Option A — Environment variable (all platforms):**
```bash
export FAMILYSEARCH_TOKEN="<TOKEN>"
```

**Option B — macOS Keychain:**
```bash
security add-generic-password -a "familysearch-app-key" -s "openclaw-familysearch" -w "<APP_KEY>"
security add-generic-password -a "familysearch-token" -s "openclaw-familysearch-token" -w "<TOKEN>"
```

The script checks `FAMILYSEARCH_TOKEN` env var first, then falls back to macOS Keychain.

### Authentication

OAuth 2.0 Authorization Code flow:
1. Direct user to: `https://ident.familysearch.org/cis-web/oauth2/v3/authorization?response_type=code&client_id={APP_KEY}&redirect_uri={REDIRECT_URI}`
2. User logs in, grants access
3. Exchange code for token:
```bash
curl -X POST "https://ident.familysearch.org/cis-web/oauth2/v3/token" \
  -d "grant_type=authorization_code&code={AUTH_CODE}&client_id={APP_KEY}"
```
4. Store returned `access_token` in Keychain

**Sandbox** for testing: `https://integration.familysearch.org` / `https://api-integ.familysearch.org`

### API Usage

```bash
python scripts/familysearch.py <command> [args]
```

| Command | Description |
|---------|-------------|
| `search --given John --surname Lewis --birth-place Oregon` | Search persons in Family Tree |
| `person <PID>` | Get person details |
| `ancestry <PID> --generations 4` | Ascending pedigree (1-8 generations) |
| `descendants <PID> --generations 2` | Descending tree |
| `parents <PID>` | Get parents |
| `spouses <PID>` | Get spouses |
| `children <PID>` | Get children |

Search parameters: `--given`, `--surname`, `--birth-date`, `--birth-place`, `--death-date`, `--death-place`, `--sex`

Results use GEDCOM X format (JSON). Key fields: `persons[].id`, `persons[].display.name`, `.birthDate`, `.birthPlace`, `.deathDate`, `.deathPlace`.

**Ahnentafel numbering** in ancestry: 1=subject, 2=father, 3=mother, 4=paternal grandfather, etc.

## Mode 2: Offline GEDCOM Files

For exported `.ged` files from FamilySearch, Ancestry, MyHeritage, etc. No API key needed — pure offline.

### Getting a GEDCOM File

FamilySearch: **familysearch.org → Family Tree → Tools → Export GEDCOM**

### Usage

```bash
python scripts/gedcom_query.py <gedcom_file> <command> [args...]
```

| Command | Description |
|---------|-------------|
| `search <name>` | Fuzzy name search — returns matches with IDs |
| `person <id_or_name>` | Full profile: birth, death, parents, spouses, children |
| `ancestors <id_or_name> [depth]` | Pedigree chart up (default: 4 generations) |
| `descendants <id_or_name> [depth]` | Pedigree chart down (default: 3 generations) |
| `story <id_or_name>` | Narrative biography paragraph |
| `timeline <id_or_name>` | Chronological life events |
| `stats` | Tree summary: counts, surnames, birth decades, completeness |
| `find-date <year>` | Find people born/died in a given year |
| `common-ancestor <name1> <name2>` | Find closest common ancestor |

`id_or_name`: GEDCOM ID (e.g., `I001`) or partial name (fuzzy, case-insensitive).

## Narrative Genealogy

Beyond data retrieval, this skill supports **narrative genealogy** — connecting facts to stories:

- Note occupations, migrations, life events when exploring a tree
- Cross-reference API/GEDCOM data with stories the user shares conversationally
- Build family narratives that explain *why* — not just dates and names
- Flag research opportunities: missing records, undocumented branches, conflicting dates
- Use `story` command (GEDCOM mode) for auto-generated biographical narratives

## Agent Workflow

1. **User asks about family history** → Check if they have a FamilySearch account (API) or GEDCOM file (offline)
2. **API mode**: Search by name → get person ID → explore ancestry/descendants/relationships
3. **GEDCOM mode**: Load file → search → explore
4. **Either mode**: Combine structured data with user's oral history for richer narratives
5. **Cross-reference**: Use API to find records that fill gaps in GEDCOM data

## Rate Limits & Best Practices

- FamilySearch API is free but rate-limited — cache results locally
- Never store FamilySearch usernames/passwords — OAuth tokens only
- Tokens expire; re-authenticate on 401 responses
- GEDCOM parser handles files up to ~100K individuals
- File encoding: auto-detects UTF-8 (with BOM), UTF-8, latin-1
