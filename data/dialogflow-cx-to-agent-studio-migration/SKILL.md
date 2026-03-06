---
name: dialogflow-cx-to-studio-migration
description: Migrate Dialogflow CX agents to CX Agent Studio (CES) using official REST/RPC APIs. Exports full CX agent packages, validates components (intents, entities, flows, pages, etc.), and creates CES apps/agents (remote Dialogflow agent) with a migration report.
---

# Dialogflow CX → CX Agent Studio Migration

Use this skill when you need to migrate a Dialogflow CX agent into CX Agent Studio (Gemini Enterprise for Customer Engagement / CES). It exports the full CX agent package, enumerates all components (intents, entities, flows, pages, webhooks, route groups, etc.), and creates a CES app + agent that runs the CX agent as a **remote Dialogflow agent**.

## What this does

1. **Exports** the DFCX agent as a JSON package via the v3beta1 REST API.
2. **Parses & indexes** all exported components (agents, intents, entity types, flows, pages, webhooks, transition route groups, test cases, playbooks, etc.).
3. **Creates** a CES app and a CES agent (remote Dialogflow agent) via CES v1beta REST API.
4. **Sets root agent** on the CES app and emits a **migration report** with component counts and resource names.

## Scripts

- `scripts/migrate.py` — end‑to‑end migration + report generation

### Usage

```bash
python skills/dialogflow-cx-to-studio-migration/scripts/migrate.py \
  --dfcx-agent projects/PROJECT/locations/LOCATION/agents/AGENT_ID \
  --studio-project PROJECT \
  --studio-location LOCATION \
  --studio-app-display-name "My CX Studio App" \
  --studio-agent-display-name "My CX Agent (Remote DFCX)"
```

Export only (no CES changes):
```bash
python skills/dialogflow-cx-to-studio-migration/scripts/migrate.py \
  --dfcx-agent projects/PROJECT/locations/LOCATION/agents/AGENT_ID \
  --export-only
```

Use existing CES app:
```bash
python skills/dialogflow-cx-to-studio-migration/scripts/migrate.py \
  --dfcx-agent projects/PROJECT/locations/LOCATION/agents/AGENT_ID \
  --studio-app projects/PROJECT/locations/LOCATION/apps/APP_ID
```

### Outputs

- `dfcx_migration_output/dfcx_agent_export.zip` — DFCX JSON package
- `dfcx_migration_output/export/` — extracted export folder
- `dfcx_migration_output/migration_report.json` — migration report with component counts

## Authentication

Use ADC (recommended):
```bash
gcloud auth application-default login
```

Ensure the caller has:
- Dialogflow CX permissions (export/list)
- CES permissions (create app/agent)

Scopes used:
- `https://www.googleapis.com/auth/cloud-platform`
- `https://www.googleapis.com/auth/dialogflow`
- `https://www.googleapis.com/auth/ces`

## Notes & Limitations

- The CES agent is created as **RemoteDialogflowAgent** (official CES support). This preserves **all DFCX components** without lossy conversion.
- The script **indexes** all components from the JSON package and writes a report for auditing.
- If you need direct LLM-native agents/tools in CES, plan a follow‑up conversion step.

## References (load as needed)

- API links and endpoints: [references/api-links.md](references/api-links.md)
- Migration mapping & component coverage: [references/mapping.md](references/mapping.md)
