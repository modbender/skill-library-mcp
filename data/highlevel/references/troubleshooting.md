# Troubleshooting Reference

## Common Errors

| HTTP Code | Cause | Fix |
|-----------|-------|-----|
| 401 | Invalid/expired token | Regenerate token via Settings → Private Integrations |
| 401 | Missing Version header | Add `Version: 2021-07-28` to all requests |
| 403 | Missing scope | Edit integration → enable required scopes → rotate token |
| 404 | Invalid endpoint or ID | Verify path and resource IDs |
| 422 | Validation error | Check required fields (locationId, etc.) |
| 429 | Rate limited | Wait and retry with exponential backoff |
| 500+ | GHL server error | Retry after 2-5 seconds |

## Environment Variable Checklist
```bash
# Both must be set:
echo $HIGHLEVEL_TOKEN      # Should show your private integration token
echo $HIGHLEVEL_LOCATION_ID # Should show your location ID

# Test GET — Retrieve location:
curl -s --request GET \
  --url "https://services.leadconnectorhq.com/locations/$HIGHLEVEL_LOCATION_ID" \
  --header "Accept: application/json" \
  --header "Authorization: Bearer $HIGHLEVEL_TOKEN" \
  --header "Version: 2021-07-28" | head -c 200

# Test POST — Create a contact:
curl --request POST \
  --url https://services.leadconnectorhq.com/contacts/ \
  --header "Authorization: Bearer $HIGHLEVEL_TOKEN" \
  --header "Content-Type: application/json" \
  --header "Version: 2021-07-28" \
  --data '{"firstName":"Test","lastName":"User","email":"test@example.com","locationId":"'$HIGHLEVEL_LOCATION_ID'"}'
```

## OAuth Token Lifecycle (Marketplace Apps Only)
- Access tokens expire in **24 hours** (86,399 seconds)
- Refresh tokens last up to **1 year**
- Private Integration tokens do NOT expire (but 90-day rotation recommended)
- `/oauth/token` is the ONLY endpoint that does NOT require the `Version` header

## Rate Limits

**Burst**: 100 requests per 10 seconds per app per resource
**Daily**: 200,000 requests per day per app per resource
**SaaS endpoints**: 10 requests per second (global)

Rate limits are **per-resource** — if an app is installed on Sub-account A and Sub-account B, each sub-account independently gets its own 100/10s and 200K/day allocation.

**Monitor via response headers**:
- `X-RateLimit-Limit-Daily` — Daily limit
- `X-RateLimit-Daily-Remaining` — Remaining daily
- `X-RateLimit-Max` — Burst max
- `X-RateLimit-Remaining` — Remaining burst
- `X-RateLimit-Interval-Milliseconds` — Reset interval

## Token Rotation

Tokens don't auto-expire, but GHL recommends rotating every 90 days. Unused tokens expire after 90 days inactivity.

**To rotate**: Settings → Private Integrations → click integration → Rotate Token

Two methods:
- **"Rotate and expire later"** — generates new token, old stays active for **7-day grace period**. You can cancel rotation or force immediate expiry during this window
- **"Rotate and expire now"** — immediately invalidates old token (use for compromised credentials)

You can edit name, description, and scopes **without generating a new token**. Permission to manage Private Integrations can be restricted per user at Settings → Team → Edit user → Roles & Permissions.

## Pagination

**Default**: 20 records per request, max 100 via `limit` parameter
**Cursor-based**: Use `startAfter` / `startAfterId` from previous response

```python
# Paginate through all contacts
all_contacts = []
start_after = None
while True:
    params = f"locationId={LOC_ID}&limit=100"
    if start_after:
        params += f"&startAfterId={start_after}"
    result = _get(f"/contacts/?{params}")
    contacts = result.get("contacts", [])
    all_contacts.extend(contacts)
    if len(contacts) < 100:
        break
    start_after = contacts[-1]["id"]
```

## Webhook Debugging

50+ event types available. Webhooks fire regardless of token expiry.
Webhook config is per marketplace app, not per private integration.

**Key webhook events:**
- Contact: `ContactCreate`, `ContactDelete`, `ContactDndUpdate`, `ContactTagUpdate`
- Conversation: `InboundMessage`, `OutboundMessage`, `ConversationUnreadUpdate`
- Opportunity: `OpportunityCreate`, `OpportunityStageUpdate`, `OpportunityStatusUpdate`, `OpportunityDelete`
- Appointment: `AppointmentCreate`, `AppointmentUpdate`, `AppointmentDelete`
- Payment: `InvoiceSent`, `InvoicePaid`, `PaymentReceived`
- Forms: `FormSubmission`, `SurveySubmission`
- Location: `LocationCreate`, `LocationUpdate`

Docs: https://marketplace.gohighlevel.com/docs/webhook/WebhookIntegrationGuide

## Official Resources
- **API Docs**: https://marketplace.gohighlevel.com/docs/
- **OpenAPI Specs**: https://github.com/GoHighLevel/highlevel-api-docs
- **Setup Video**: https://youtu.be/ssDO6tz6b1w
- **Developer Slack**: https://developers.gohighlevel.com/join-dev-community
