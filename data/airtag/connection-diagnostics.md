# Connection Diagnostics - AirTag

Use this playbook when account-level access fails before or during recovery.

## A) Connector Health Triage

Classify failures first:

1. **Connector failure**: no usable data path (permissions, auth, tooling, session).
2. **Find My failure**: connector works, but location data is stale/missing.
3. **AirTag state failure**: account is healthy, specific tag has battery/pairing/range issues.

Only move to AirTag resets after connector and account checks pass.

## B) Direct App Control Checks (macOS)

1. Confirm Find My.app opens and shows items.
2. Confirm automation tool can read/click the app window.
3. Re-grant permissions if commands fail silently.
4. Re-test with one simple action before full locate workflow.

Escalate when:
- App is visible but automation cannot interact after permission reset.
- Item list appears inconsistent with account expectations.

## C) API Mode Checks (`findmy`)

1. Confirm the user-managed connector is reachable and authenticated.
2. Confirm read-only location fetch works for at least one known item.
3. If auth fails, stop and ask user to refresh connector credentials outside this skill.
4. Resume incident actions only after a successful read-only fetch.

Escalate when:
- Repeated auth/session errors persist across a clean environment.
- Reports run but return no item set while Find My app clearly has items.

## D) Pairing and Reconnect Flow

Use only after connector and account path are healthy:

1. Confirm which specific tag is affected.
2. Check battery and last-seen behavior.
3. Validate Bluetooth/location settings and nearby detection behavior.
4. Apply one change at a time and verify map + ring behavior after each.
5. Log the exact point of recovery or failure in incident notes.

## E) Fast Resolution Ladder

1. Restore connector path.
2. Validate account item visibility.
3. Run locate workflow from `recovery-playbook.md`.
4. Apply tag-level diagnostics (battery/pairing) only if locate still fails.
5. For unknown tracking alerts, switch immediately to `anti-stalking-safety.md`.
