# Index

| API | Line |
|-----|------|
| Salesforce | 2 |
| HubSpot | 102 |
| Pipedrive | 212 |
| Attio | 290 |
| Close | 372 |
| Apollo | 459 |
| Outreach | 550 |
| Gong | 656 |

---

# Salesforce

## Base URL
```
https://{instance}.salesforce.com/services/data/v59.0
```

## Authentication
```bash
# After OAuth flow
curl "https://{instance}.salesforce.com/services/data/v59.0/" \
  -H "Authorization: Bearer $SALESFORCE_ACCESS_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /sobjects/:type | POST | Create record |
| /sobjects/:type/:id | GET | Get record |
| /sobjects/:type/:id | PATCH | Update record |
| /sobjects/:type/:id | DELETE | Delete record |
| /query | GET | SOQL query |

## Quick Examples

### SOQL Query
```bash
curl "https://{instance}.salesforce.com/services/data/v59.0/query?q=SELECT+Id,Name,Email+FROM+Contact+LIMIT+10" \
  -H "Authorization: Bearer $SALESFORCE_ACCESS_TOKEN"
```

### Get Record
```bash
curl "https://{instance}.salesforce.com/services/data/v59.0/sobjects/Contact/003xx000001234" \
  -H "Authorization: Bearer $SALESFORCE_ACCESS_TOKEN"
```

### Create Contact
```bash
curl -X POST "https://{instance}.salesforce.com/services/data/v59.0/sobjects/Contact" \
  -H "Authorization: Bearer $SALESFORCE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "FirstName": "John",
    "LastName": "Doe",
    "Email": "john@example.com",
    "AccountId": "001xx000001234"
  }'
```

### Update Record
```bash
curl -X PATCH "https://{instance}.salesforce.com/services/data/v59.0/sobjects/Contact/003xx000001234" \
  -H "Authorization: Bearer $SALESFORCE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"Email": "newemail@example.com"}'
```

### Delete Record
```bash
curl -X DELETE "https://{instance}.salesforce.com/services/data/v59.0/sobjects/Contact/003xx000001234" \
  -H "Authorization: Bearer $SALESFORCE_ACCESS_TOKEN"
```

## SOQL Examples

| Query | Description |
|-------|-------------|
| `SELECT Id, Name FROM Account` | Basic select |
| `SELECT Id FROM Contact WHERE Email LIKE '%@example.com'` | Filter |
| `SELECT Id, Account.Name FROM Contact` | Related object |
| `SELECT Id, (SELECT Id FROM Contacts) FROM Account` | Subquery |
| `SELECT Id FROM Opportunity WHERE Amount > 10000` | Comparison |

## Common Objects

| Object | Description |
|--------|-------------|
| Account | Companies |
| Contact | People |
| Lead | Prospects |
| Opportunity | Deals |
| Case | Support tickets |
| Task | Activities |

## Common Traps

- Instance URL varies (na1, eu1, etc.) - get from OAuth response
- API version in URL (v59.0) - use latest
- SOQL is SQL-like but different syntax
- Record IDs are 15 or 18 characters (both work)
- Rate limits vary by edition (Enterprise vs Professional)

## Rate Limits

Varies by edition. Enterprise: ~100,000 requests/24 hours

## Official Docs
https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/
# HubSpot

## Base URL
```
https://api.hubapi.com
```

## Authentication
```bash
curl https://api.hubapi.com/crm/v3/objects/contacts \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /crm/v3/objects/contacts | GET | List contacts |
| /crm/v3/objects/contacts | POST | Create contact |
| /crm/v3/objects/companies | GET | List companies |
| /crm/v3/objects/deals | GET | List deals |
| /crm/v3/objects/deals | POST | Create deal |
| /crm/v3/objects/:type/search | POST | Search objects |

## Quick Examples

### List Contacts
```bash
curl "https://api.hubapi.com/crm/v3/objects/contacts?limit=10" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

### Create Contact
```bash
curl -X POST https://api.hubapi.com/crm/v3/objects/contacts \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "email": "user@example.com",
      "firstname": "John",
      "lastname": "Doe",
      "company": "Acme Inc"
    }
  }'
