# Session Startup & Heartbeat Protocol

## Session Startup Flow (Every New Session)

### Step 1: Run Dashboard Check

```bash
cd <SKILL_DIR> && python scripts/check_status.py --auto-e2ee
```

### Step 2: Parse Status → Decide Next Action

| Status Condition | Recommended Action |
|-----------------|-------------------|
| `identity.status == "no_identity"` | Guide identity creation: `setup_identity.py --name "<name>"` |
| `identity.status == "no_jwt"` | Run `setup_identity.py --load default` to refresh JWT |
| `identity.status == "jwt_refresh_failed"` | Inform the user refresh failed; suggest deleting credentials and recreating |
| `inbox.text_messages > 0` | Display message summary; prompt user to review |
| `inbox.has_pending_handshakes == true` | Inform the user of pending E2EE handshake requests (already handled by --auto-e2ee) |
| `e2ee_auto.processed > 0` | Report auto-processing results |
| All normal | "DID identity OK, no unread messages." |

### Step 3: Report Summary (Format)

```
DID identity status: [name] ([DID abbreviated]) - JWT valid/refreshed
Inbox: [N] unread messages
  - [sender]: [count] messages (latest: [time])
E2EE: [active] active / [pending] handshaking
```

If E2EE auto-processing occurred:
```
E2EE auto-processing: automatically accepted encrypted communication request from [DID]
```

### Step 4: Check Profile Completeness

If the user hasn't set up their Profile (`get_profile.py` returns empty or missing nickname/bio), suggest at an appropriate time:
> "Consider completing your Profile — see template: `<SKILL_DIR>/references/PROFILE_TEMPLATE.md`"

Set up incrementally via `update_profile.py`: `--nick-name` / `--bio` / `--tags` / `--profile-md`.

## Heartbeat Check (Every 15 Minutes)

### Trigger Condition

When more than 15 minutes have passed since the last `check_status.py` execution, and the user sends a new message — run the check before processing the user's request.

### State Tracking

The Agent should maintain in memory:
- `last_did_check_at`: ISO timestamp of the last check
- `consecutive_failures`: consecutive failure count

### Silent Judgment Rules

Only notify the user when any of the following are true; otherwise, remain completely silent:
- `inbox.text_messages > 0`
- `e2ee_auto.processed > 0`
- `identity.jwt_refreshed == true`
- `identity.status != "ok"`

### Backoff Strategy

- Success: reset failures to zero
- 1-2 failures: retry normally
- >= 3 failures: pause automatic heartbeat; inform the user
- After user confirmation: reset failures; resume heartbeat

## E2EE Auto-Processing Strategy

**Auto-process (no confirmation needed):**
- `e2ee_hello` → auto-reply to handshake
- `e2ee_finished` → auto-activate session
- `e2ee_error` → log the error

**Notify user:**
- "Automatically accepted encrypted communication request from [DID]"
- "E2EE channel with [DID] has been established"

**Do not auto-execute (requires user instruction):**
- Initiating handshakes, sending encrypted messages, decrypting messages

**Design rationale:** The E2EE protocol has no rejection mechanism, and handshake messages expire after 5 minutes. Auto-accepting avoids timeouts; notifying the user maintains transparency.

## check_status.py Output Field Reference

| Field Path | Type | Description |
|-----------|------|-------------|
| `timestamp` | string | UTC ISO timestamp |
| `identity.status` | string | `"ok"` / `"no_identity"` / `"no_jwt"` / `"jwt_refresh_failed"` |
| `identity.did` | string\|null | DID identifier |
| `identity.name` | string\|null | Identity name |
| `identity.jwt_valid` | bool | Whether JWT is valid |
| `identity.jwt_refreshed` | bool | Whether JWT was refreshed this time (only present on refresh) |
| `identity.error` | string | Error description (only present on jwt_refresh_failed) |
| `inbox.status` | string | `"ok"` / `"no_identity"` / `"error"` / `"skipped"` |
| `inbox.total` | int | Total inbox message count |
| `inbox.text_messages` | int | Plain text unread count (excluding E2EE protocol messages) |
| `inbox.text_by_sender` | object | `{did: {count: int, latest: string}}` |
| `inbox.has_pending_handshakes` | bool | Whether there are pending E2EE handshakes |
| `inbox.e2ee_handshake_pending` | list | List of DIDs that initiated handshakes |
| `inbox.e2ee_encrypted_from` | list | List of DIDs that sent encrypted messages |
| `inbox.by_type` | object | Count by message type `{type: count}` |
| `e2ee_auto.status` | string | `"ok"` / `"no_identity"` / `"error"` (only with --auto-e2ee) |
| `e2ee_auto.processed` | int | Number auto-processed this time (only with --auto-e2ee) |
| `e2ee_auto.details` | list | Processing details (only with --auto-e2ee) |
| `e2ee_auto.error` | string | Error description (only when status is error) |
| `e2ee_sessions.active` | int | Active E2EE session count |
| `e2ee_sessions.pending` | int | Handshaking E2EE session count |
