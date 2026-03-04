# Testing Guide — pager-triage

**Version:** 0.1.1
**Last updated:** 2026-02-16

---

## 1. Smoke Tests (No API Key Required)

These tests verify the tool loads, parses arguments, and handles missing configuration gracefully. They require no PagerDuty account.

### Run the automated smoke test

```bash
./scripts/smoke.sh
```

### Manual smoke tests

#### T-SMOKE-1: Help output
```bash
./scripts/pager-triage.sh help
```
**Expected:** Usage text listing all 8 subcommands. Exit code 0.

#### T-SMOKE-2: No arguments
```bash
./scripts/pager-triage.sh
```
**Expected:** Usage text on stderr. Exit code 1.

#### T-SMOKE-3: Unknown subcommand
```bash
./scripts/pager-triage.sh foobar
```
**Expected:** JSON error `{"error": "Unknown subcommand: foobar..."}` on stderr. Exit code 1.

#### T-SMOKE-4: Missing API key
```bash
unset PAGERDUTY_API_KEY
./scripts/pager-triage.sh incidents
```
**Expected:** JSON error mentioning `PAGERDUTY_API_KEY` with setup instructions. Exit code 1.

#### T-SMOKE-5: Missing email for write ops
```bash
export PAGERDUTY_API_KEY="test_key"
unset PAGERDUTY_EMAIL
./scripts/pager-triage.sh ack P123ABC --confirm
```
**Expected:** JSON error mentioning `PAGERDUTY_EMAIL`. Exit code 1. No API call attempted.