```

### Create Deal
```bash
curl -X POST https://api.hubapi.com/crm/v3/objects/deals \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "dealname": "New Deal",
      "amount": "10000",
      "dealstage": "qualifiedtobuy",
      "pipeline": "default"
    }
  }'
```

### Search Contacts
```bash
curl -X POST https://api.hubapi.com/crm/v3/objects/contacts/search \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filterGroups": [{
      "filters": [{
        "propertyName": "email",
        "operator": "CONTAINS_TOKEN",
        "value": "example.com"
      }]
    }],
    "limit": 10
  }'
```

### Associate Objects
```bash
curl -X PUT "https://api.hubapi.com/crm/v3/objects/contacts/$CONTACT_ID/associations/deals/$DEAL_ID/contact_to_deal" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

## Object Types

| Type | Endpoint |
|------|----------|
| contacts | /crm/v3/objects/contacts |
| companies | /crm/v3/objects/companies |
| deals | /crm/v3/objects/deals |
| tickets | /crm/v3/objects/tickets |
| products | /crm/v3/objects/products |

## Common Traps

- Properties use internal names, not display names
- Search requires specific filter operators
- Associations are directional (contact_to_deal vs deal_to_contact)
- Pagination uses `after` cursor, not offset
- Email is unique identifier for contacts

## Rate Limits

- OAuth apps: 100 requests/10 seconds per app
- Private apps: 100 requests/10 seconds per account

## Official Docs
https://developers.hubspot.com/docs/api/crm/contacts
# Pipedrive

Sales CRM with pipeline management, deals tracking, and contact organization.

## Base URL
`https://api.pipedrive.com/v1`

## Authentication
API key via query parameter or OAuth 2.0. API keys can be found in Settings > Personal preferences > API.

```bash
# API Key auth (query param)
curl "https://api.pipedrive.com/v1/deals?api_token=$PIPEDRIVE_API_KEY"

# OAuth 2.0 Bearer token
curl https://api.pipedrive.com/v1/deals \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Core Endpoints

### List Deals
```bash
curl "https://api.pipedrive.com/v1/deals?api_token=$PIPEDRIVE_API_KEY&status=open&limit=50"
```

### Create Deal
```bash
curl -X POST "https://api.pipedrive.com/v1/deals?api_token=$PIPEDRIVE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Deal",
    "value": 5000,
    "currency": "USD",
    "person_id": 123,
    "org_id": 456
  }'
```

### Get Person (Contact)
```bash
curl "https://api.pipedrive.com/v1/persons/123?api_token=$PIPEDRIVE_API_KEY"
```

### Create Activity
```bash
curl -X POST "https://api.pipedrive.com/v1/activities?api_token=$PIPEDRIVE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Call with client",
    "type": "call",
    "due_date": "2024-03-15",
    "deal_id": 789
  }'
```

### Search Items
```bash
curl "https://api.pipedrive.com/v1/itemSearch?term=acme&item_types=deal,person&api_token=$PIPEDRIVE_API_KEY"
```

## Rate Limits
- **Standard:** 100 requests per 10 seconds per API token
- **OAuth apps:** 80 requests per 2 seconds per company
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Gotchas
- API key in query param is deprecated for OAuth apps — use Bearer token
- Custom fields use hash keys like `abc123_custom_field` — fetch field definitions first
- Pagination uses `start` and `limit` params, not page numbers
- `additional_data.pagination` in response tells if more data exists
- Deals without `person_id` or `org_id` are valid but less useful
- Activities require a `type` that matches ActivityTypes in your account

## Links
- [Docs](https://pipedrive.readme.io/docs)
- [API Reference](https://developers.pipedrive.com/docs/api/v1)
- [OpenAPI Spec](https://developers.pipedrive.com/docs/api/v1/openapi.yaml)
# Attio

Modern CRM with flexible data modeling, custom objects, and relationship intelligence.

## Base URL
`https://api.attio.com/v2`

## Authentication
Bearer token via OAuth 2.0 or API key generated in workspace settings.

```bash
curl https://api.attio.com/v2/objects \
  -H "Authorization: Bearer $ATTIO_API_KEY" \
  -H "Content-Type: application/json"
```

## Core Endpoints

