# ScrapeSense Developer Capabilities

## Scope
This reference captures the practical capability surface from the ScrapeSense developer portal + API spec and maps it to reliable execution patterns.

## 1) Scan Orchestration
- Create scans (`POST /scans`) with bounds/keywords/depth/zoom.
- Monitor scans (`GET /scans/:id`) and tile progress (`GET /scans/:id/tiles`).
- Control running scans (`pause`, `resume`, `cancel`).
- Retrieve scan places (`GET /scans/:id/places`).

### Coastal-city guidance
For coastal geographies, trim water-heavy bounds before deep scans to avoid wasted tiles/credits.

## 2) Places Data
- Read place payloads from scan results.
- Fetch individual place details (`GET /places/:id`).
- Use place-level fields for campaign filtering and dedup.

## 3) Campaign Lifecycle
- Create/list campaigns and campaign stats.
- Manage campaign state: start/pause/resume/cancel/complete.
- Generate AI emails, review/edit, regenerate one/all, retry failed sends.
- Approve/send per-email or bulk (`approve-all`, `send-all-approved`, combined approve+send).

### Mandatory pre-send hygiene
Before any large send flow, run email cleaning (preview/apply) when available in workflow.

## 4) Billing & Credits
- Credits balance, transactions, spend, settings.
- Cost-per-place/cost-per-email values must align across backend/frontend/worker runtime env.

## 5) Developer Surface
- API key lifecycle (create/list/revoke/patch/usage).
- Webhook subscriptions + events/deliveries + retry delivery.

## 6) Reliability & Monitoring
- Use reliability analytics endpoint for scraper health trend checks.
