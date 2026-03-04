# hubspot

An [OpenClaw](https://clawhub.ai) skill for querying and managing your HubSpot CRM — directly via `api.hubapi.com`, no third-party proxy.

## What it does

Search and manage contacts, companies, deals, and tickets. Create and update CRM records, associate objects, inspect pipelines, and list owners.

## Setup

**1. Create a HubSpot private app**

Go to HubSpot → Settings → Integrations → Private Apps → Create a private app.

Required scopes:

```
crm.objects.contacts.read
crm.objects.contacts.write
crm.objects.companies.read
crm.objects.companies.write
crm.objects.deals.read
crm.objects.deals.write
tickets
```

**2. Set the environment variable**

```bash
export HUBSPOT_TOKEN=pat-na1-...
```

## Supported objects

| Object | List | Search | Get | Create | Update | Associate |
|---|---|---|---|---|---|---|
| contacts | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| companies | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| deals | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| tickets | ✅ | | ✅ | ✅ | ✅ | ✅ |

## Usage

### List

```bash
python3 scripts/hubspot_query.py list contacts --limit 20
python3 scripts/hubspot_query.py list companies --limit 20
python3 scripts/hubspot_query.py list deals --limit 20
python3 scripts/hubspot_query.py list tickets --limit 20
```

### Search

```bash
python3 scripts/hubspot_query.py search contacts --query "john"
python3 scripts/hubspot_query.py search contacts --email "john@acme.com"
python3 scripts/hubspot_query.py search companies --query "Acme"
python3 scripts/hubspot_query.py search deals --query "enterprise"
```

### Get

```bash
python3 scripts/hubspot_query.py get contacts 12345
python3 scripts/hubspot_query.py get companies 67890
python3 scripts/hubspot_query.py get deals 11111
```

### Create

```bash
python3 scripts/hubspot_query.py create contacts --email "jane@acme.com" --firstname "Jane" --lastname "Doe"
python3 scripts/hubspot_query.py create companies --name "Acme Corp" --domain "acme.com"
python3 scripts/hubspot_query.py create deals --dealname "Enterprise Plan" --amount 50000 --pipeline default --dealstage appointmentscheduled
```

### Update

```bash
python3 scripts/hubspot_query.py update contacts 12345 --email "new@acme.com" --phone "+1234567890"
python3 scripts/hubspot_query.py update deals 11111 --dealstage closedwon --amount 75000
```

### Associate objects

```bash
python3 scripts/hubspot_query.py associate contacts 12345 companies 67890
python3 scripts/hubspot_query.py associate contacts 12345 deals 11111
```

Supported associations: contacts ↔ companies, contacts ↔ deals, contacts ↔ tickets, companies ↔ deals.

### Pipelines

```bash
python3 scripts/hubspot_query.py pipelines deals
python3 scripts/hubspot_query.py pipelines tickets
```

### Owners

```bash
python3 scripts/hubspot_query.py owners
```

## Requirements

- Python 3 (stdlib only, no pip installs)
- `HUBSPOT_TOKEN` environment variable

## How it works

All requests go directly to `https://api.hubapi.com/crm/v3` using your private app token as a Bearer token. No intermediary services, no OAuth flow, no additional dependencies.
