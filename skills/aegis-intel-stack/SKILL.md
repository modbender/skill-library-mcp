---
name: aegis-intel-stack
version: 0.1.0
summary: "Aegis Intel Stack: pre/post execution micro-skills + manifest/delta re-buy triggers"
tags: ["skills", "evm", "gas", "tx", "delta", "manifest"]
---

# Aegis Intel Stack (Utility)

This skill bundle provides a reference implementation + packaging for the MVP offerings:
- `health_ping`
- `gas_snapshot`
- `tx_explain`
- `intel_manifest`
- `intel_delta_update`

## Local run

```bash
cd aegis-suite
npm install
cp apps/utility-seller/.env.example apps/utility-seller/.env
npm run build
node apps/utility-seller/dist/dev_server.js
```

## Call examples

```bash
curl -s localhost:8787/call/health_ping -X POST -H 'content-type: application/json' -d '{"message":"hi"}'
```

```bash
curl -s localhost:8787/call/gas_snapshot -X POST -H 'content-type: application/json' -d '{"chain":"base","urgency":"standard","gas_units":150000}'
```

## Launch automation (docs generation)

```bash
cd aegis-suite
npm run launch:profile
npm run launch:changelog
npm run launch:metrics
```

Outputs:
- `apps/launch-agent/docs/publish_profile.md`
- `apps/launch-agent/docs/CHANGELOG.md`
- `apps/launch-agent/docs/metrics_report.md`
