# HomePod Network Diagnostics

Use this flow when playback stalls, Siri responses timeout, or devices vanish from Home.

## Layered Triage

1. Confirm incident scope:
- Single device
- Single room
- Whole home

2. Capture baseline:
- HomePod model and software version
- Current Wi-Fi band and RSSI estimate
- Home hub online status

3. Run checks by layer:
- Layer A: local link quality
- Layer B: router policy and multicast behavior
- Layer C: Apple service dependency

## Fast Checks

| Signal | Check | Expected |
|--------|-------|----------|
| Device visibility | Home app accessory list | HomePod present and responsive |
| Local reachability | Same SSID and subnet for controllers | Stable discovery |
| Hub health | Home hub shown as connected | Automation execution available |
| Time sync | Router and devices synchronized | No auth timestamp drift |

## Decision Matrix

| Observation | Probable Layer | First Action |
|-------------|----------------|--------------|
| One HomePod drops from AirPlay | Layer A | Validate signal and local interference |
| All automations stop at once | Layer B or hub | Verify home hub status and router changes |
| Siri responds but action does not execute | Layer C or permission | Validate account/home permissions and service status |
| Playback starts then desyncs | Layer A | Stabilize channel congestion and retest sequence |

## Escalation Guardrails

- Do not factory reset before collecting at least one reproducible trace.
- Do not change router and device settings in the same iteration.
- After each change, rerun the same two validation actions to keep evidence comparable.
