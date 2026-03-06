#!/usr/bin/env python3
"""Datadog CLI — Datadog monitoring — manage monitors, dashboards, metrics, logs, events, and incidents via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://api.datadoghq.com/api"

def get_env(name):
    val = os.environ.get(name, "")
    if not val:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(name + "="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not val:
        print(f"Error: {name} not set", file=sys.stderr)
        sys.exit(1)
    return val


def get_headers():
    token = get_env("DD_API_KEY")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}


def get_headers():
    api_key = get_env("DD_API_KEY")
    app_key = get_env("DD_APP_KEY")
    return {"DD-API-KEY": api_key, "DD-APPLICATION-KEY": app_key, "Content-Type": "application/json"}


def get_api_base():
    base = API_BASE
    pass
    return base

def req(method, path, data=None, params=None):
    headers = get_headers()
    if path.startswith("http"):
        url = path
    else:
        url = get_api_base() + path
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url = f"{url}?{qs}" if "?" not in url else f"{url}&{qs}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    for k, v in headers.items():
        r.add_header(k, v)
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {"ok": True}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err_body}), file=sys.stderr)
        sys.exit(1)


def try_json(val):
    if val is None:
        return None
    try:
        return json.loads(val)
    except (json.JSONDecodeError, ValueError):
        return val


def out(data, human=False):
    if human and isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    elif human and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print(item)
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_monitors(args):
    """List monitors."""
    path = "/v1/monitor"
    params = {}
    if getattr(args, "query", None): params["query"] = args.query
    if getattr(args, "tags", None): params["tags"] = args.tags
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_monitor_get(args):
    """Get monitor."""
    path = f"/v1/monitor/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_monitor_create(args):
    """Create monitor."""
    path = "/v1/monitor"
    body = {}
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    if getattr(args, "type", None): body["type"] = try_json(args.type)
    if getattr(args, "query", None): body["query"] = try_json(args.query)
    if getattr(args, "message", None): body["message"] = try_json(args.message)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_monitor_update(args):
    """Update monitor."""
    path = f"/v1/monitor/{args.id}"
    body = {}
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    if getattr(args, "query", None): body["query"] = try_json(args.query)
    data = req("PUT", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_monitor_delete(args):
    """Delete monitor."""
    path = f"/v1/monitor/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_monitor_mute(args):
    """Mute monitor."""
    path = f"/v1/monitor/{args.id}/mute"
    data = req("POST", path)
    out(data, getattr(args, "human", False))

def cmd_dashboards(args):
    """List dashboards."""
    path = "/v1/dashboard"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_dashboard_get(args):
    """Get dashboard."""
    path = f"/v1/dashboard/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_dashboard_create(args):
    """Create dashboard."""
    path = "/v1/dashboard"
    body = {}
    if getattr(args, "title", None): body["title"] = try_json(args.title)
    if getattr(args, "layout", None): body["layout"] = try_json(args.layout)
    if getattr(args, "widgets", None): body["widgets"] = try_json(args.widgets)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_dashboard_delete(args):
    """Delete dashboard."""
    path = f"/v1/dashboard/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_metrics_search(args):
    """Search metrics."""
    path = "/v1/search"
    params = {}
    if getattr(args, "q", None): params["q"] = args.q
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_metrics_query(args):
    """Query metrics."""
    path = "/v1/query"
    params = {}
    if getattr(args, "from_val", None): params["from"] = getattr(args, "from_val")
    if getattr(args, "to", None): params["to"] = args.to
    if getattr(args, "query", None): params["query"] = args.query
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_events_list(args):
    """List events."""
    path = "/v1/events"
    params = {}
    if getattr(args, "start", None): params["start"] = args.start
    if getattr(args, "end", None): params["end"] = args.end
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_event_create(args):
    """Create event."""
    path = "/v1/events"
    body = {}
    if getattr(args, "title", None): body["title"] = try_json(args.title)
    if getattr(args, "text", None): body["text"] = try_json(args.text)
    if getattr(args, "alert_type", None): body["alert_type"] = try_json(args.alert_type)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_logs_search(args):
    """Search logs."""
    path = "/v2/logs/events/search"
    body = {}
    if getattr(args, "query", None): body["query"] = try_json(args.query)
    if getattr(args, "from_val", None): body["from"] = try_json(getattr(args, "from_val"))
    if getattr(args, "to", None): body["to"] = try_json(args.to)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_incidents(args):
    """List incidents."""
    path = "/v2/incidents"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_incident_get(args):
    """Get incident."""
    path = f"/v2/incidents/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_hosts(args):
    """List hosts."""
    path = "/v1/hosts"
    params = {}
    if getattr(args, "filter", None): params["filter"] = args.filter
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_downtimes(args):
    """List downtimes."""
    path = "/v1/downtime"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_downtime_create(args):
    """Create downtime."""
    path = "/v1/downtime"
    body = {}
    if getattr(args, "scope", None): body["scope"] = try_json(args.scope)
    if getattr(args, "message", None): body["message"] = try_json(args.message)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_slos(args):
    """List SLOs."""
    path = "/v1/slo"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_synthetics(args):
    """List synthetic tests."""
    path = "/v1/synthetics/tests"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_users(args):
    """List users."""
    path = "/v2/users"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Datadog CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    monitors_p = sub.add_parser("monitors", help="List monitors")
    monitors_p.add_argument("--query", help="Search query", default=None)
    monitors_p.add_argument("--tags", help="Filter tags", default=None)
    monitors_p.set_defaults(func=cmd_monitors)

    monitor_get_p = sub.add_parser("monitor-get", help="Get monitor")
    monitor_get_p.add_argument("id", help="Monitor ID")
    monitor_get_p.set_defaults(func=cmd_monitor_get)

    monitor_create_p = sub.add_parser("monitor-create", help="Create monitor")
    monitor_create_p.add_argument("--name", help="Name", default=None)
    monitor_create_p.add_argument("--type", help="Type", default=None)
    monitor_create_p.add_argument("--query", help="Query", default=None)
    monitor_create_p.add_argument("--message", help="Message", default=None)
    monitor_create_p.set_defaults(func=cmd_monitor_create)

    monitor_update_p = sub.add_parser("monitor-update", help="Update monitor")
    monitor_update_p.add_argument("id", help="Monitor ID")
    monitor_update_p.add_argument("--name", help="Name", default=None)
    monitor_update_p.add_argument("--query", help="Query", default=None)
    monitor_update_p.set_defaults(func=cmd_monitor_update)

    monitor_delete_p = sub.add_parser("monitor-delete", help="Delete monitor")
    monitor_delete_p.add_argument("id", help="Monitor ID")
    monitor_delete_p.set_defaults(func=cmd_monitor_delete)

    monitor_mute_p = sub.add_parser("monitor-mute", help="Mute monitor")
    monitor_mute_p.add_argument("id", help="Monitor ID")
    monitor_mute_p.set_defaults(func=cmd_monitor_mute)

    dashboards_p = sub.add_parser("dashboards", help="List dashboards")
    dashboards_p.set_defaults(func=cmd_dashboards)

    dashboard_get_p = sub.add_parser("dashboard-get", help="Get dashboard")
    dashboard_get_p.add_argument("id", help="Dashboard ID")
    dashboard_get_p.set_defaults(func=cmd_dashboard_get)

    dashboard_create_p = sub.add_parser("dashboard-create", help="Create dashboard")
    dashboard_create_p.add_argument("--title", help="Title", default=None)
    dashboard_create_p.add_argument("--layout", help="ordered/free", default=None)
    dashboard_create_p.add_argument("--widgets", help="JSON widgets", default=None)
    dashboard_create_p.set_defaults(func=cmd_dashboard_create)

    dashboard_delete_p = sub.add_parser("dashboard-delete", help="Delete dashboard")
    dashboard_delete_p.add_argument("id", help="Dashboard ID")
    dashboard_delete_p.set_defaults(func=cmd_dashboard_delete)

    metrics_search_p = sub.add_parser("metrics-search", help="Search metrics")
    metrics_search_p.add_argument("--q", help="Query", default=None)
    metrics_search_p.set_defaults(func=cmd_metrics_search)

    metrics_query_p = sub.add_parser("metrics-query", help="Query metrics")
    metrics_query_p.add_argument("--from", dest="from_val", help="Start timestamp", default=None)
    metrics_query_p.add_argument("--to", help="End timestamp", default=None)
    metrics_query_p.add_argument("--query", help="Metric query", default=None)
    metrics_query_p.set_defaults(func=cmd_metrics_query)

    events_list_p = sub.add_parser("events-list", help="List events")
    events_list_p.add_argument("--start", help="Start timestamp", default=None)
    events_list_p.add_argument("--end", help="End timestamp", default=None)
    events_list_p.set_defaults(func=cmd_events_list)

    event_create_p = sub.add_parser("event-create", help="Create event")
    event_create_p.add_argument("--title", help="Title", default=None)
    event_create_p.add_argument("--text", help="Text", default=None)
    event_create_p.add_argument("--alert_type", help="Type", default=None)
    event_create_p.set_defaults(func=cmd_event_create)

    logs_search_p = sub.add_parser("logs-search", help="Search logs")
    logs_search_p.add_argument("--query", help="Log query", default=None)
    logs_search_p.add_argument("--from", dest="from_val", help="From ISO", default=None)
    logs_search_p.add_argument("--to", help="To ISO", default=None)
    logs_search_p.set_defaults(func=cmd_logs_search)

    incidents_p = sub.add_parser("incidents", help="List incidents")
    incidents_p.set_defaults(func=cmd_incidents)

    incident_get_p = sub.add_parser("incident-get", help="Get incident")
    incident_get_p.add_argument("id", help="Incident ID")
    incident_get_p.set_defaults(func=cmd_incident_get)

    hosts_p = sub.add_parser("hosts", help="List hosts")
    hosts_p.add_argument("--filter", help="Filter", default=None)
    hosts_p.set_defaults(func=cmd_hosts)

    downtimes_p = sub.add_parser("downtimes", help="List downtimes")
    downtimes_p.set_defaults(func=cmd_downtimes)

    downtime_create_p = sub.add_parser("downtime-create", help="Create downtime")
    downtime_create_p.add_argument("--scope", help="Scope", default=None)
    downtime_create_p.add_argument("--message", help="Message", default=None)
    downtime_create_p.set_defaults(func=cmd_downtime_create)

    slos_p = sub.add_parser("slos", help="List SLOs")
    slos_p.set_defaults(func=cmd_slos)

    synthetics_p = sub.add_parser("synthetics", help="List synthetic tests")
    synthetics_p.set_defaults(func=cmd_synthetics)

    users_p = sub.add_parser("users", help="List users")
    users_p.set_defaults(func=cmd_users)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
