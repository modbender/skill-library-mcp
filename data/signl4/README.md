# SIGNL4 OpenClaw Skill

This OpenClaw skill allows you to **send and close alerts in SIGNL4** using the SIGNL4 inbound webhook.

SIGNL4 provides critical alerting, incident response, and service dispatching for mission-critical operations. It delivers persistent notifications via mobile push, SMS, voice calls, and email, with built-in tracking, escalation, on-call scheduling, and team collaboration. Find out more at https://www.signl4.com/.

## What it can do
- Trigger a new SIGNL4 alert
- Resolve an existing alert using an External ID
- Optionally set service, alerting scenario, and location

## Requirements
- `curl`
- A SIGNL4 team secret

## Configuration
Set the following environment variable:

```sh
export SIGNL4_TEAM_SECRET="<your-team-secret>"
```

Optional:
```sh
export SIGNL4_WEBHOOK_BASE="https://connect.signl4.com/webhook"
```

## Usage examples

### Send an alert
Send a SIGNL4 alert about a database outage with an External ID.

### Close an alert
Close the SIGNL4 alert using the same External ID.

## References
https://docs.signl4.com/integrations/webhook/webhook.html
