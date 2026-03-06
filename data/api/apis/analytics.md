# Index

| API | Line |
|-----|------|
| Mixpanel | 2 |
| Amplitude | 70 |
| PostHog | 135 |
| Segment | 213 |
| Sentry | 296 |
| Datadog | 361 |
| Algolia | 429 |

---

# Mixpanel

## Base URL
```
https://api.mixpanel.com
```

## Authentication
```bash
# Ingestion API (track events)
curl https://api.mixpanel.com/track \
  -d "data=$(echo '{"event":"test","properties":{"token":"YOUR_TOKEN"}}' | base64)"

# Export API
curl "https://data.mixpanel.com/api/2.0/export" \
  -u "$MIXPANEL_API_SECRET:"
```

## Track Event
```bash
curl -X POST https://api.mixpanel.com/track \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{
      "event": "Sign Up",
      "properties": {
        "token": "YOUR_PROJECT_TOKEN",
        "distinct_id": "user123",
        "plan": "premium"
      }
    }]
  }'
```

## Set User Profile
```bash
curl -X POST https://api.mixpanel.com/engage \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{
      "$token": "YOUR_PROJECT_TOKEN",
      "$distinct_id": "user123",
      "$set": {
        "$email": "user@example.com",
        "$name": "John Doe",
        "plan": "premium"
      }
    }]
  }'
```

## Query Events (JQL)
```bash
curl "https://mixpanel.com/api/2.0/jql" \
  -u "$MIXPANEL_API_SECRET:" \
  -d 'script=function main() { return Events({from_date:"2024-01-01",to_date:"2024-01-31"}).groupBy(["name"], mixpanel.reducer.count()) }'
```

## Common Traps

- Two tokens: Project Token (tracking), API Secret (querying)
- Events can be sent in batches (array)
- distinct_id must be consistent per user
- Properties starting with $ are reserved
- Rate limit: 2000 requests/minute

## Official Docs
https://developer.mixpanel.com/reference/overview
# Amplitude

## Base URLs
```
# HTTP API (tracking)
https://api2.amplitude.com

# Dashboard API (query)
https://amplitude.com/api/2
```

## Track Event
```bash
curl -X POST https://api2.amplitude.com/2/httpapi \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "$AMPLITUDE_API_KEY",
    "events": [{
      "user_id": "user123",
      "event_type": "Button Clicked",
      "event_properties": {
        "button_name": "signup"
      }
    }]
  }'
```

## Identify User
```bash
curl -X POST https://api2.amplitude.com/identify \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "$AMPLITUDE_API_KEY",
    "identification": [{
      "user_id": "user123",
      "user_properties": {
        "plan": "premium",
        "company": "Acme"
      }
    }]
  }'
```

## Query Events (Dashboard API)
```bash
curl "https://amplitude.com/api/2/events/segmentation?e={\"event_type\":\"Button Clicked\"}&start=20240101&end=20240131" \
  -u "$AMPLITUDE_API_KEY:$AMPLITUDE_SECRET_KEY"
```

## Export Raw Data
```bash
curl "https://amplitude.com/api/2/export?start=20240101T00&end=20240102T00" \
  -u "$AMPLITUDE_API_KEY:$AMPLITUDE_SECRET_KEY"
```

## Common Traps

- Two different APIs: HTTP (tracking) vs Dashboard (query)
- HTTP API uses api_key in body
- Dashboard API uses Basic Auth
- Batch up to 10 events per request
- Rate limit: 1000 events/second

## Official Docs
https://www.docs.developers.amplitude.com/analytics/apis/http-v2-api/
# PostHog

## Base URL
```
https://app.posthog.com/api  # Cloud
https://your-instance.com/api  # Self-hosted
```

## Authentication
```bash
curl https://app.posthog.com/api/projects/@current \
  -H "Authorization: Bearer $POSTHOG_API_KEY"
```

## Capture Event
```bash
curl -X POST https://app.posthog.com/capture \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "$POSTHOG_PROJECT_KEY",
    "event": "user_signed_up",
    "distinct_id": "user123",
    "properties": {
      "plan": "premium"
    }
  }'
```

