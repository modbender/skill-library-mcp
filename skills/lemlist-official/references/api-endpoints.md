# Lemlist API — Full Endpoint Reference

Base URL: `https://api.lemlist.com/api`

## Team

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/team` | Team info |
| GET | `/api/team/members` | List members |
| GET | `/api/team/overview` | Team overview |
| GET | `/api/team/credits` | Credit balance |
| GET | `/api/team/senders` | List senders and their campaigns |
| GET | `/api/team/crmUsers` | CRM users |
| GET | `/api/team/sendUsers` | Sending users |

## Campaigns

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/campaigns` | List campaigns (paginated) |
| POST | `/api/campaigns` | Create campaign. Body: `{ "name": "..." }`. Auto-adds empty sequence + default schedule |
| GET | `/api/campaigns/:campaignId` | Campaign details |
| PATCH | `/api/campaigns/:campaignId` | Update campaign |
| GET | `/api/campaigns/reports` | Campaign reports |
| POST | `/api/campaigns/:campaignId/pause` | Pause campaign |
| POST | `/api/campaigns/:campaignId/start` | Start campaign |
| GET | `/api/campaigns/:campaignId/stats` | Campaign stats (v1) |
| GET | `/api/v2/campaigns/:campaignId/stats` | Campaign stats (v2, more detailed) |
| POST | `/api/campaigns/:campaignId/leads/import` | Import leads CSV (`multipart/form-data`) |

NOTE: Campaigns **cannot be deleted** via API.

## Sequences & Steps

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/campaigns/:campaignId/sequences` | List sequences and steps |
| POST | `/api/sequences/:sequenceId/steps` | Create step |
| PATCH | `/api/sequences/:sequenceId/steps/:stepId` | Update step |
| DELETE | `/api/sequences/:sequenceId/steps/:stepId` | Delete step |

## Leads (Campaign Context)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/campaigns/:campaignId/leads` | List leads (paginated) |
| POST | `/api/campaigns/:campaignId/leads` | Add lead. Body: `{ "email", "firstName", "lastName", "companyName" }` |
| GET | `/api/campaigns/:campaignId/leads/:idOrEmail` | Get lead |
| PATCH | `/api/campaigns/:campaignId/leads/:idOrEmail` | Update lead |
| DELETE | `/api/campaigns/:campaignId/leads/:idOrEmail` | Remove lead from campaign |
| POST | `/api/campaigns/:campaignId/leads/:idOrEmail/interested` | Mark interested |
| POST | `/api/campaigns/:campaignId/leads/:idOrEmail/notinterested` | Mark not interested |

Emails in `:idOrEmail` must be URL-encoded (`@` → `%40`).

## Leads (Global)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/leads` | Search leads |
| GET | `/api/leads/:email` | Search by email |
| POST | `/api/leads/pause/:idOrEmail` | Pause lead |
| POST | `/api/leads/start/:idOrEmail` | Resume lead |
| POST | `/api/leads/interested/:idOrEmail` | Mark interested |
| POST | `/api/leads/notinterested/:idOrEmail` | Mark not interested |
| POST | `/api/leads/:leadId/variables` | Set variables |
| PATCH | `/api/leads/:leadId/variables` | Update variables |
| DELETE | `/api/leads/:leadId/variables` | Delete variables (NOT the lead) |
| POST | `/api/leads/audio` | Upload voice note |

## Enrichment

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/leads/:leadId/enrich` | Enrich a lead |
| GET | `/api/enrich/:enrichId` | Enrichment status |
| POST | `/api/enrich` | Batch enrichment |

## Activities

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/activities` | List activities (last 100). Filter: `campaignId`, `type` |
| POST | `/api/overview/activities/leadIds` | Lead IDs from activity filters |
| POST | `/api/overview/leads/ids` | Lead IDs from overview filters |

## Schedules

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/schedules` | List schedules |
| POST | `/api/schedules` | Create. Body: `{ "name", "timezone", "start", "end", "weekdays": [1,2,3,4,5] }`. Weekdays: 0=Sun..6=Sat |
| GET | `/api/schedules/:scheduleId` | Get schedule |
| PATCH | `/api/schedules/:scheduleId` | Update schedule |
| DELETE | `/api/schedules/:scheduleId` | Delete schedule |
| POST | `/api/campaigns/:campaignId/schedules` | Assign schedule to campaign |
| POST | `/api/campaigns/:campaignId/schedules/:scheduleId` | Assign specific schedule |

## Unsubscribes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/unsubscribes` | List unsubscribes |
| POST | `/api/unsubscribes/:value` | Add email or domain |
| DELETE | `/api/unsubscribes/:value` | Remove from list |