### List Objects (Schema)
```bash
curl https://api.attio.com/v2/objects \
  -H "Authorization: Bearer $ATTIO_API_KEY"
```

### List Records
```bash
curl -X POST https://api.attio.com/v2/objects/companies/records/query \
  -H "Authorization: Bearer $ATTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 25,
    "sorts": [{"attribute": "name", "direction": "asc"}]
  }'
```

### Create Record
```bash
curl -X POST https://api.attio.com/v2/objects/companies/records \
  -H "Authorization: Bearer $ATTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "values": {
        "name": [{"value": "Acme Corp"}],
        "domains": [{"domain": "acme.com"}]
      }
    }
  }'
```

### Get Record
```bash
curl https://api.attio.com/v2/objects/companies/records/abc123 \
  -H "Authorization: Bearer $ATTIO_API_KEY"
```

### List Entries (from a List)
```bash
curl -X POST https://api.attio.com/v2/lists/my-list/entries/query \
  -H "Authorization: Bearer $ATTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"limit": 50}'
```

## Rate Limits
- **Read requests:** 100 requests/second
- **Write requests:** 25 requests/second
- Score-based limits for complex queries on List/Record endpoints
- Response includes `Retry-After` header when limited (HTTP 429)

## Gotchas
- Attribute values are arrays — even single values: `"name": [{"value": "X"}]`
- Objects are schema definitions, Records are instances
- Lists have Entries (records + list-specific attributes)
- Query endpoints use POST with JSON body for filters/sorts
- Complex filters can hit score-based rate limits even under request/sec limits
- Workspace-level API keys, not user-level

