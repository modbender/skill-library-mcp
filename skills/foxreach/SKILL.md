---
name: foxreach
description: Manage FoxReach cold email outreach — leads, campaigns, sequences, templates, email accounts, inbox, and analytics. Use when the user asks to create leads, manage campaigns, check analytics, send outreach, manage email sequences, or anything related to the FoxReach API.
argument-hint: "[resource] [action] [options]"
allowed-tools: Bash(python *), Bash(cd *), Bash(FOXREACH_API_KEY=* python *), Read, Grep, Glob
---

# FoxReach API Management Skill

You are managing the FoxReach cold email outreach platform through its Python SDK and CLI. This skill covers all API operations for leads, campaigns, sequences, templates, email accounts, inbox, and analytics.

## Setup & Authentication

The Python SDK is at `integrations/sdk-python/` and the CLI is at `integrations/cli/`. Both use API key authentication with keys prefixed `otr_`.

**Check if the SDK is available:**
```bash
python -c "from foxreach import FoxReach; print('SDK ready')"
```

**If not installed, install it:**
```bash
cd integrations/sdk-python && pip install -e .
```

**Authentication** — Always get the API key from the user or environment before making calls. Never hardcode keys. Use environment variable injection:
```bash
FOXREACH_API_KEY=otr_... python script.py
```

Or use the CLI config:
```bash
cd integrations/cli && PYTHONPATH=. python -m foxreach_cli.main config set-key --key otr_...
```

## How to Execute Operations

Write inline Python scripts using the SDK. Always follow this pattern:

```python
import json
from foxreach import FoxReach

client = FoxReach(api_key="otr_USER_KEY_HERE")

# ... perform operation ...

client.close()
```

For quick operations, use one-liners:
```bash
python -c "
from foxreach import FoxReach
client = FoxReach(api_key='otr_...')
result = client.leads.list(page_size=10)
for lead in result:
    print(f'{lead.id}  {lead.email}  {lead.status}')
print(f'Total: {result.meta.total}')
client.close()
"
```

---

## Resource Reference

For complete API details, see [api-reference.md](api-reference.md).
For usage examples of every operation, see [examples.md](examples.md).

---

## Quick Reference — Available Operations

### Leads
| Action | Method | Notes |
|--------|--------|-------|
| List | `client.leads.list(page=1, page_size=50, search=..., status=..., tags=...)` | Paginated, filterable |
| Get | `client.leads.get(lead_id)` | Returns single Lead |
| Create | `client.leads.create(LeadCreate(email=..., first_name=..., ...))` | Deduplicates by email |
| Update | `client.leads.update(lead_id, LeadUpdate(company=..., ...))` | Partial update |
| Delete | `client.leads.delete(lead_id)` | Soft-delete |

### Campaigns
| Action | Method | Notes |
|--------|--------|-------|
| List | `client.campaigns.list(status=...)` | Filter by draft/active/paused/completed |
| Get | `client.campaigns.get(campaign_id)` | Includes stats |
| Create | `client.campaigns.create(CampaignCreate(name=..., ...))` | Creates in draft |
| Update | `client.campaigns.update(campaign_id, CampaignUpdate(...))` | Can't edit if active |
| Delete | `client.campaigns.delete(campaign_id)` | Must be draft |
| Start | `client.campaigns.start(campaign_id)` | Transitions to active |
| Pause | `client.campaigns.pause(campaign_id)` | Pauses sending |
| Add Leads | `client.campaigns.add_leads(campaign_id, [lead_ids])` | Bulk add |
| Add Accounts | `client.campaigns.add_accounts(campaign_id, [account_ids])` | Assign senders |

### Sequences (nested under campaigns)
| Action | Method | Notes |
|--------|--------|-------|
| List | `client.campaigns.sequences.list(campaign_id)` | All steps |
| Create | `client.campaigns.sequences.create(campaign_id, SequenceCreate(body=..., ...))` | Add step |
| Update | `client.campaigns.sequences.update(campaign_id, seq_id, SequenceUpdate(...))` | Edit step |
| Delete | `client.campaigns.sequences.delete(campaign_id, seq_id)` | Remove step |

### Templates
| Action | Method | Notes |
|--------|--------|-------|
| List | `client.templates.list()` | Paginated |
| Get | `client.templates.get(template_id)` | Single template |
| Create | `client.templates.create(TemplateCreate(name=..., body=...))` | New template |
| Update | `client.templates.update(template_id, TemplateUpdate(...))` | Partial update |
| Delete | `client.templates.delete(template_id)` | Remove |