## Webhooks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/hooks` | List webhooks |
| POST | `/api/hooks` | Create webhook |
| DELETE | `/api/hooks/:_id` | Delete webhook |

### Create webhook body

```json
{
  "targetUrl": "https://your-endpoint.com/webhook",
  "type": "emailsOpened,emailsClicked",
  "campaignId": "cam_abc123",
  "isFirst": true,
  "secret": "your-shared-secret"
}
```

- `type`: comma-separated event types (optional — all if omitted)
- `campaignId`: filter to campaign (optional)
- `isFirst`: first-touch only (optional)
- `secret`: included in payload for verification (optional)
- Max 200 webhooks per team

### Events

**Activity:** `emailsSent`, `emailsOpened`, `emailsClicked`, `emailsReplied`, `emailsBounced`, `emailsFailed`, `emailsUnsubscribed`, `linkedinVisit`, `linkedinInvite`, `linkedinReplied`

**System:** `customDomainErrors`, `connectionIssue`, `sendLimitReached`, `lemwarmPaused`, `campaignComplete`, `enrichmentDone`, `enrichmentError`, `callTranscriptDone`, `callRecordingDone`, `inboxLabelUpdated`, `signalRegistered`

### Payload

```json
{
  "type": "emailsOpened",
  "campaignId": "...",
  "campaignName": "...",
  "leadId": "...",
  "email": "...",
  "firstName": "...",
  "lastName": "...",
  "variables": {},
  "labels": [],
  "sequenceTested": "A",
  "stepTested": 1,
  "emailTemplateName": "...",
  "secret": "your-secret-if-configured"
}
```

Verification: `payload.secret === your_configured_secret` (no HMAC).

Retries: up to 5, exponential backoff `10s * 2^retryCount`. 404/410 → webhook auto-deleted.

## Inbox

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/inbox` | List conversations (paginated) |
| POST | `/api/inbox/email` | Send email |
| POST | `/api/inbox/linkedin` | Send LinkedIn message |
| POST | `/api/inbox/whatsapp` | Send WhatsApp message |
| POST | `/api/inbox/sms` | Send SMS |
| GET | `/api/inbox/:contactId` | Get conversation |

### Inbox Labels

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/inbox/labels` | List labels |
| POST | `/api/inbox/labels` | Create label |
| GET | `/api/inbox/labels/:id` | Get label |
| PATCH | `/api/inbox/labels/:id` | Update label |
| DELETE | `/api/inbox/labels/:id` | Delete label |
| GET | `/api/inbox/conversations/labels/:contactId` | Get conversation labels |
| POST | `/api/inbox/conversations/labels/:contactId` | Assign label |
| DELETE | `/api/inbox/conversations/labels/:contactId` | Remove label |

## Companies & Contacts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/companies` | List companies |
| GET | `/api/companies/:companyId/notes` | Company notes |
| POST | `/api/companies/:companyId/notes` | Create note |
| GET | `/api/contacts` | Search contacts (query: `idsOrEmails`) |
| GET | `/api/contacts/:idOrEmail` | Contact details |

## Exports

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/campaigns/:campaignId/export` | Sync CSV export (direct) |
| GET | `/api/campaigns/:campaignId/export/start` | Start async export |
| GET | `/api/campaigns/:campaignId/export/:exportId/status` | Poll async status |
| PUT | `/api/campaigns/:campaignId/export/:exportId/email/:email` | Send export by email |
| GET | `/api/campaigns/:campaignId/export/leads` | CSV export (leads) |
| GET | `/api/campaigns/:campaignId/export/list` | CSV export (list) |
| GET | `/api/contacts/export` | Export contacts |
| POST | `/api/overview/activities/export` | Export activities |
| POST | `/api/overview/leads/export` | Export leads overview |
| GET | `/api/unsubs/export` | Export unsubscribes |
| POST | `/api/leads/export/hot-leads` | Export hot leads |

## Tasks (Opportunities)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tasks` | List tasks |
| POST | `/api/tasks` | Create task |
| PATCH | `/api/tasks` | Update task |
| POST | `/api/tasks/ignore` | Ignore tasks |

## Lemwarm

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/lemwarm/:userMailboxId/start` | Start warming |
| POST | `/api/lemwarm/:userMailboxId/pause` | Pause warming |
| GET | `/api/lemwarm/:userMailboxId/settings` | Get settings |
| PATCH | `/api/lemwarm/:userMailboxId/settings` | Update settings |

## CRM

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/crm/filters` | Available CRM filters |

## Domains

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/domains/redirect` | Check domain redirects |
