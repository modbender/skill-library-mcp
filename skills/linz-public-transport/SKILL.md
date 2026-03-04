---
name: linz-public-transport
description: Query Linz Linien raw EFA endpoints for stop lookup and live departures. Use when tasks involve Linz public transport stop search, resolving stop IDs from stop names, or fetching upcoming departures from a stop.
metadata: {"homepage":"https://docs.openclaw.ai/tools/skills","env":["LINZ_TRANSPORT_API_BASE_URL"],"network":"required","version":"1.0.1","notes":"Uses Linz EFA endpoints /efa/XML_STOPFINDER_REQUEST and /efa/XML_DM_REQUEST at default base http://www.linzag.at/linz2"}
---

# Linz Public Transport

Use this skill to interact with Linz Linien EFA endpoints:
- `GET /efa/XML_STOPFINDER_REQUEST`
- `GET /efa/XML_DM_REQUEST`

Read endpoint details in `{baseDir}/references/endpoints.md` before implementation.
Use `{baseDir}/scripts/linz_transport.py` as the default execution path.

## Workflow
1. Resolve the API base URL.
2. Run the script subcommand that matches the task.
3. Return a compact, user-facing summary.

## Primary Tooling
- Script path: `{baseDir}/scripts/linz_transport.py`
- Runtime: Python 3, standard library only.
- Base URL input:
  - `--base-url <url>` argument, or
  - `LINZ_TRANSPORT_API_BASE_URL` environment variable, or
  - default `http://www.linzag.at/linz2`.

Preferred commands:
- Search stops:
  - `python {baseDir}/scripts/linz_transport.py stops "taubenmarkt"`
- Fetch departures by stop ID:
  - `python {baseDir}/scripts/linz_transport.py departures --stop-id 60501160 --limit 10`
- Resolve stop and fetch departures in one call:
  - `python {baseDir}/scripts/linz_transport.py next "taubenmarkt" --limit 10 --pick-first`

## Step 1: Resolve Base URL
- Use user-provided base URL first.
- Otherwise use `LINZ_TRANSPORT_API_BASE_URL` if available.
- If neither exists, use `http://www.linzag.at/linz2`.

## Step 2: Present Output
- Sort by `countdownInMinutes` ascending if needed.
- Show the next 5-10 departures unless user asks for more.
- Include both relative (`countdownInMinutes`) and absolute (`time`) times.
- Keep field names stable when returning JSON.

## Error Handling
- If stop search returns empty list, suggest nearby spellings and retry with a shorter query token.
- If multiple stop matches are returned, rerun with explicit `--stop-id` or use `next ... --pick-first` only when ambiguity is acceptable.
- If departures response is empty, state that no upcoming departures are currently available.
- If HTTP request fails, report status code, endpoint, and retry guidance.
- If EFA response includes a `message` code, include that code in diagnostics.

## Minimal Examples

```bash
python {baseDir}/scripts/linz_transport.py stops "taubenmarkt"
python {baseDir}/scripts/linz_transport.py departures --stop-id 60501160 --limit 10
python {baseDir}/scripts/linz_transport.py next "taubenmarkt" --limit 10 --pick-first
```

```powershell
python "{baseDir}/scripts/linz_transport.py" stops "taubenmarkt"
python "{baseDir}/scripts/linz_transport.py" departures --stop-id 60501160 --limit 10
python "{baseDir}/scripts/linz_transport.py" next "taubenmarkt" --limit 10 --pick-first
```
