---
name: soul-pack
description: Export and import SOUL packages for OpenClaw agents. Use when creating a reusable persona package (SOUL.md + preview.md + manifest.json), installing a soul package into a new/existing agent workspace, or batch listing local soul packages for a Soul marketplace workflow.
---

# Soul Pack

Use bundled scripts for deterministic behavior.

## Export soul package

```bash
bash /Users/feifei/projects/soul-pack-skill/scripts/export-soul.sh \
  --workspace /Users/feifei/.openclaw/workspace \
  --out /Users/feifei/projects/soul-packages \
  --name edith-soul
```

## Import soul package + create agent

```bash
bash /Users/feifei/projects/soul-pack-skill/scripts/import-soul.sh \
  --package /Users/feifei/projects/soul-packages/edith-soul.tar.gz \
  --agent my-soul \
  --workspace /Users/feifei/projects/agents/my-soul
```

## List local soul packages

```bash
bash /Users/feifei/projects/soul-pack-skill/scripts/list-souls.sh \
  --dir /Users/feifei/projects/soul-packages
```

## Notes
- `manifest.json` is validated against `schema/manifest.schema.v0.1.json`.
- Import does not overwrite existing SOUL.md unless `--force` is provided.
- Agent registration uses `openclaw agents add` (or reuses existing agent id).