## Links
- [Docs](https://docs.attio.com/)
- [API Reference](https://docs.attio.com/rest-api)
- [Authentication Guide](https://docs.attio.com/rest-api/guides/authentication)
# Close

Sales CRM built for inside sales teams with built-in calling, email, and SMS.

## Base URL
`https://api.close.com/api/v1`

## Authentication
HTTP Basic Auth with API key as username and empty password.

```bash
curl https://api.close.com/api/v1/me/ \
  -u "$CLOSE_API_KEY:"

# Note the trailing colon — password is empty
```

## Core Endpoints

### Get Current User
```bash
curl https://api.close.com/api/v1/me/ \
  -u "$CLOSE_API_KEY:"
```

### List Leads
```bash
curl "https://api.close.com/api/v1/lead/?_limit=50" \
  -u "$CLOSE_API_KEY:"
```

### Create Lead
```bash
curl -X POST https://api.close.com/api/v1/lead/ \
  -u "$CLOSE_API_KEY:" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp",
    "contacts": [{
      "name": "John Doe",
      "emails": [{"email": "john@acme.com", "type": "office"}],
      "phones": [{"phone": "+15551234567", "type": "office"}]
    }],
    "custom.cf_ABC123": "custom value"
  }'
```

### Search Leads
```bash
curl -X POST https://api.close.com/api/v1/lead/search/ \
  -u "$CLOSE_API_KEY:" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "status:\"Potential\"",
    "_limit": 25
  }'
```

### Log Activity
```bash
curl -X POST https://api.close.com/api/v1/activity/note/ \
  -u "$CLOSE_API_KEY:" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "lead_ABC123",
    "note": "Had a great call with the team"
  }'
```

## Rate Limits
- **Burst:** 300 requests per minute
- **Sustained:** Lower limits for write-heavy operations
- Headers: `X-Rate-Limit-Limit`, `X-Rate-Limit-Remaining`, `X-Rate-Limit-Reset`
- HTTP 429 when exceeded with `Retry-After` header

## Gotchas
- API key goes in Basic Auth username field, password is EMPTY (don't forget the colon)
- Custom fields use `custom.cf_XXXXX` format — fetch field IDs from `/custom_field/lead/`
- Leads contain Contacts (people) — they're not separate entities
- Search uses Close's query language, not JSON filters
- Trailing slashes matter on endpoints
- Activities are per-type: `/activity/note/`, `/activity/call/`, `/activity/email/`

## Links
- [Docs](https://developer.close.com/)
- [API Reference](https://developer.close.com/resources/)
- [Authentication](https://developer.close.com/topics/authentication/)
# Apollo

Sales intelligence platform for prospecting, enrichment, and outreach automation.

## Base URL
`https://api.apollo.io/api/v1`

## Authentication
API key via header or query parameter.

```bash
curl https://api.apollo.io/api/v1/auth/health \
  -H "X-Api-Key: $APOLLO_API_KEY"

# Or via query param (deprecated)
curl "https://api.apollo.io/api/v1/auth/health?api_key=$APOLLO_API_KEY"
```

## Core Endpoints

### People Enrichment
```bash
curl -X POST https://api.apollo.io/api/v1/people/match \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@acme.com"
  }'
```

### Organization Enrichment
```bash
curl "https://api.apollo.io/api/v1/organizations/enrich?domain=acme.com" \
  -H "X-Api-Key: $APOLLO_API_KEY"
```

### People Search
```bash
curl -X POST https://api.apollo.io/api/v1/mixed_people/search \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "person_titles": ["CEO", "CTO"],
    "organization_locations": ["United States"],
    "per_page": 25,
    "page": 1
  }'
```

### Create Contact
```bash
curl -X POST https://api.apollo.io/api/v1/contacts \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@acme.com",
    "organization_name": "Acme Corp"
  }'
```

### Add to Sequence
```bash
curl -X POST https://api.apollo.io/api/v1/emailer_campaigns/add_contact_ids \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_ids": ["contact_id_123"],
    "emailer_campaign_id": "sequence_id_456"
  }'
```

## Rate Limits
- Varies by plan and endpoint
- Enrichment endpoints have credit costs, not just rate limits
- Check `/api/v1/auth/health` for current usage stats
- Rate limit headers included in responses

## Gotchas
- Enrichment consumes credits — check your plan's allocation
- `mixed_people/search` returns both Apollo DB and your contacts
- Bulk enrichment endpoints have different limits than single-record
- Some fields require specific plan tiers to access
- `person_titles` is an array, even for single title searches
- Contact and Lead are different entities — Contacts are in your CRM

## Links
- [Docs](https://docs.apollo.io/)
- [API Reference](https://docs.apollo.io/reference/api-overview)
- [Rate Limits](https://docs.apollo.io/reference/rate-limits)
# Outreach

Sales engagement platform for sequences, email automation, and prospect management.

## Base URL
`https://api.outreach.io/api/v2`

## Authentication
OAuth 2.0 only. Requires app registration and authorization flow.

```bash
curl https://api.outreach.io/api/v2/prospects \
  -H "Authorization: Bearer $OUTREACH_ACCESS_TOKEN" \
  -H "Content-Type: application/vnd.api+json"
```

## Core Endpoints

### List Prospects
```bash
curl "https://api.outreach.io/api/v2/prospects?page[limit]=25" \
  -H "Authorization: Bearer $OUTREACH_ACCESS_TOKEN" \
  -H "Content-Type: application/vnd.api+json"
```

### Create Prospect
```bash
curl -X POST https://api.outreach.io/api/v2/prospects \
  -H "Authorization: Bearer $OUTREACH_ACCESS_TOKEN" \
  -H "Content-Type: application/vnd.api+json" \
  -d '{
    "data": {
      "type": "prospect",
      "attributes": {
        "emails": ["sally@acme.com"],
        "firstName": "Sally",
        "lastName": "Smith",
        "title": "CEO"
      },
      "relationships": {
        "account": {
          "data": {"type": "account", "id": 1}
        }
      }
    }
  }'
```

### Create Account
```bash
curl -X POST https://api.outreach.io/api/v2/accounts \
  -H "Authorization: Bearer $OUTREACH_ACCESS_TOKEN" \
  -H "Content-Type: application/vnd.api+json" \
  -d '{
    "data": {
      "type": "account",
      "attributes": {
        "name": "Acme Corp",
        "domain": "acme.com"
      }
    }
  }'
```

### Add Prospect to Sequence
```bash
curl -X POST https://api.outreach.io/api/v2/sequenceStates \
  -H "Authorization: Bearer $OUTREACH_ACCESS_TOKEN" \
  -H "Content-Type: application/vnd.api+json" \
  -d '{
    "data": {
      "type": "sequenceState",
      "relationships": {
        "prospect": {"data": {"type": "prospect", "id": 1}},
        "sequence": {"data": {"type": "sequence", "id": 1}},
        "mailbox": {"data": {"type": "mailbox", "id": 1}}
      }
    }
  }'
```

### List Sequences
```bash
curl "https://api.outreach.io/api/v2/sequences" \
  -H "Authorization: Bearer $OUTREACH_ACCESS_TOKEN"
```

## Rate Limits
- **Standard:** 10,000 requests per hour
- **Burst:** Short-term limits apply
- Rate limit info in response headers
- HTTP 429 with `Retry-After` header when exceeded

## Gotchas
- **JSON:API spec** — must use `application/vnd.api+json` content type
- Data structure: `{"data": {"type": "...", "attributes": {...}, "relationships": {...}}}`
- OAuth only — no API keys for direct access
- Tokens expire in 2 hours, use refresh tokens
- Relationships are "to-one" writable (prospect→account), "to-many" are read-only
- SequenceState = prospect enrollment in a sequence
- Mailbox ID required when adding to sequences

## Links
- [Docs](https://developers.outreach.io/)
- [API Reference](https://developers.outreach.io/api/reference/overview/)
- [Common Patterns](https://developers.outreach.io/api/common-patterns/)
# Gong

Revenue intelligence platform for call recording, conversation analytics, and deal insights.

## Base URL
`https://api.gong.io/v2`

Note: Some instances use regional URLs like `https://us-12345.api.gong.io/v2`

## Authentication
OAuth 2.0 or Basic Auth with Access Key + Access Key Secret.

```bash
# Basic Auth (Access Key as username, Secret as password)
curl https://api.gong.io/v2/calls \
  -u "$GONG_ACCESS_KEY:$GONG_ACCESS_KEY_SECRET"

# OAuth Bearer token
curl https://api.gong.io/v2/calls \
  -H "Authorization: Bearer $GONG_ACCESS_TOKEN"
```

## Core Endpoints

### List Calls
```bash
curl -X POST https://api.gong.io/v2/calls/extensive \
  -u "$GONG_ACCESS_KEY:$GONG_ACCESS_KEY_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "fromDateTime": "2024-01-01T00:00:00Z",
      "toDateTime": "2024-03-01T00:00:00Z"
    },
    "contentSelector": {
      "exposedFields": {
        "content": {"brief": true}
      }
    }
  }'
```

### Get Call Transcript
```bash
curl -X POST https://api.gong.io/v2/calls/transcript \
  -u "$GONG_ACCESS_KEY:$GONG_ACCESS_KEY_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "callIds": ["1234567890"]
    }
  }'
```

### List Users
```bash
curl https://api.gong.io/v2/users \
  -u "$GONG_ACCESS_KEY:$GONG_ACCESS_KEY_SECRET"
```

### Get Stats
```bash
curl -X POST https://api.gong.io/v2/stats/activity/aggregate \
  -u "$GONG_ACCESS_KEY:$GONG_ACCESS_KEY_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "fromDateTime": "2024-01-01T00:00:00Z",
      "toDateTime": "2024-03-01T00:00:00Z"
    }
  }'
```

### List Deals
```bash
curl "https://api.gong.io/v2/deals?fromDateTime=2024-01-01T00:00:00Z" \
  -u "$GONG_ACCESS_KEY:$GONG_ACCESS_KEY_SECRET"
```

## Rate Limits
- **Standard:** 600 requests per minute per user
- **Bulk endpoints:** Lower limits, varies by endpoint
- Response headers include rate limit info
- HTTP 429 when exceeded

## Gotchas
- Access Keys are generated in Gong settings under Company Settings > API
- Most list endpoints use POST with filter body, not GET with query params
- `contentSelector` controls what fields are returned (can reduce response size)
- Call IDs are numeric strings, not integers
- Transcripts are separate from call metadata — need additional request
- DateTime filters use ISO 8601 format with timezone
- Some endpoints paginated via cursor in response

## Links
- [Docs](https://gong.io/api)
- [API Reference](https://gong.app.gong.io/settings/api/documentation)
- [Help Center](https://help.gong.io/)
