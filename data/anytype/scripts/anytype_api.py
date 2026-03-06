#!/usr/bin/env python3
"""
Anytype API helper — thin wrapper around http://127.0.0.1:31012
Usage: python3 anytype_api.py <method> <path> [json_body]
  python3 anytype_api.py GET /v1/spaces
  python3 anytype_api.py POST /v1/spaces '{"name":"My Space"}'
  python3 anytype_api.py POST /v1/search '{"query":"meeting","limit":10}'
"""
import json, os, sys, urllib.request, urllib.error

BASE = "http://127.0.0.1:31012"

def load_env():
    env_path = os.path.expanduser("~/.openclaw/workspace/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env()
API_KEY = os.environ.get("ANYTYPE_API_KEY", "")

def request(method, path, body=None):
    if not API_KEY:
        raise RuntimeError("ANYTYPE_API_KEY not set in .env")
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {err}")

def get(path, **params):
    if params:
        from urllib.parse import urlencode
        path += "?" + urlencode(params)
    return request("GET", path)

def post(path, body=None):
    return request("POST", path, body)

def patch(path, body=None):
    return request("PATCH", path, body)

def delete(path):
    return request("DELETE", path)

# ── Convenience helpers ───────────────────────────────────────────────────────

def list_spaces():
    return get("/v1/spaces").get("data", [])

def search(query, space_id=None, limit=20, types=None, filters=None):
    body = {"query": query, "limit": limit}
    if types:
        body["types"] = types
    if filters:
        body["filter"] = filters
    path = f"/v1/spaces/{space_id}/search" if space_id else "/v1/search"
    return post(path, body).get("data", [])

def list_objects(space_id, limit=50, offset=0):
    return get(f"/v1/spaces/{space_id}/objects", limit=limit, offset=offset).get("data", [])

def get_object(space_id, object_id):
    return get(f"/v1/spaces/{space_id}/objects/{object_id}")

def create_object(space_id, type_key="page", name="", body_md="", properties=None, icon=None):
    payload = {"type_key": type_key, "name": name, "body": body_md}
    if properties:
        payload["properties"] = properties
    if icon:
        payload["icon"] = icon
    return post(f"/v1/spaces/{space_id}/objects", payload)

def update_object(space_id, object_id, **kwargs):
    return patch(f"/v1/spaces/{space_id}/objects/{object_id}", kwargs)

# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    method = sys.argv[1].upper()
    path   = sys.argv[2]
    body   = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    try:
        result = request(method, path, body)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
