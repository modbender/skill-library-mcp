# Recovery Playbook - AirTag

Use this map to select the shortest safe recovery path.

## Preflight: Confirm Account Access Path

Before running any scenario:
1. Confirm which connector mode is active (Direct App Control, API Mode, or Shared Link Mode).
2. Validate that the selected connector can see the target item.
3. If connector visibility fails, switch to `connection-diagnostics.md` first.

## 1) Nearby but Not Found

Signals:
- AirTag appears online
- Last seen is current location or very recent
- User cannot physically locate the item

Actions:
1. Trigger sound first, then walk in quiet arcs.
2. Re-check volume blockers (bag padding, drawers, dense fabric).
3. If iPhone supports Precision Finding, use directional flow and pause every few meters.
4. Validate item attachment point (ring, clip, pocket seam) before deeper reset steps.

Exit condition:
- Item found or clear evidence that last-seen location changed.

## 2) Stale Last Location

Signals:
- Map shows old timestamp
- AirTag appears unreachable

Actions:
1. Confirm iPhone connectivity basics (Bluetooth, location services, network path).
2. Verify Find My settings and background app refresh are active.
3. Ask whether the tagged item may still be in low-traffic zones where no Apple device passed nearby.
4. Define next checkpoint time and place to re-scan, then avoid repeated blind refresh loops.

Exit condition:
- New location update appears or scenario reclassified as unknown location.

## 3) Unknown Location

Signals:
- No usable current signal
- Last-known point does not match likely path

Actions:
1. Build a timeline with the user: last confirmed possession, transit mode, probable handoff points.
2. Prioritize high-probability checkpoints over random sweeps.
3. Use Lost Mode only after verifying contact details are correct and safe to expose.
4. Log each action in sequence to avoid duplicate effort.

Exit condition:
- Item recovered, or incident handed to longer-term monitoring plan.

## 4) Shared-Ownership or Family Handoff Confusion

Signals:
- Item moved by trusted contact
- Conflicting ownership context

Actions:
1. Confirm intended owner and sharing state.
2. Separate technical issue from expected handoff behavior.
3. Update ownership and attachment notes to prevent repeat confusion.

Exit condition:
- Clear owner and expected movement rules documented.

## Escalation Guardrails

- Do not start with unpair/reset unless basic detection steps failed.
- Avoid simultaneous multi-change troubleshooting.
- If user safety risk appears, switch to `anti-stalking-safety.md` immediately.
