# CRM Setup Guide

## HubSpot

### Get API Key
1. Go to Settings → Integrations → Private Apps
2. Create a private app with scopes: `crm.objects.contacts.write`, `crm.objects.deals.write`
3. Copy the access token

### Configure
```json
{
  "default_crm": "hubspot",
  "crm": {
    "hubspot": {
      "api_key": "pat-na1-xxxxx",
      "pipeline_id": "default",
      "stage_id": "appointmentscheduled"
    }
  }
}
```

### Pipeline Stages
Default HubSpot pipeline stages: `appointmentscheduled` → `qualifiedtobuy` → `presentationscheduled` → `decisionmakerboughtin` → `contractsent` → `closedwon` / `closedlost`

---

## Pipedrive

### Get API Key
1. Settings → Personal Preferences → API
2. Copy your API token
3. Note your Pipedrive domain (e.g., `yourcompany` from `yourcompany.pipedrive.com`)

### Configure
```json
{
  "default_crm": "pipedrive",
  "crm": {
    "pipedrive": {
      "api_key": "xxxxx",
      "domain": "yourcompany"
    }
  }
}
```

---

## Zoho CRM

### Get Access Token
1. Go to https://api-console.zoho.com/
2. Create a Self Client
3. Generate token with scope: `ZohoCRM.modules.leads.CREATE,ZohoCRM.modules.contacts.CREATE`

### Configure
```json
{
  "default_crm": "zoho",
  "crm": {
    "zoho": {
      "access_token": "xxxxx",
      "refresh_token": "xxxxx"
    }
  }
}
```

**Note:** Zoho tokens expire in 1 hour. Use refresh token for long-running workflows.

---

## CSV Export (Universal Fallback)

Use `--crm csv` for any CRM that supports CSV import. Generates `reports/leads-export.csv` with standard fields.
