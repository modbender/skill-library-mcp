# Security Notes — ns-trains

This skill calls the official **NS (Nederlandse Spoorwegen) API** to retrieve public travel information (journeys, departures, arrivals, disruptions, station lookup).

## Secrets

- Uses a single secret: `NS_SUBSCRIPTION_KEY` (read from the environment).
- The subscription key is only used to set the HTTP header:
  - `Ocp-Apim-Subscription-Key: <subscription key>`
- The code **does not print** the subscription key and should never log it.

## Network Egress Controls

All HTTP requests go through `scripts/ns-api.mjs` (`nsFetch()`), which enforces:

- **HTTPS only** (refuses non-HTTPS URLs)
- **Host allowlist**: only requests to the NS API gateway are permitted:
  - `gateway.apiportal.ns.nl`

If a URL is not allowlisted, the request is rejected.

## Endpoints Used

Hardcoded endpoints (all under `https://gateway.apiportal.ns.nl/`):

- `/reisinformatie-api/api/v2/stations`
- `/reisinformatie-api/api/v2/arrivals`
- `/reisinformatie-api/api/v2/departures`
- `/reisinformatie-api/api/v3/trips`
- `/reisinformatie-api/api/v3/disruptions`

## Data Handling

- Reads only from environment variables and NS API responses.
- Does not write files, modify system settings, or execute shell commands.
- Outputs results to stdout (times, platforms, disruptions, etc.).

## Operational Guidance

- Treat `NS_SUBSCRIPTION_KEY` as a secret (do not commit, paste, or share).
- Prefer injecting the key via runtime secrets (container env, secret manager) rather than shell profile files.
- If you suspect key exposure, rotate it in the NS API portal.
