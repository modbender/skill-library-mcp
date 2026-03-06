# FoxReach SDK Examples

Complete working examples for every operation. Replace `otr_YOUR_KEY` with a real API key.

---

## Leads

### List leads with filters

```python
from foxreach import FoxReach

client = FoxReach(api_key="otr_YOUR_KEY")

# Basic list
page = client.leads.list(page_size=10)
for lead in page:
    print(f"{lead.id}  {lead.email}  {lead.first_name}  {lead.status}")
print(f"\nPage {page.meta.page}/{page.meta.total_pages} — {page.meta.total} total leads")

# Search by email or name
results = client.leads.list(search="acme", status="active")
for lead in results:
    print(f"{lead.email} at {lead.company}")

# Auto-paginate through ALL leads
count = 0
for lead in client.leads.list(page_size=100).auto_paging_iter():
    count += 1
print(f"Total leads iterated: {count}")

client.close()
```

### Get a single lead

```python
from foxreach import FoxReach, NotFoundError

client = FoxReach(api_key="otr_YOUR_KEY")

try:
    lead = client.leads.get("cld_abc123def456")
    print(f"Name: {lead.first_name} {lead.last_name}")
    print(f"Email: {lead.email}")
    print(f"Company: {lead.company}")
    print(f"Title: {lead.title}")
    print(f"Status: {lead.status}")
    print(f"Tags: {', '.join(lead.tags) if lead.tags else 'none'}")
    print(f"Created: {lead.created_at}")
except NotFoundError:
    print("Lead not found")

client.close()
```

### Create a lead

```python
from foxreach import FoxReach, LeadCreate

client = FoxReach(api_key="otr_YOUR_KEY")

lead = client.leads.create(LeadCreate(
    email="jane.smith@acme.com",
    first_name="Jane",
    last_name="Smith",
    company="Acme Corp",
    title="VP of Sales",
    phone="+1-555-0123",
    linkedin_url="https://linkedin.com/in/janesmith",
    website="https://acme.com",
    notes="Met at SaaStr conference. Interested in our enterprise plan.",
    tags=["conference", "enterprise"],
))

print(f"Created lead: {lead.id} — {lead.email}")
client.close()
```

### Update a lead

```python
from foxreach import FoxReach, LeadUpdate

client = FoxReach(api_key="otr_YOUR_KEY")

lead = client.leads.update("cld_abc123def456", LeadUpdate(
    company="Acme International",
    title="SVP of Sales",
    notes="Promoted in Q1. Follow up on enterprise plan.",
))

print(f"Updated lead: {lead.id} — {lead.company}")
client.close()
```

### Delete a lead

```python
from foxreach import FoxReach

client = FoxReach(api_key="otr_YOUR_KEY")
client.leads.delete("cld_abc123def456")
print("Lead deleted")
client.close()
```

### Bulk create leads

```python
from foxreach import FoxReach, LeadCreate

client = FoxReach(api_key="otr_YOUR_KEY")

contacts = [
    {"email": "alice@startup.io", "first_name": "Alice", "company": "Startup Inc"},
    {"email": "bob@bigcorp.com", "first_name": "Bob", "company": "BigCorp"},
    {"email": "carol@techco.dev", "first_name": "Carol", "company": "TechCo", "title": "CTO"},
]

created = []
for contact in contacts:
    lead = client.leads.create(LeadCreate(**contact))
    created.append(lead)
    print(f"  Created: {lead.id} — {lead.email}")

print(f"\n{len(created)} leads created")
client.close()
```

---

## Campaigns

### List campaigns

```python
from foxreach import FoxReach

client = FoxReach(api_key="otr_YOUR_KEY")

# All campaigns
page = client.campaigns.list()
for c in page:
    print(f"{c.id}  {c.name:30s}  {c.status:10s}  sent:{c.total_sent}  replied:{c.total_replied}")

# Only active campaigns
active = client.campaigns.list(status="active")
for c in active:
    print(f"{c.name} — {c.total_sent} sent, {c.total_replied} replied")

client.close()
```

### Create a campaign

```python
from foxreach import FoxReach, CampaignCreate

client = FoxReach(api_key="otr_YOUR_KEY")

campaign = client.campaigns.create(CampaignCreate(
    name="Q1 2025 Outreach — Enterprise",
    timezone="America/New_York",
    sending_days=[1, 2, 3, 4, 5],      # Mon-Fri
    sending_start_hour=9,
    sending_end_hour=17,
    daily_limit=100,
))

print(f"Campaign created: {campaign.id} — {campaign.name} (status: {campaign.status})")
client.close()
```

