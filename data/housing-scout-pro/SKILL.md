---
name: housing-scout
description: Find and monitor housing listings (buy/rent), apply practical filters, and manage subscription-style alerts in any supported region. Use when the user asks to search homes, compare candidates, run comps, or set listing notifications.
user-invocable: true
command-dispatch: tool
command-tool: exec
---

# Housing Scout

This skill is self-contained for ClawHub publish. All commands run against the bundled runtime under `./scripts/housing_scout/`.

## Quickstart (recommended)

- Create a profile and run first search immediately:
  - `node ./scripts/housing_scout/housing_scout.mjs quickstart --name "great nyc area" --city "New York" --state "NY" --beds-min 3 --budget-max 2000000 --run true`

## Direct search (no profile required)

- Buy:
  - `node ./scripts/housing_scout/housing_scout.mjs search --intent buy --city "Seattle" --state "WA" --beds-min 3 --budget-max 1200000`
- Rent:
  - `node ./scripts/housing_scout/housing_scout.mjs search --intent rent --city "Seattle" --state "WA" --beds-min 2 --budget-max 4500`

## Profile workflow

- Create:
  - `node ./scripts/housing_scout/housing_scout.mjs create_profile --name "great new york city area" --city "New York" --state "NY" --country "US" --beds-min 3 --budget-max 2000000`
- List:
  - `node ./scripts/housing_scout/housing_scout.mjs list_profiles`
- Show:
  - `node ./scripts/housing_scout/housing_scout.mjs show_profile --name "great new york city area"`
- Delete:
  - `node ./scripts/housing_scout/housing_scout.mjs delete_profile --name "great new york city area"`
- Use profile:
  - `node ./scripts/housing_scout/housing_scout.mjs search --profile "great new york city area" --intent buy`
  - `node ./scripts/housing_scout/housing_scout.mjs search --profile "great new york city area" --intent rent`

## Provider cache operations

- Status:
  - `node ./scripts/housing_scout/housing_scout.mjs provider_cache_status --provider zillow --intent buy`
- Refresh:
  - `node ./scripts/housing_scout/housing_scout.mjs refresh_provider_cache --provider zillow --intent buy --from ./tmp/zillow_buy.json`

## Other useful commands

- Lease flow:
  - `node ./scripts/housing_scout/housing_scout.mjs lease --profile "great new york city area"`
- Comps from Redfin URL:
  - `node ./scripts/housing_scout/housing_scout.mjs comps --query south-bay-buy-default --redfin-url "https://www.redfin.com/..."`
- Subscriptions:
  - `node ./scripts/housing_scout/housing_scout.mjs subscribe --query south-bay-buy-default --channel telegram --to YOUR_CHAT_ID`
  - `node ./scripts/housing_scout/housing_scout.mjs unsubscribe --query south-bay-buy-default`
  - `node ./scripts/housing_scout/housing_scout.mjs unsubscribe --subscription-id sub-...`
  - `node ./scripts/housing_scout/housing_scout.mjs list_subscriptions`
  - `node ./scripts/housing_scout/housing_scout.mjs run_subscriptions`

## Optional preset example

- The built-in South Bay preset is only for demo/smoke test:
  - `node ./scripts/housing_scout/housing_scout.mjs search --query south-bay-buy-default`

## Notes

- Multi-provider selector: `--providers redfin,zillow,realtor`.
- Provider status:
  - Redfin: live feed/caches
  - Zillow: live-cache adapter (`live_zillow_buy.json` / `live_zillow_rent.json`)
  - Realtor: live-cache adapter (`live_realtor_buy.json` / `live_realtor_rent.json`)
- `refresh_provider_cache` input shape:
  - `{ "listings": [ { "address"|"street/city/state/zip", "url", "price"|"rent", "beds", "baths", "sqft", "homeType" } ] }`

## Security + data egress notes (important)

- Redfin fetch path uses `https://r.jina.ai/http/...` in this runtime. This is a third-party fetch proxy.
- Any URL supplied via Redfin/city endpoint flows may be requested through that proxy and fetched content is returned into the tool pipeline.
- Never pass private/internal URLs (for example: `localhost`, `127.0.0.1`, `10.x.x.x`, `172.16-31.x.x`, `192.168.x.x`, link-local, intranet hostnames, cloud metadata endpoints).
- Only use public real-estate pages you are comfortable sharing with an external fetch service.
- Subscriptions/notifications can send data outside the runtime (`channel` + `to`). Verify recipients before enabling.

## Notifications setup (Telegram)

- This skill does **not** store bot tokens in skill files.
- Configure Telegram credentials in OpenClaw Gateway/channel config or environment variables.
- `subscribe` stores destination metadata (`channel`, `to`) in local skill state.
- `run_subscriptions` emits `NOTIFY_PAYLOAD` JSON; delivery is performed by assistant/gateway messaging.

## Local persistence + cleanup

- The skill writes state under `./scripts/housing_scout/data/` (profiles, queries, subscriptions, snapshots, caches).
- Keep this directory scoped to the skill workspace; do not point commands at unrelated sensitive files.
- Remove active outbound targets when no longer needed:
  - `node ./scripts/housing_scout/housing_scout.mjs unsubscribe --query <queryId>`
  - `node ./scripts/housing_scout/housing_scout.mjs unsubscribe --subscription-id <subId>`
- Remove unused profiles:
  - `node ./scripts/housing_scout/housing_scout.mjs delete_profile --name "<profile>"`
- If you need a hard reset, manually clear JSON state files under `./scripts/housing_scout/data/`.

## Privacy/safety checklist

- Replace `YOUR_CHAT_ID` with your own approved target.
- Do not commit personal chat IDs, tokens, or private channels.
- Keep credentials outside skill files (env vars or gateway config).
- Review and prune subscriptions/caches periodically.