### Email Accounts
| Action | Method | Notes |
|--------|--------|-------|
| List | `client.email_accounts.list()` | Paginated |
| Get | `client.email_accounts.get(account_id)` | With health metrics |
| Delete | `client.email_accounts.delete(account_id)` | Remove |

### Inbox
| Action | Method | Notes |
|--------|--------|-------|
| List Threads | `client.inbox.list_threads(category=..., is_read=..., ...)` | Filterable |
| Get | `client.inbox.get(reply_id)` | Full thread |
| Update | `client.inbox.update(reply_id, ThreadUpdate(is_read=..., ...))` | Mark read/starred |

### Analytics
| Action | Method | Notes |
|--------|--------|-------|
| Overview | `client.analytics.overview()` | Dashboard KPIs |
| Campaign | `client.analytics.campaign(campaign_id)` | Metrics + daily stats |

---

## Pagination

List endpoints return `PaginatedResponse` objects:

```python
result = client.leads.list(page=1, page_size=50, search="acme")

# Access data
for lead in result:
    print(lead.email)

# Check pagination info
print(f"Page {result.meta.page}/{result.meta.total_pages}, {result.meta.total} total")

# Get next page
if result.has_next_page():
    next_result = result.next_page()

# Auto-paginate through ALL results
for lead in client.leads.list().auto_paging_iter():
    print(lead.email)
```

---

## Error Handling

Always wrap API calls in try/except:

```python
from foxreach import FoxReach, NotFoundError, RateLimitError, AuthenticationError, FoxReachError

try:
    lead = client.leads.get("cld_nonexistent")
except NotFoundError:
    print("Lead not found")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except FoxReachError as e:
    print(f"API error: {e}")
```

---

## Template Variables & Personalization

Email bodies support variable substitution using `{{variable}}` syntax:
- `{{firstName}}`, `{{lastName}}`, `{{email}}`
- `{{company}}`, `{{title}}`, `{{phone}}`
- `{{website}}`, `{{linkedinUrl}}`
- Custom fields: `{{customFieldName}}`

Spintax is also supported: `{Hi|Hey|Hello} {{firstName}}`

---

## Common Workflows

### 1. Full Campaign Setup
When the user wants to set up a complete campaign, follow these steps in order:
1. Create the campaign with `campaigns.create()`
2. Add sequence steps with `campaigns.sequences.create()` for each email in the chain
3. Add leads with `campaigns.add_leads()`
4. Assign email accounts with `campaigns.add_accounts()`
5. Start the campaign with `campaigns.start()`

### 2. Check Campaign Performance
1. Get campaign analytics with `analytics.campaign(id)`
2. Show sent, delivered, bounced, replied, opened stats
3. Show reply rate and bounce rate
4. If daily_stats are available, summarize trends

### 3. Manage Inbox
1. List unread threads with `inbox.list_threads(is_read=False)`
2. Categorize replies by updating with `inbox.update(id, ThreadUpdate(category="interested"))`
3. Common categories: interested, not_interested, out_of_office, wrong_person, unsubscribe

### 4. Bulk Lead Import
For adding multiple leads, create them one by one (the API deduplicates by email):
```python
leads_data = [
    {"email": "a@example.com", "first_name": "Alice", "company": "Acme"},
    {"email": "b@example.com", "first_name": "Bob", "company": "Beta"},
]
created = []
for data in leads_data:
    lead = client.leads.create(LeadCreate(**data))
    created.append(lead)
    print(f"Created: {lead.id} - {lead.email}")
```

---

## Important Notes

- **Base URL**: `https://api.foxreach.io/api/v1`
- **Rate limit**: 100 requests per minute. The SDK auto-retries on 429.
- **ID prefixes**: Leads `cld_`, Campaigns `cmp_`, Replies `rpl_`, Templates `tpl_`
- **Timezone**: All datetimes in UTC ISO 8601 format.
- **Sending days**: Array of integers, 1=Monday through 7=Sunday.
- **Sending hours**: 0-23 range, in the campaign's timezone.
- **Campaign status flow**: draft → active → paused → active → completed
- **Soft deletes**: Leads are soft-deleted and can reappear on re-import.
- Always confirm with the user before destructive operations (delete, start campaign).
- When listing data, default to showing a formatted summary, not raw JSON.
- When creating resources, confirm the details with the user before executing.
