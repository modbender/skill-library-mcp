---
name: zoho-support
description: "Skill: zoho-support"
---

# zoho-support

Skill: zoho-support

Description: Integrates Zoho Desk with OpenClaw to ingest historical tickets, store local embeddings, analyse open tickets and propose draft replies.

Usage:
- Install via clawhub/publish or copy to workspace skills.
- Configure .env with ZOHO_TOKEN and OPENAI_API_KEY

Commands:
- ingest: Run historical ingest (npm run ingest)
- analyse: Analyse open tickets and generate drafts (npm run analyse)

Notes:
- CommonJS project. No TypeScript.
- Keep credentials in .env (don't commit).
