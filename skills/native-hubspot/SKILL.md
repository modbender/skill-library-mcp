---
name: hubspot
description: "Query and manage HubSpot CRM data via the HubSpot API. Use when you need to search or manage contacts, companies, deals, tickets, or pipelines. Supports creating, updating, and associating CRM objects. Calls api.hubapi.com directly with no third-party proxy."
metadata:
  openclaw:
    requires:
      env:
        - HUBSPOT_TOKEN
      bins:
        - python3
    primaryEnv: HUBSPOT_TOKEN
    files:
      - "scripts/*"
---

# HubSpot

Interact with HubSpot CRM directly via the HubSpot API (`api.hubapi.com`).

## Setup (one-time)

1. In HubSpot: Settings → Integrations → Private Apps → Create a private app
2. Give it scopes: `crm.objects.contacts.read`, `crm.objects.contacts.write`, `crm.objects.companies.read`, `crm.objects.companies.write`, `crm.objects.deals.read`, `crm.objects.deals.write`, `tickets`
3. Copy the access token
4. Set environment variable:
   ```
   HUBSPOT_TOKEN=pat-na1-...
   ```

## Queries

### Search contacts
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py search contacts --query "john"
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py search contacts --email "john@example.com"
```

### List contacts
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py list contacts --limit 20
```

### Get a specific object
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py get contacts 12345
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py get companies 67890
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py get deals 11111
```

### List companies
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py list companies --limit 20
```

### Search companies
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py search companies --query "Acme"
```

### List deals
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py list deals --limit 20
```

### Search deals
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py search deals --query "enterprise"
```

### List tickets
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py list tickets --limit 20
```

### Create a contact
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py create contacts --email "new@example.com" --firstname "Jane" --lastname "Doe"
```

### Create a company
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py create companies --name "Acme Corp" --domain "acme.com"
```

### Create a deal
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py create deals --dealname "Enterprise Plan" --amount 50000 --pipeline default --dealstage appointmentscheduled
```

### Update an object
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py update contacts 12345 --email "new@example.com" --phone "+1234567890"
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py update deals 11111 --dealstage closedwon --amount 75000
```

### Associate objects
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py associate contacts 12345 companies 67890
```

### List pipelines
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py pipelines deals
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py pipelines tickets
```

### List owners
```bash
python3 /mnt/skills/user/hubspot/scripts/hubspot_query.py owners
```
