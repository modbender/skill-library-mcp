# 🐝 CRM-in-a-Box

> An open protocol for customer relationship management. Fork it. Make it yours.

**CRM-in-a-box** is an append-only, hash-chained CRM protocol built on the same principles as [biz-in-a-box](https://biz-in-a-box.org). One repo = one CRM. No vendor lock-in. No SaaS fees. Your data, your rules.

## Why

Every CRM today is a walled garden. Your contacts, your pipeline, your conversations — trapped inside Salesforce, HubSpot, or a dozen other platforms that charge per seat and hold your data hostage.

CRM-in-a-box is different:
- **Open protocol** — JSON files in a git repo
- **Hash-chained** — every entry is cryptographically linked
- **Forkable** — `crm-in-a-box` → `pm-crm`, `saas-crm`, `realestate-crm`
- **Agent-native** — built for AI agents to read, write, and act on
- **Free forever** — self-host for $0, or pay us $1/seat/mo to host it

## Core Concepts

### Contacts
People and companies, stored as structured JSON with full interaction history.

### Pipeline
Customizable stages. Every stage transition is a journal entry — auditable, reversible, timestamped.

### Interactions
Every email, call, meeting, and note is an append-only entry. Nothing gets deleted. Everything is searchable.

### Labels
Flexible tagging system. Tag contacts, deals, interactions — whatever your workflow needs.

## Quick Start

```bash
git clone https://github.com/taylorhou/crm-in-a-box
cd crm-in-a-box
# Your CRM is ready. Start adding contacts.
```

## Protocol

Built on the [biz-in-a-box](https://biz-in-a-box.org) append-only journal protocol:
- `contacts.ndjson` — contact records
- `pipeline.ndjson` — deal/opportunity tracking
- `interactions.ndjson` — all touchpoints
- `config.yaml` — pipeline stages, labels, settings

## Forks

CRM-in-a-box is designed to be forked for specific verticals:
- **pm-crm** — Property management (tenants, owners, vendors)
- **saas-crm** — SaaS sales pipeline
- **realestate-crm** — Buyers, sellers, agents, listings
- **recruiting-crm** — Candidates, jobs, placements

## License

[BSL 1.1](LICENSE) — Free for personal/internal use. Commercial redistribution requires a license. Converts to Apache 2.0 after 4 years.

---

*Part of the [in-a-box](https://biz-in-a-box.org) family of open protocols.*