#### T-SMOKE-6: Confirmation gate — ack without --confirm
```bash
export PAGERDUTY_API_KEY="test_key"
export PAGERDUTY_EMAIL="test@example.com"
./scripts/pager-triage.sh ack P123ABC
```
**Expected:** JSON with `"error": "confirmation_required"` on stderr. Exit code 1. Should attempt to fetch incident details (will fail with invalid key, but that's expected in smoke tests).

#### T-SMOKE-7: Invalid incident ID format
```bash
export PAGERDUTY_API_KEY="test_key"
./scripts/pager-triage.sh detail "../../etc/passwd"
```
**Expected:** JSON error `"Invalid incident ID format"`. Exit code 1. No API call made.

#### T-SMOKE-8: Invalid incident ID — special characters
```bash
export PAGERDUTY_API_KEY="test_key"
./scripts/pager-triage.sh detail "P123;rm -rf /"
```
**Expected:** JSON error `"Invalid incident ID format"`. Exit code 1.

#### T-SMOKE-9: Dependency check
```bash
# Verify curl and jq are required
which curl jq
```
**Expected:** Both found. If either is missing, the script will error with a clear dependency message.

---

## 2. Integration Tests (Real PagerDuty Account)

These tests require a PagerDuty account with:
- A valid REST API v2 key (full access for write tests, read-only for read tests)
- At least one service configured
- `PAGERDUTY_EMAIL` set to a valid PagerDuty user email

### Setup

```bash
export PAGERDUTY_API_KEY="u+real_key_here"
export PAGERDUTY_EMAIL="you@company.com"
```

### T-INT-1: List incidents
```bash
./scripts/pager-triage.sh incidents
```
**Verify:**
- Output is valid JSON (`| jq .`)
- `tool` field equals `"pd_incidents"`
- `total_incidents` is an integer
- `incidents` is an array (may be empty)
- If incidents exist: each has `id`, `title`, `status`, `urgency`

### T-INT-2: Incident detail
```bash
# Use an incident ID from T-INT-1, or create a test incident first
./scripts/pager-triage.sh detail <INCIDENT_ID>
```
**Verify:**
- Output is valid JSON
- `tool` field equals `"pd_incident_detail"`
- `incident` object has `id`, `title`, `status`, `urgency`, `service`
- `timeline` is an array, chronologically ordered
- `alerts` is an array
- `notes` is an array
- `analysis` object has `alert_count`, `acknowledged`, `trigger_source`

### T-INT-3: On-call schedules
```bash
./scripts/pager-triage.sh oncall
```
**Verify:**
- Valid JSON with `tool: "pd_oncall"`
- `oncalls` is an array
- Each entry has `user.name`, `schedule.name`, `escalation_level`

### T-INT-4: List services
```bash
./scripts/pager-triage.sh services
```
**Verify:**
- Valid JSON with `tool: "pd_services"`
- `services` is an array (non-empty if you have services configured)
- Each has `id`, `name`, `status`

### T-INT-5: Recent incidents
```bash
./scripts/pager-triage.sh recent --since 7d
```
**Verify:**
- Valid JSON with `tool: "pd_recent"`
- `period` equals `"last 7 days"`
- `stats.total` matches `incidents` array length
- `stats.by_urgency` and `stats.by_status` are objects

### T-INT-6: Full write workflow

> ⚠️ This test creates real state changes in PagerDuty. Use a test service/incident.

```bash
# Step 1: Create a test incident via PagerDuty API or UI

# Step 2: Verify it appears
./scripts/pager-triage.sh incidents

# Step 3: Get details
./scripts/pager-triage.sh detail <INCIDENT_ID>

# Step 4: Acknowledge
./scripts/pager-triage.sh ack <INCIDENT_ID> --confirm
# Verify: status is "acknowledged"

# Step 5: Add note
./scripts/pager-triage.sh note <INCIDENT_ID> --content "Integration test note" --confirm
# Verify: note_id is returned, content matches

# Step 6: Resolve
./scripts/pager-triage.sh resolve <INCIDENT_ID> --confirm
# Verify: status is "resolved"

# Step 7: Verify in history
./scripts/pager-triage.sh recent --since 24h
# Verify: resolved incident appears in list
```

---

## 3. Edge Cases

### E-1: Expired / Revoked API Token
```bash
export PAGERDUTY_API_KEY="u+expired_key_here"
./scripts/pager-triage.sh incidents
```
**Expected:** JSON error mentioning "Invalid PAGERDUTY_API_KEY" with masked key (`****<last4>`). No stack trace.

### E-2: Rate Limiting
PagerDuty allows 960 requests/minute. Under normal use this is unreachable, but:
```bash
# Simulate by running many requests rapidly
for i in $(seq 1 100); do
  ./scripts/pager-triage.sh incidents &
done
wait
```
**Expected:** If 429 is hit, clean JSON error: "PagerDuty rate limit hit (HTTP 429). Wait 30 seconds and retry."

### E-3: Empty Incident List
```bash
# When no active incidents exist
./scripts/pager-triage.sh incidents
```
**Expected:** Valid JSON with `"total_incidents": 0`, `"incidents": []`, and a summary like "0 active incident(s)". **Not** an error.

### E-4: Malformed Incident ID
```bash
./scripts/pager-triage.sh detail ""
```
**Expected:** JSON error: "Usage: pager-triage detail <incident_id>"

```bash
./scripts/pager-triage.sh detail "DOESNOTEXIST99"
```
**Expected:** PagerDuty returns 404. Tool should handle gracefully (may vary — PD might return 404 or a not-found error in the response body).

### E-5: Non-existent Service ID
```bash
./scripts/pager-triage.sh recent --service NONEXISTENT
```
**Expected:** Either empty results or a PagerDuty error handled gracefully.

### E-6: Network Timeout
```bash
# Simulate by pointing to a non-routable address (don't actually do this in CI)
# The script has a 10-second curl timeout. After 1 retry with 2s backoff,
# it should output: "PagerDuty API is unreachable."
```
**Expected:** After ~24 seconds (10s timeout × 2 attempts + 2s backoff), JSON error about API being unreachable.

### E-7: Write operation with read-only key
```bash
# Using a read-only API key:
./scripts/pager-triage.sh ack <INCIDENT_ID> --confirm
```
**Expected:** JSON error mentioning HTTP 403 and insufficient permissions.

### E-8: Note with empty content
```bash
./scripts/pager-triage.sh note P123ABC --content "" --confirm
```
**Expected:** JSON error: "Note content is required."

---

## 4. Output Schema Validation

For any subcommand, the output should always be valid JSON. Quick validation:

```bash
./scripts/pager-triage.sh <subcommand> [args] | jq . > /dev/null
echo "Exit code: $?"
```

Exit code 0 means valid JSON. Any non-zero means the output wasn't parseable.

### Key schema invariants
- All timestamps are ISO 8601 format
- `total_incidents` / `stats.total` are integers
- `incidents`, `oncalls`, `services`, `timeline`, `alerts`, `notes` are always arrays (never null)
- `status` values are from the set: `triggered`, `acknowledged`, `resolved`
- `urgency` values are from the set: `high`, `low`
- Error output goes to stderr; success output goes to stdout

---

<sub>Testing documentation for pager-triage v0.1.1 · [Anvil AI](https://anvil-ai.io)</sub>
