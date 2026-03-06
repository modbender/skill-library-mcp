# ScrapeSense Endpoint Map (v1)

## Health
- `GET /status`

## Scans
- `GET, POST /scans`
- `GET, DELETE /scans/{id}`
- `GET /scans/{id}/tiles`
- `POST /scans/{id}/pause`
- `POST /scans/{id}/resume`
- `POST /scans/{id}/cancel`
- `GET /scans/{id}/places`

## Places
- `GET /places/{id}`

## Jobs
- `GET /jobs`
- `GET /jobs/{id}`
- `POST /jobs/{id}/cancel`

## Campaigns
- `GET, POST /campaigns`
- `POST /campaigns/create`
- `GET /campaigns/stats/summary`
- `GET, DELETE /campaigns/{id}`
- `GET /campaigns/{id}/emails`
- `GET, PUT, DELETE /campaigns/{id}/emails/{emailId}`
- `POST /campaigns/{id}/emails/{emailId}/approve`
- `POST /campaigns/{id}/emails/{emailId}/send`
- `POST /campaigns/{id}/start`
- `POST /campaigns/{id}/pause`
- `POST /campaigns/{id}/resume`
- `POST /campaigns/{id}/cancel`
- `POST /campaigns/{id}/remove-unsent`
- `POST /campaigns/{id}/remove-invalid`
- `POST /campaigns/{id}/complete`
- `PUT /campaigns/{id}/prompt`
- `PUT /campaigns/{id}/settings`
- `POST /campaigns/{id}/approve-all`
- `POST /campaigns/{id}/send-all-approved`
- `POST /campaigns/{id}/approve-and-send-all`
- `POST /campaigns/{id}/generate-emails`
- `POST /campaigns/{id}/emails/{emailId}/regenerate`
- `POST /campaigns/{id}/regenerate-all`
- `POST /campaigns/{id}/retry-failed`
- `DELETE /campaigns/{id}/places/{placeId}`
- `POST /campaigns/{id}/test-prompt`
- `POST /campaigns/{id}/preview`

## Billing
- `GET /billing/credits`
- `GET /billing/transactions`
- `GET /billing/spend`
- `GET, PUT /billing/settings`

## Developer API Keys
- `GET, POST /developer/keys`
- `PATCH, DELETE /developer/keys/{id}`
- `GET /developer/keys/{id}/usage`

## Developer Webhooks
- `GET /developer/webhooks/events`
- `GET, POST /developer/webhooks`
- `PATCH, DELETE /developer/webhooks/{id}`
- `POST /developer/webhooks/{id}/test`
- `GET /developer/webhooks/{id}/deliveries`
- `POST /developer/webhooks/deliveries/{deliveryId}/retry`

## Reliability
- `GET /analytics/scraper-reliability`
