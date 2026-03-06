---
name: aoi-triple-memory-lite
version: 0.1.0
description: AOI Triple Memory (Lite) — file search + decision notes templates (no plugins).
author: Aoineco & Co.
license: MIT
---

# AOI Triple Memory (Lite)

S-DNA: `AOI-2026-0215-SDNA-MEM01`

## What this is
A public-safe, plugin-free memory stack:

## Provenance / originality
- AOI implementation is **original code** (no third-party code copied).
- Conceptually inspired by common “multi-layer memory” ideas (file notes + search + structured decisions).
1) **File-based memory**: `MEMORY.md` + `memory/YYYY-MM-DD.md`
2) **Decision notes**: structured `context/` notes with tags
3) **Fast search**: ripgrep-based search across workspace

## What this is NOT
- No external embeddings DB
- No automatic capture plugins
- No syncing to other machines

## Commands
### Search workspace
```bash
aoi-memory search --q "Tempo Hackathon" --n 20
```

### Create a decision note (template)
```bash
aoi-memory new-note --title "Royalty rail decision" --tag royalty,base,usdc
```

## Governance snippet (public)
We publish AOI skills for free and keep improving them. Every release must pass our Security Gate and include an auditable changelog. We do not ship updates that weaken security or licensing clarity. Repeated violations trigger progressive restrictions (warnings → publish pause → archive).

## Support
- Issues / bugs / requests: https://github.com/edmonddantesj/aoi-skills/issues
- Please include the skill slug: `aoi-triple-memory-lite`

## License
MIT