### Full campaign setup (create → sequences → leads → accounts → start)

```python
from foxreach import FoxReach, CampaignCreate, SequenceCreate

client = FoxReach(api_key="otr_YOUR_KEY")

# 1. Create campaign
campaign = client.campaigns.create(CampaignCreate(
    name="Product Launch Outreach",
    timezone="America/New_York",
    daily_limit=50,
))
print(f"1. Campaign created: {campaign.id}")

# 2. Add sequence steps
step1 = client.campaigns.sequences.create(campaign.id, SequenceCreate(
    subject="Quick question about {{company}}",
    body="Hi {{firstName}},\n\nI noticed {{company}} is growing fast. We help companies like yours with cold email outreach.\n\nWould you be open to a quick chat this week?\n\nBest,\n[Your Name]",
    delay_days=0,
))
print(f"2. Step 1 added: {step1.id}")

step2 = client.campaigns.sequences.create(campaign.id, SequenceCreate(
    subject="Re: Quick question about {{company}}",
    body="Hi {{firstName}},\n\nJust following up on my last email. I know you're busy — would a 15-minute call work better?\n\nHere's a link to book time: [calendar link]\n\nCheers,\n[Your Name]",
    delay_days=3,
))
print(f"   Step 2 added: {step2.id}")

step3 = client.campaigns.sequences.create(campaign.id, SequenceCreate(
    subject="Last try — {{firstName}}",
    body="Hi {{firstName}},\n\n{I understand if this isn't a priority right now|No worries if the timing isn't right}. I'll leave the door open — feel free to reach out anytime.\n\nBest,\n[Your Name]",
    delay_days=5,
))
print(f"   Step 3 added: {step3.id}")

# 3. Add leads
lead_ids = ["cld_lead1", "cld_lead2", "cld_lead3"]
result = client.campaigns.add_leads(campaign.id, lead_ids)
print(f"3. Added {result.get('added', len(lead_ids))} leads")

# 4. Assign email accounts
account_ids = ["acc_sender1"]
result = client.campaigns.add_accounts(campaign.id, account_ids)
print(f"4. Assigned {result.get('added', len(account_ids))} email accounts")

# 5. Start campaign
campaign = client.campaigns.start(campaign.id)
print(f"5. Campaign started! Status: {campaign.status}")

client.close()
```

### Pause / update a campaign

```python
from foxreach import FoxReach, CampaignUpdate

client = FoxReach(api_key="otr_YOUR_KEY")

# Pause
campaign = client.campaigns.pause("cmp_xyz789")
print(f"Paused: {campaign.name}")

# Update settings while paused
campaign = client.campaigns.update("cmp_xyz789", CampaignUpdate(
    daily_limit=200,
    sending_end_hour=19,
))
print(f"Updated daily limit to {campaign.daily_limit}")

client.close()
```

---

## Sequences

### List sequences for a campaign

```python
from foxreach import FoxReach

client = FoxReach(api_key="otr_YOUR_KEY")

steps = client.campaigns.sequences.list("cmp_xyz789")
for step in steps:
    print(f"Step {step.step_number}: {step.subject or '(no subject)'}")
    print(f"  Delay: {step.delay_days} days")
    print(f"  Body preview: {step.body[:80]}...")
    print()

client.close()
```

### Update a sequence step

```python
from foxreach import FoxReach, SequenceUpdate

client = FoxReach(api_key="otr_YOUR_KEY")

updated = client.campaigns.sequences.update(
    "cmp_xyz789",
    "seq_step2",
    SequenceUpdate(
        delay_days=5,
        body="Updated follow-up body with {{firstName}} personalization.",
    ),
)
print(f"Updated step {updated.step_number}, delay now {updated.delay_days} days")

client.close()
```

---

## Templates

### Create and list templates

```python
from foxreach import FoxReach, TemplateCreate

client = FoxReach(api_key="otr_YOUR_KEY")

# Create
template = client.templates.create(TemplateCreate(
    name="Cold Intro — SaaS",
    subject="Quick question about {{company}}",
    body="Hi {{firstName}},\n\nI saw that {{company}} is {{title ? 'hiring for ' + title : 'growing'}}. We help teams like yours scale outreach.\n\nWorth a quick chat?\n\nBest,\n[Your Name]",
))
print(f"Template created: {template.id}")

# List all
page = client.templates.list()
for t in page:
    print(f"  {t.id}  {t.name:30s}  {t.template_type}")

client.close()
```