## Identify User
```bash
curl -X POST https://app.posthog.com/capture \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "$POSTHOG_PROJECT_KEY",
    "event": "$identify",
    "distinct_id": "user123",
    "properties": {
      "$set": {
        "email": "user@example.com",
        "name": "John Doe"
      }
    }
  }'
```

## Query Events (HogQL)
```bash
curl -X POST "https://app.posthog.com/api/projects/@current/query" \
  -H "Authorization: Bearer $POSTHOG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "kind": "HogQLQuery",
      "query": "SELECT event, count() FROM events GROUP BY event"
    }
  }'
```

## Feature Flags
```bash
curl -X POST https://app.posthog.com/decide?v=3 \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "$POSTHOG_PROJECT_KEY",
    "distinct_id": "user123"
  }'
```

## Common Traps

- Two keys: Personal API key (reads), Project API key (events)
- Events use /capture endpoint (no auth header)
- $set for user properties, $ prefix is reserved
- HogQL for advanced queries
- Batch events for performance

## Official Docs
https://posthog.com/docs/api
# Segment

## Base URL
```
https://api.segment.io/v1
```

## Authentication
```bash
# Write Key as username, empty password
curl https://api.segment.io/v1/track \
  -u "$SEGMENT_WRITE_KEY:"
```

## Track Event
```bash
curl -X POST https://api.segment.io/v1/track \
  -u "$SEGMENT_WRITE_KEY:" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "event": "Order Completed",
    "properties": {
      "order_id": "12345",
      "total": 99.99
    }
  }'
```

## Identify User
```bash
curl -X POST https://api.segment.io/v1/identify \
  -u "$SEGMENT_WRITE_KEY:" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "traits": {
      "email": "user@example.com",
      "name": "John Doe",
      "plan": "premium"
    }
  }'
```

## Page View
```bash
curl -X POST https://api.segment.io/v1/page \
  -u "$SEGMENT_WRITE_KEY:" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "name": "Home",
    "properties": {
      "url": "https://example.com"
    }
  }'
```

## Group (Company)
```bash
curl -X POST https://api.segment.io/v1/group \
  -u "$SEGMENT_WRITE_KEY:" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "groupId": "company456",
    "traits": {
      "name": "Acme Inc",
      "plan": "enterprise"
    }
  }'
```

## Common Traps

- Write Key as Basic Auth username, empty password
- userId or anonymousId required
- Data routes to destinations configured in UI
- Batch endpoint for multiple events
- Rate limit: 500 requests/second

## Official Docs
https://segment.com/docs/connections/sources/catalog/libraries/server/http-api/
# Sentry

## Base URL
```
https://sentry.io/api/0
```

## Authentication
```bash
curl https://sentry.io/api/0/organizations/ \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN"
```

## List Projects
```bash
curl "https://sentry.io/api/0/organizations/$ORG_SLUG/projects/" \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN"
```

## List Issues
```bash
curl "https://sentry.io/api/0/projects/$ORG_SLUG/$PROJECT_SLUG/issues/?query=is:unresolved" \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN"
```

## Get Issue Details
```bash
curl "https://sentry.io/api/0/issues/$ISSUE_ID/" \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN"
```

## Get Issue Events
```bash
curl "https://sentry.io/api/0/issues/$ISSUE_ID/events/" \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN"
```

## Resolve Issue
```bash
curl -X PUT "https://sentry.io/api/0/issues/$ISSUE_ID/" \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'
```

## Query Search Syntax

| Query | Meaning |
|-------|---------|
| `is:unresolved` | Open issues |
| `is:resolved` | Resolved issues |
| `assigned:me` | Assigned to me |
| `level:error` | Error level |
| `browser:Chrome` | By browser |

## Common Traps

- Auth token from Settings > Auth Tokens
- Organization slug in URL (not name)
- Issues vs events: issue groups multiple events
- Pagination via Link header
- DSN for SDK, Auth Token for API

## Official Docs
https://docs.sentry.io/api/
# Datadog

