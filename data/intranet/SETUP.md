# Setup

## Prerequisites

- Python 3 (no additional packages — uses built-in `http.server`)

## Configuration

### Root Directory

The server serves files from a configurable root directory, created automatically if it doesn't exist.

Always `{workspace}/intranet/` (auto-detected from CWD or script location, not configurable).

### Server Settings

| Setting | Default | Flag |
|---|---|---|
| Host | `127.0.0.1` | `--host` |
| Port | `8080` | `--port` |

### State Files

- `{workspace}/intranet/.pid` — PID of running server
- `{workspace}/intranet/.conf` — Runtime config (host, port)

Created automatically on start, cleaned up on stop.

## Plugins

Register external directories as URL-mounted plugins in `config.json`:

```json
{
  "plugins": {
    "banker": "/path/to/banker-data",
    "deliveries": "/path/to/deliveries-data"
  }
}
```

Each plugin is served at `http://host:port/<prefix>/`. If the plugin directory contains an executable `index.py`, it handles all sub-paths as CGI. Otherwise, files are served statically.

### Dynamic Pages

Only files named `index.py` can execute — place one in any webroot subdirectory or plugin root:

```bash
chmod +x {workspace}/intranet/my-dashboard/index.py
```

All other `.py` files are blocked (403 Forbidden).

## Remote Access

To expose the intranet outside your LAN, use any HTTP tunnel or reverse proxy (e.g. Cloudflare Tunnel, Tailscale Funnel, or similar). When exposing to the internet, **always enable token authentication and host allowlist**.

## Authentication

Enable bearer token authentication to restrict access:

```bash
# Via CLI flag
python3 scripts/intranet.py start --token MY_SECRET_TOKEN

# Or set in config.json (recommended)
```

```json
{
  "token": "MY_SECRET_TOKEN"
}
```

When a token is set, clients authenticate via:
- **Query param:** `?token=MY_SECRET_TOKEN` — sets a session cookie and redirects to strip the token from the URL. All subsequent requests use the cookie automatically. Ideal for browsers.
- **Header:** `Authorization: Bearer MY_SECRET_TOKEN` — for API/curl clients (no cookie needed).

The session cookie is `HttpOnly`, `SameSite=Strict`, valid for 30 days. The token never appears in URLs after the initial redirect.

Requests without a valid token or session cookie receive `401 Unauthorized`.

## Host Allowlist

Restrict which hostnames the server responds to via `allowed_hosts` in `config.json`:

```json
{
  "allowed_hosts": [
    "localhost",
    "my-machine.local",
    "my-tunnel.example.com"
  ]
}
```

Requests with a `Host` header not on the list receive `403 Forbidden` — before authentication is even checked.

When `allowed_hosts` is omitted or empty, all hosts are accepted (only allowed on loopback). Binding to `0.0.0.0` requires both `token` and `allowed_hosts` to be configured.

## Persistent Config (`config.json`)

All settings can be stored in `{workspace}/intranet/config.json`:

```json
{
  "token": "MY_SECRET_TOKEN",
  "allowed_hosts": ["localhost", "my-machine.local"],
  "plugins": {
    "myapp": "/path/to/myapp"
  }
}
```

| Key | Description |
|---|---|
| `token` | Bearer token for authentication |
| `allowed_hosts` | Hostnames the server responds to |
| `plugins` | URL prefix → directory path mappings |