---

## Email Accounts

### List accounts with health

```python
from foxreach import FoxReach

client = FoxReach(api_key="otr_YOUR_KEY")

page = client.email_accounts.list()
for acct in page:
    health = f"{acct.health_score:.0f}" if acct.health_score is not None else "N/A"
    active = "active" if acct.is_active else "inactive"
    print(f"  {acct.email:35s}  {active:10s}  health:{health}  sent:{acct.sent_today}/{acct.daily_limit}")

client.close()
```

---

## Inbox

### List unread replies

```python
from foxreach import FoxReach

client = FoxReach(api_key="otr_YOUR_KEY")

unread = client.inbox.list_threads(is_read=False, page_size=20)
for thread in unread:
    star = "*" if thread.is_starred else " "
    cat = thread.category or "uncategorized"
    print(f"  {star} {thread.from_email:30s}  {cat:15s}  {thread.subject}")

print(f"\n{unread.meta.total} unread threads")
client.close()
```

### Categorize a reply

```python
from foxreach import FoxReach, ThreadUpdate

client = FoxReach(api_key="otr_YOUR_KEY")

# Mark as read and categorize
thread = client.inbox.update("rpl_abc123", ThreadUpdate(
    is_read=True,
    category="interested",
    is_starred=True,
))
print(f"Thread {thread.id} marked as {thread.category}")

client.close()
```

---

## Analytics

### Dashboard overview

```python
from foxreach import FoxReach

client = FoxReach(api_key="otr_YOUR_KEY")

stats = client.analytics.overview()
print("=== Dashboard Overview ===")
print(f"Accounts:  {stats.active_accounts}/{stats.total_accounts} active")
print(f"Campaigns: {stats.active_campaigns}/{stats.total_campaigns} active")
print(f"Leads:     {stats.total_leads:,}")
print(f"Sent:      {stats.total_sent:,}")
print(f"Replies:   {stats.total_replies:,}")
print(f"Reply Rate: {stats.reply_rate:.1f}%")
print(f"Avg Health: {stats.account_health_avg:.0f}/100")

client.close()
```

### Campaign analytics with daily breakdown

```python
from foxreach import FoxReach

client = FoxReach(api_key="otr_YOUR_KEY")

stats = client.analytics.campaign("cmp_xyz789")
print("=== Campaign Analytics ===")
print(f"Sent: {stats.sent}  Delivered: {stats.delivered}  Bounced: {stats.bounced}")
print(f"Replied: {stats.replied}  Opened: {stats.opened}")
print(f"Reply Rate: {stats.reply_rate:.1f}%  Bounce Rate: {stats.bounce_rate:.1f}%")

if stats.daily_stats:
    print("\nDaily breakdown:")
    print(f"{'Date':12s} {'Sent':>6s} {'Delivered':>10s} {'Bounced':>8s} {'Replied':>8s} {'Opened':>7s}")
    print("-" * 55)
    for day in stats.daily_stats:
        print(f"{day.date:12s} {day.sent:6d} {day.delivered:10d} {day.bounced:8d} {day.replied:8d} {day.opened:7d}")

client.close()
```

---

## Error Handling

### Comprehensive error handling example

```python
from foxreach import (
    FoxReach,
    FoxReachError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    BadRequestError,
    ServerError,
    ConnectionError,
    LeadCreate,
)

client = FoxReach(api_key="otr_YOUR_KEY")

try:
    lead = client.leads.create(LeadCreate(email="invalid"))
except ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Details: {e.response_body}")
except BadRequestError as e:
    print(f"Bad request: {e}")
except AuthenticationError:
    print("Invalid API key. Check your configuration.")
except NotFoundError:
    print("Resource not found.")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds.")
except ServerError as e:
    print(f"Server error ({e.status_code}): {e}")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except FoxReachError as e:
    print(f"Unexpected API error: {e}")

client.close()
```

---

## Async Usage

All operations are available asynchronously:

```python
import asyncio
from foxreach import AsyncFoxReach, LeadCreate

async def main():
    async with AsyncFoxReach(api_key="otr_YOUR_KEY") as client:
        # Create a lead
        lead = await client.leads.create(LeadCreate(
            email="async@example.com",
            first_name="Async",
        ))
        print(f"Created: {lead.id}")

        # List with auto-pagination
        async for lead in (await client.leads.list()).auto_paging_iter():
            print(lead.email)

        # Get analytics
        overview = await client.analytics.overview()
        print(f"Total leads: {overview.total_leads}")

asyncio.run(main())
```
