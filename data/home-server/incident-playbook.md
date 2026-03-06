# Incident Playbook

## Severity Levels

- Sev-1: Data at risk or total outage
- Sev-2: Major feature unavailable with workaround
- Sev-3: Degraded performance or isolated failure

## First Five Minutes

1. Stabilize: stop automated changes and preserve evidence.
2. Scope: identify affected services, users, and data paths.
3. Contain: isolate failing components from healthy traffic.
4. Communicate: post concise status with next update time.

## Triage Commands (Adapt to Host)

- Service state: process manager status or container health
- Network state: listening ports and recent connection errors
- Storage state: free space, I/O saturation, filesystem health
- Logs: reverse proxy, application, and host security logs

## Recovery Sequence

1. Restore control plane dependencies (DNS, proxy, auth).
2. Recover stateful stores from latest verified snapshot.
3. Bring stateless services back online.
4. Run functional smoke checks before full traffic.

## Post-Incident Review

- Timeline with timestamps and key decisions
- Root cause and contributing factors
- Preventive actions with owners and deadlines
- Detection improvements for earlier alerting
