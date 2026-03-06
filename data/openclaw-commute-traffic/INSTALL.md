# Commute Traffic Skill — Installation Guide

## Prerequisites

- OpenClaw running on Kubernetes with `python3` available in the pod
- A **free** TomTom API key (no credit card required)

## 1. Get a TomTom API Key

1. Go to [developer.tomtom.com](https://developer.tomtom.com)
2. Register for a free account
3. In the dashboard, go to **My Apps** → create an app (or use the default one)
4. Copy your API key

**Free tier:** 2,500 requests/day (~75,000/month). Each traffic check uses 3 requests (geocode origin + geocode destination + route), so you get ~830 checks/day for free.

## 2. Create the Kubernetes Secret

```bash
kubectl create secret generic tomtom-api-key \
  --from-literal=TOMTOM_API_KEY='your-key-here' \
  -n <openclaw-namespace>
```

## 3. Expose the Secret to the OpenClaw Pod

Add the environment variable to your OpenClaw deployment:

```yaml
env:
  - name: TOMTOM_API_KEY
    valueFrom:
      secretKeyRef:
        name: tomtom-api-key
        key: TOMTOM_API_KEY
```

## 4. Install the Skill

Copy the skill directory into the OpenClaw pod:

```bash
# Option A: Into user-level skills (applies to all workspaces)
kubectl cp commute-traffic/ <pod>:~/.openclaw/skills/commute-traffic/

# Option B: Into a specific workspace
kubectl cp commute-traffic/ <pod>:<workspace>/skills/commute-traffic/
```

Make the script executable:

```bash
kubectl exec <pod> -- chmod +x ~/.openclaw/skills/commute-traffic/scripts/check_traffic.py
```

## 5. Configure in openclaw.json

Add the skill entry to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "commute-traffic": {
        "enabled": true,
        "env": {
          "TOMTOM_API_KEY": {
            "source": "env",
            "provider": "default",
            "id": "TOMTOM_API_KEY"
          }
        }
      }
    }
  }
}
```

## 6. Verify

Start a **new OpenClaw session** (skills are snapshotted at session start), then ask:

> "Check traffic from Basel to Zurich"

You should get a JSON response with live travel time, traffic delay, and congestion level.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `TOMTOM_API_KEY not set` | Verify the secret exists and the env var is mounted in the pod |
| `No coordinates found` | Try a more specific location (e.g., "Basel, Switzerland" instead of just "Basel") |
| `HTTP 403` | API key is invalid or expired — regenerate at developer.tomtom.com |
| `HTTP 429` | Free tier limit exceeded (2,500/day) — wait until tomorrow |
| No response from skill | Start a new session — skills load at session start |
