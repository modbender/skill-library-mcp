---
name: iammeter
description: "Query and export device/site data via the iammeter API (based on https://www.iammeter.com/swaggerui/swagger.json). Triggers: list sites/devices, get real-time or historical energy data, export CSV, run power or offline analysis."
metadata: {"openclaw": {"primaryEnv": "IAMMETER_TOKEN", "requires": {"env": ["IAMMETER_TOKEN"]}}}
---

# iammeter Skill (Node.js)

A Node.js client and CLI for the iammeter API, based on the official swagger spec.

Features
- Token is loaded automatically: first from the `IAMMETER_TOKEN` environment variable,
  then from `~/.openclaw/openclaw.json` (`skills.entries.iammeter.apiKey`)
- List user sites (sitelist)
- Get latest data for all meters (metersdata)
- Get latest upload data for a single meter (meterdata / meterdata2)
- Query site energy history (energyhistory) and export CSV
- Power analysis (poweranalysis), offline analysis (offlineanalysis)

Configuration
- Option A (OpenClaw / Clawhub): set the token in the Skills UI. It is stored in
  `~/.openclaw/openclaw.json` under `skills.entries.iammeter.apiKey` and injected
  as the `IAMMETER_TOKEN` environment variable at runtime.
- Option B (local testing): export IAMMETER_TOKEN=<your_token> before running.

Files
- references/api.md — endpoint reference summarized from swagger
- scripts/iammeter_client.js — Node.js client wrapping common endpoints
- scripts/cli.js — CLI: sitelist|meters|meter|history|poweranalysis|offlineanalysis
- package.json — dependencies (axios, yargs)

Usage (local testing)
1) Install dependencies:
   cd ~/.openclaw/workspace/skills/iammeter
   npm install

2) Run:
   node scripts/cli.js sitelist
   node scripts/cli.js meters
   node scripts/cli.js meter <device_sn>
   node scripts/cli.js history <placeId> 2026-02-01 2026-02-25 --out out.csv

Notes
- Some endpoints have strict rate limits (see references/api.md for details).
- Do not commit real tokens to public repositories.

# Credits
- API endpoints and fields from https://www.iammeter.com/swaggerui/swagger.json

# About IAMMETER
IAMMETER is an energy monitoring solution provider offering Wi-Fi-based single-phase and three-phase smart meters with multiple open interfaces, including Modbus/TCP, MQTT, HTTP/HTTPS API, TCP, and Local Push protocols.
These open communication options make IAMMETER devices easy to integrate with OpenHAB and other open-source platforms.

Learn more about supported protocols and APIs:
Device communication protocols: https://www.iammeter.com/newsshow/blog-fw-features

IAMMETER Cloud API: https://www.iammeter.com/docs/system-api
![advanced-user-ecosystem](https://iammeterglobal.oss-accelerate.aliyuncs.com/img/advanced-user-ecosystem.png)

