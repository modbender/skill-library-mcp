# AOI Squad Orchestrator (Lite)

S-DNA: `AOI-2026-0215-SDNA-SQUAD01`

## What this is
A **public-safe** productized orchestration skill that:
- provides **3 selectable presets** (each 3 roles)
- assigns each role a **stable pseudonym** (no AOI internal nicknames)
- lets users **rename** team members
- emits a **single fixed JSON report schema** for easy parsing & testing

## What this is NOT
- No external posting, no web crawling, no form submit.
- No wallets/trading/purchases.
- No automatic privilege escalation.

## Presets
- `planner-builder-reviewer`
- `researcher-writer-editor`
- `builder-security-operator`

## Commands
### List presets
```bash
aoi-squad preset list
```

### Show current team names (stable per preset)
```bash
aoi-squad team show --preset planner-builder-reviewer
```

### Rename a team member
```bash
aoi-squad team rename --preset planner-builder-reviewer --role reviewer --name "Sentinel Kestrel"
```

### Run (MVP: structured report)
```bash
aoi-squad run --preset planner-builder-reviewer --task "Draft a launch checklist"
```

## Data
- Team name mapping is stored locally:
  - `~/.openclaw/aoi/squad_names.json`

## Support
- Issues / bugs / requests: https://github.com/edmonddantesj/aoi-skills/issues
- Please include the skill slug: `aoi-squad-orchestrator-lite`

## License
MIT
