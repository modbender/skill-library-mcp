---
name: linkedin-connect
description: Send LinkedIn connection requests to a list of people via browser automation and track status in a CSV/TSV file. Use when the user wants to bulk-connect with a list of people on LinkedIn (founders, speakers, leads, etc.) from a spreadsheet or list containing LinkedIn profile URLs. Handles Connect button, Follow-mode profiles, already-connected detection, stale URL fallback via LinkedIn search and Google search, and incremental status tracking.
---

# LinkedIn Connect

Automates sending LinkedIn connection requests from a list and tracks results in a data file.

## ⚠️ Pre-flight Checklist — Confirm Before Starting

**Before doing anything else**, confirm all of the following with the user. Do not proceed until each item is confirmed.

### 1. Data File
Ask the user to provide their spreadsheet/CSV/TSV file and confirm it has (or can have) these columns:
- **Person/Founder Name** — full name of the person to connect with
- **Company/Brand Name** — their company or brand (used for search fallback)
- **LinkedIn Profile URL** — optional but highly recommended; reduces automation footprint

If the file lacks any column, tell the user which columns are missing and offer to add them.

### 2. Browser Setup
Ask which browser setup they're using:

**Option A — Chrome Browser Relay (recommended for accounts flagged for automation)**
- User must have the OpenClaw Browser Relay Chrome extension installed
- User opens LinkedIn in their regular Chrome browser and clicks the OpenClaw Relay toolbar icon on that tab (badge turns ON)
- Use `profile="chrome"` for all browser tool calls in this mode

**Option B — OpenClaw Isolated Browser (`openclaw` profile)**
- OpenClaw manages a separate Chrome instance
- On first use, navigate to `https://www.linkedin.com` and let the user log in; cookies persist across sessions
- Use `profile="openclaw"` for all browser tool calls in this mode

Confirm which option they've set up. Default to **Option A (Chrome Relay)** if the user's account has been flagged or warned about automation.

### 3. Ready Check
Only proceed once the user says:
- ✅ File is ready and accessible
- ✅ Browser is open with LinkedIn logged in (and relay is attached if Option A)

---

## Browser Profile

Set the `profile` variable based on user's choice in the Pre-flight Checklist:
- **Option A:** `profile="chrome"` — reuse the relay-attached tab; get `targetId` via `browser action=tabs`
- **Option B:** `profile="openclaw"` — OpenClaw-managed isolated Chrome instance

Do not mix profiles mid-run. Pick one and use it consistently for every browser tool call.

## Data File Setup

Ensure the tracking file has a `Connection Status` column. If missing, add it:

```python
import csv
rows = []
with open('file.tsv', 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    fieldnames = reader.fieldnames + ['Connection Status']
    rows = list(reader)
with open('file.tsv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    for row in rows:
        row['Connection Status'] = ''
        writer.writerow(row)
```

## Three-Tier Profile Discovery (Priority Order)

Always try in this order. Move to the next tier only if the current one fails.

### Tier 1 — Direct LinkedIn URL (fastest, zero ambiguity)
Navigate directly to the LinkedIn profile URL from the data file.
- ✅ URL loads → correct profile, proceed to connect
- ❌ Returns 404 → escalate to Tier 2
- Skip Tier 1 if no URL is in the data file for this person

### Tier 2 — Google Search (reliable fallback, preserves accuracy)
Search Google for `"Founder Name" "Brand/Company" linkedin`.
- Navigate to: `https://www.google.com/search?q=<Name>+<Company>+linkedin`
- Find the LinkedIn profile link in results (usually first result), click it
- Once on the profile, proceed to Connect step
- ⚠️ Only escalate to Tier 3 if Google can't find the right person or returns no LinkedIn result

### Tier 3 — LinkedIn People Search (last resort)
Run a LinkedIn people search for the founder + brand directly inside LinkedIn.
- Navigate to: `https://www.linkedin.com/search/results/people/?keywords=<Name>+<Company>`
- Look for inline `Connect` buttons first; otherwise open the profile from search results
- Confirm name + headline/company match before connecting
- ❌ No trustworthy match → mark `Profile Not Found`

See `references/browser-workflow.md` for detailed browser steps for each tier.

## Connecting on a Profile

Once on the correct profile, two patterns exist:

**Pattern A - Direct Connect button** visible on profile → click it → confirm dialog → `Send without a note`

**Pattern B - Follow mode** (no Connect button, only Follow + Message + More) → click `More actions` → use selector `.artdeco-dropdown__content--is-open` to get dropdown → click `Invite [Name] to connect` → confirm dialog → `Send without a note`

If neither Connect nor Invite is available → mark `Follow Only`.

## Status Values

| Status | Meaning |
|---|---|
| `Request Sent` | Connection request sent this session |
| `Already Connected` | 1st degree - no action needed |
| `Pending` | Request already sent previously |
| `Follow Only` | No Connect option available on this profile |
| `Profile Not Found` | All three tiers failed |
| `Skipped` | Intentionally skipped |

## Multi-founder Rows

When a TSV row has multiple founders, track per-founder status separated by ` | `:
```
Founder1Slug: Request Sent | Founder2Slug: Already Connected
```

## Rate Limiting & Anti-Detection

> ⚠️ LinkedIn flags accounts that jump directly between profile URLs. Always visit the feed between profiles — no exceptions.

- **Navigate to `/feed/` before every single profile**, without exception. See `references/browser-workflow.md` for the exact call. This is the primary anti-detection measure.
- Add a short natural pause (2–4 seconds) after loading the feed before navigating to the next profile.
- If >3 consecutive clean URLs return 404, pause for 10 seconds on the feed before continuing (then fall back to Google/LinkedIn search).
- Do not open new browser tabs — the relay breaks; reuse the same attached tab for every action.
- Aim for no more than 20–25 connection requests per session. Stop and tell the user if you're approaching this limit.

## Saving Progress

Use a `linkedin_progress.json` sidecar file:
```json
{ "statuses": { "https://www.linkedin.com/in/username/": "Request Sent" } }
```
Update the TSV from this dict every 10 profiles or at the end.

## References

- `references/browser-workflow.md` - Detailed browser steps for all three tiers and both connect patterns