## Base URLs
```
# US1
https://api.datadoghq.com

# EU
https://api.datadoghq.eu
```

## Authentication
```bash
curl "https://api.datadoghq.com/api/v1/validate" \
  -H "DD-API-KEY: $DD_API_KEY" \
  -H "DD-APPLICATION-KEY: $DD_APP_KEY"
```

## Submit Metrics
```bash
curl -X POST "https://api.datadoghq.com/api/v2/series" \
  -H "DD-API-KEY: $DD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "series": [{
      "metric": "my.metric",
      "type": 1,
      "points": [{"timestamp": 1704067200, "value": 42}],
      "tags": ["env:prod"]
    }]
  }'
```

## Query Metrics
```bash
curl "https://api.datadoghq.com/api/v1/query?from=1704067200&to=1704153600&query=avg:system.cpu.user{*}" \
  -H "DD-API-KEY: $DD_API_KEY" \
  -H "DD-APPLICATION-KEY: $DD_APP_KEY"
```

## Send Event
```bash
curl -X POST "https://api.datadoghq.com/api/v1/events" \
  -H "DD-API-KEY: $DD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Deployment completed",
    "text": "Version 1.2.3 deployed",
    "tags": ["env:prod", "service:api"]
  }'
```

## Get Monitors
```bash
curl "https://api.datadoghq.com/api/v1/monitor" \
  -H "DD-API-KEY: $DD_API_KEY" \
  -H "DD-APPLICATION-KEY: $DD_APP_KEY"
```

## Common Traps

- Two keys: API Key (write) + Application Key (read)
- Region determines base URL
- Timestamps in seconds (not ms)
- Metric type: 1=count, 2=rate, 3=gauge

## Official Docs
https://docs.datadoghq.com/api/latest/
# Algolia

## Base URL
```
https://{APPLICATION_ID}.algolia.net
```

## Authentication
```bash
curl "https://$ALGOLIA_APP_ID.algolia.net/1/indexes" \
  -H "X-Algolia-API-Key: $ALGOLIA_API_KEY" \
  -H "X-Algolia-Application-Id: $ALGOLIA_APP_ID"
```

## Search
```bash
curl -X POST "https://$ALGOLIA_APP_ID.algolia.net/1/indexes/$INDEX_NAME/query" \
  -H "X-Algolia-API-Key: $ALGOLIA_API_KEY" \
  -H "X-Algolia-Application-Id: $ALGOLIA_APP_ID" \
  -H "Content-Type: application/json" \
  -d '{"query": "search term", "hitsPerPage": 10}'
```

## Add/Update Object
```bash
curl -X PUT "https://$ALGOLIA_APP_ID.algolia.net/1/indexes/$INDEX_NAME/object123" \
  -H "X-Algolia-API-Key: $ALGOLIA_API_KEY" \
  -H "X-Algolia-Application-Id: $ALGOLIA_APP_ID" \
  -H "Content-Type: application/json" \
  -d '{"name": "Product", "price": 99}'
```

## Batch Operations
```bash
curl -X POST "https://$ALGOLIA_APP_ID.algolia.net/1/indexes/$INDEX_NAME/batch" \
  -H "X-Algolia-API-Key: $ALGOLIA_API_KEY" \
  -H "X-Algolia-Application-Id: $ALGOLIA_APP_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {"action": "addObject", "body": {"name": "Item 1"}},
      {"action": "addObject", "body": {"name": "Item 2"}}
    ]
  }'
```

## Delete Object
```bash
curl -X DELETE "https://$ALGOLIA_APP_ID.algolia.net/1/indexes/$INDEX_NAME/object123" \
  -H "X-Algolia-API-Key: $ALGOLIA_API_KEY" \
  -H "X-Algolia-Application-Id: $ALGOLIA_APP_ID"
```

## Common Traps

- App ID is part of the hostname
- Two API keys: Admin (write) and Search (read-only)
- objectID auto-generated if not provided
- Batch operations are atomic

## Official Docs
https://www.algolia.com/doc/rest-api/search/
