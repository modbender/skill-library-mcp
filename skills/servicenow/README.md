# 🔧 ServiceNow Skill for OpenClaw

**By [OnlyFlows](https://onlyflows.tech)**

> Connect your AI agent to ServiceNow — full CRUD, analytics, schema introspection, and attachment management across every table in your instance.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-onlyflows%2Fservicenow-orange)](https://clawhub.dev/onlyflows/servicenow)

---

## What It Does

The ServiceNow skill gives your OpenClaw agent native access to **any ServiceNow instance** via the REST Table API and Stats API. Ask questions in natural language and your agent translates them into precise API calls — no scripting required.

Whether you're triaging incidents at 2 AM, auditing CMDB accuracy, or building change request dashboards, this skill turns your AI into a ServiceNow power user.

---

## ⚡ Features

| Tool | Description |
|------|-------------|
| **sn_query** | Query any table with encoded queries, field selection, pagination, and sorting |
| **sn_get** | Retrieve a single record by sys_id with display value support |
| **sn_create** | Create records on any table with JSON field payloads |
| **sn_update** | Update records via PATCH with partial field updates |
| **sn_delete** | Delete records with mandatory `--confirm` safety flag |
| **sn_aggregate** | Run COUNT, AVG, MIN, MAX, SUM with group-by support |
| **sn_schema** | Introspect table schemas — field types, lengths, references, mandatory flags |
| **sn_attach** | List, upload, and download file attachments on any record |
| **sn_batch** | Bulk update or delete records with dry-run safety, query filters, and progress tracking |
| **sn_health** | Instance health dashboard — version, cluster nodes, stuck jobs, semaphores, and quick stats |

---

## 📦 Installation

```bash
clawhub install onlyflows/servicenow
```

Or clone manually into your skills directory:

```bash
git clone https://github.com/onlyflowstech/servicenow-openclaw-skill.git \
  ~/.openclaw/skills/servicenow
```

### Prerequisites

- **curl** and **jq** must be available on your system
- A ServiceNow instance with REST API access enabled
- A ServiceNow user account with appropriate table permissions

---

## 🔑 Configuration

Set three environment variables — **no credentials are stored in the skill files**:

```bash
export SN_INSTANCE="https://yourinstance.service-now.com"
export SN_USER="your_api_username"
export SN_PASSWORD="your_api_password"
```

| Variable | Description | Example |
|----------|-------------|---------|
| `SN_INSTANCE` | Your ServiceNow instance URL | `https://dev12345.service-now.com` |
| `SN_USER` | API user with table read/write access | `api_user` |
| `SN_PASSWORD` | Password for the API user | *(set securely)* |

> 💡 **Tip:** Use a dedicated integration user with least-privilege ACLs rather than an admin account.

---

## 🚀 Usage Examples

Once configured, just ask your agent in natural language:

### Incident Management
> **"How many open P1 incidents do we have?"**
> → Runs an aggregate COUNT on `incident` where `active=true^priority=1`

> **"Create an incident for the VPN outage affecting the Chicago office"**
> → Creates a record on `incident` with the description and impact details

> **"Who submitted the most incidents this month?"**
> → Queries `incident` with date filters and groups by caller

### Change Management
> **"Show me all changes scheduled for this week"**
> → Queries `change_request` with date range filters on `start_date`

### CMDB & Schema Discovery
> **"What's the schema of the cmdb_ci_server table?"**
> → Returns all fields, types, references, and mandatory flags

> **"List all Linux servers in the production environment"**
> → Queries `cmdb_ci_server` with OS and environment filters

### Knowledge Management
> **"Find knowledge articles about password resets"**
> → Searches `kb_knowledge` with description LIKE filters

### Bulk Operations
> **"Close all resolved incidents older than 90 days"**
> → Runs `sn_batch` on `incident` with state/date filters and update action

> **"How many abandoned test records do we have?"**
> → Dry-run batch delete to count matching records without changes

### Instance Health
> **"Is the instance healthy?"**
> → Runs `sn_health` with all checks — version, nodes, stuck jobs, semaphores, and stats

> **"Any stuck scheduled jobs?"**
> → Runs `sn_health --check jobs` to find overdue sys_trigger records

---

## 📋 Supported Tables

The skill works with **any** ServiceNow table, but here are the most common:

| Table | Description |
|-------|-------------|
| `incident` | Incident records |
| `change_request` | Change requests |
| `problem` | Problem records |
| `sc_req_item` | Requested Items (RITMs) |
| `sc_request` | Service requests |
| `sys_user` | User records |
| `sys_user_group` | Group records |
| `cmdb_ci` | Configuration Items (base) |
| `cmdb_ci_server` | Server CIs |
| `cmdb_ci_app_server` | Application Server CIs |
| `kb_knowledge` | Knowledge articles |
| `task` | Parent task table |
| `sys_choice` | Choice list values |
| `sla_condition` | SLA definitions |
| `change_task` | Change tasks |
| `incident_task` | Incident tasks |

---

## 🔍 Encoded Query Cheat Sheet

ServiceNow uses encoded query syntax for filtering. Here's a quick reference:

| Operator | Syntax | Example |
|----------|--------|---------|
| Equals | `field=value` | `priority=1` |
| Not equals | `field!=value` | `state!=7` |
| Contains | `fieldLIKEvalue` | `short_descriptionLIKEserver` |
| Starts with | `fieldSTARTSWITHvalue` | `numberSTARTSWITHINC` |
| Greater than | `field>value` | `sys_created_on>2026-01-01` |
| Greater or equal | `field>=value` | `priority>=2` |
| Less than | `field<value` | `reassignment_count<3` |
| Is empty | `fieldISEMPTY` | `assigned_toISEMPTY` |
| Is not empty | `fieldISNOTEMPTY` | `resolution_codeISNOTEMPTY` |
| In list | `fieldINvalue1,value2` | `stateIN1,2,3` |
| AND | `^` | `active=true^priority=1` |
| OR | `^OR` | `priority=1^ORpriority=2` |
| Dot-walking | `ref.field=value` | `caller_id.department=IT` |
| Order by | `^ORDERBY field` | `^ORDERBYsys_created_on` |
| Order descending | `^ORDERBYDESC field` | `^ORDERBYDESCpriority` |

---

## 🔒 Security

- **Zero hardcoded credentials** — all authentication is via environment variables
- **No instance URLs stored** — `SN_INSTANCE` is always read from env at runtime
- **Delete safety** — the `--confirm` flag is mandatory for all delete operations
- **Basic Auth** — uses standard ServiceNow REST API authentication

---

## 🏗️ Built By

**Brandon Wilson** — ServiceNow Certified Technical Architect (CTA)

- 🌐 [OnlyFlows](https://onlyflows.tech) — ServiceNow tools, skills & AI automation

- 🌐 [OnlyFlows.tech](https://onlyflows.tech) — Workflow automation & AI

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

Copyright © 2026 OnlyFlows

---

## 🤝 Contributing

Contributions welcome! Open an issue or PR at [github.com/onlyflowstech/servicenow-openclaw-skill](https://github.com/onlyflowstech/servicenow-openclaw-skill).

Ideas for contribution:
- Additional ServiceNow API support (CMDB API, Import Sets, Scripted REST)
- OAuth 2.0 authentication
- ServiceNow Flow Designer integration
