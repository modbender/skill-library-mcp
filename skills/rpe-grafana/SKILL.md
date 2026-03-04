---
name: rpe-grafana
description: "Read current values from Grafana dashboards without knowing the underlying queries. Use when: asked about values visible in a Grafana dashboard (sensor readings, metrics, stats). Navigate by dashboard and panel name — no PromQL/SQL needed. NOT for: writing to Grafana, admin operations, or raw query execution."
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires": { "env": ["GRAFANA_URL", "GRAFANA_USER", "GRAFANA_PASSWORD"] },
        "install":
          [
            {
              "id": "config",
              "kind": "config",
              "label": "Configure Grafana credentials in openclaw.json",
            },
          ],
      },
  }
---

# Grafana Skill

Read current values from any Grafana dashboard without writing queries. The plugin navigates by dashboard and panel name, extracts the panel's existing query configuration, and returns a compact summary — no PromQL, SQL, or datasource knowledge required.

Works with any Grafana datasource (Prometheus, InfluxDB, MySQL, …).

## When to Use

✅ **USE this skill when:**

- Asked about a value that's visible in a Grafana dashboard
- Listing what dashboards or panels are available
- Retrieving the current or recent value of a metric by panel name

## When NOT to Use

❌ **DON'T use this skill when:**

- Writing, modifying, or creating dashboards → use Grafana UI
- Admin operations (users, datasource config, alerts) → use Grafana API directly
- You need to run an arbitrary query not backed by an existing panel

## Setup

Add to your `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "rpe-grafana": {
        "enabled": true,
        "config": {
          "url": "http://your-grafana:3000",
          "user": "your-username",
          "password": "your-password"
        }
      }
    }
  }
}
```

Or set environment variables:

- `GRAFANA_URL` - Grafana base URL
- `GRAFANA_USER` - Username
- `GRAFANA_PASSWORD` - Password or API key

## Tools

### grafana_list_dashboards

List all available dashboards.

**Parameters:** none

**Returns:** `[{ uid, title }]`

### grafana_list_panels

List all panels in a dashboard.

**Parameters:**
- `dashboard_uid` (required) - Dashboard UID from `grafana_list_dashboards`

**Returns:** `[{ id, title }]`

### grafana_query_panel

Read the current data for a specific panel. Fetches the panel's query configuration from the dashboard and executes it via Grafana's datasource API — no query language knowledge needed.

**Parameters:**
- `dashboard_uid` (required) - Dashboard UID
- `panel_id` (required) - Panel ID from `grafana_list_panels`
- `from` (optional) - Start of time range (default: `now-1h`)
- `to` (optional) - End of time range (default: `now`)

**Returns:** `[{ refId, name, lastValue, unit }]`

## Typical Workflow

1. `grafana_list_dashboards` → find the dashboard UID
2. `grafana_list_panels` → find the panel ID by title
3. `grafana_query_panel` → get the current value

## Notes

- Requires a Grafana user with read access (Viewer role is sufficient)
- Dashboard UIDs are stable identifiers; panel IDs are unique within a dashboard
- Row panels are flattened automatically
