---
name: caprover
description: "Manage CapRover PaaS instances via API: create/update apps, deploy from Docker image or custom Dockerfile (tar file), configure ports, volumes, env vars, and serviceUpdateOverride for Docker Swarm settings. Use when the user wants to deploy, configure, or diagnose an app on a CapRover server — including setting up TCP ports for non-HTTP servers (game servers, databases), mounting persistent volumes, building custom Docker images on the host, or reading build/runtime logs."
---

# CapRover Management Skill

CapRover is a self-hosted PaaS that wraps Docker Swarm. It exposes a REST API for full app lifecycle management.

## Quick Setup

Always start by authenticating:

```python
import urllib.request, json, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE  # self-signed cert on CapRover is common

BASE = "https://<captain-domain>"  # e.g. https://captain.example.com

def api(path, data=None, token=None, timeout=60):
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["x-captain-auth"] = token
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers)
    resp = urllib.request.urlopen(req, context=ctx, timeout=timeout)
    return json.loads(resp.read())

token = api("/api/v2/login", {"password": "<password>"})["data"]["token"]
```

See `references/api.md` for all endpoints. See `scripts/caprover.py` for a ready-to-use helper class.

## Core Workflows

### 1. Create an App

```python
api("/api/v2/user/apps/appDefinitions/register",
    {"appName": "myapp", "hasPersistentData": False}, token)
```

Set `hasPersistentData: True` if the app needs persistent volumes.

### 2. Deploy from a Docker Image

```python
api("/api/v2/user/apps/appDefinitions/update",
    {"appName": "myapp", "imageName": "nginx:latest"}, token)

api("/api/v2/user/apps/appData/myapp/redeploy",
    {"appName": "myapp", "gitHash": ""}, token)
```

### 3. Deploy from a Custom Dockerfile (Build on Host)

Pack a `captain-definition`, `Dockerfile`, and support files into a `.tar.gz`, then POST:

```python
# captain-definition (required in tar root):
# {"schemaVersion": 2, "dockerfilePath": "./Dockerfile"}

with open("app.tar.gz", "rb") as f:
    tar_data = f.read()

boundary = "----FormBoundaryCaprover"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="sourceFile"; filename="app.tar.gz"\r\n'
    f"Content-Type: application/octet-stream\r\n\r\n"
).encode() + tar_data + f"\r\n--{boundary}--\r\n".encode()

req = urllib.request.Request(
    f"{BASE}/api/v2/user/apps/appData/myapp",
    data=body,
    headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "x-captain-auth": token,
    },
)
resp = urllib.request.urlopen(req, context=ctx, timeout=180)
```

**This builds the image natively on the CapRover host** — critical for ARM64 hosts where pre-built amd64 images won't run.

### 4. Configure Ports, Env Vars, Volumes

```python
api("/api/v2/user/apps/appDefinitions/update", {
    "appName": "myapp",
    "envVars": [{"key": "MY_VAR", "value": "hello"}],
    "ports": [{"hostPort": 25565, "containerPort": 7777}],
    "volumes": [{"containerPath": "/data", "volumeName": "myapp-data"}],
    "instanceCount": 1,
}, token)
```

> ⚠️ **Port update bug**: The `ports` field update sometimes returns HTTP 500 on CapRover (known issue). Workaround: set ports once at app creation time or use `serviceUpdateOverride`.

### 5. Advanced Docker Swarm Settings (serviceUpdateOverride)

For settings not exposed in the standard API — volume mounts, custom DNS, resource limits:

```python
override = json.dumps({
    "TaskTemplate": {
        "ContainerSpec": {
            "Mounts": [{
                "Type": "volume",
                "Source": "captain--myapp-data",  # CapRover names: captain--<appname>-<name>
                "Target": "/data"
            }]
        }
    }
})

api("/api/v2/user/apps/appDefinitions/update",
    {"appName": "myapp", "serviceUpdateOverride": override}, token)
```

> ⚠️ Setting `serviceUpdateOverride` to `""` (empty string) **clears** it and removes all Docker Swarm overrides, including volume mounts.

### 6. Read Logs

```python
# Build logs (after deploying)
r = api("/api/v2/user/apps/appData/myapp", token=token)
build_lines = r["data"]["logs"]["lines"]

# Runtime logs (stdout of running container)
r = api("/api/v2/user/apps/appData/myapp/logs", token=token)
raw_logs = r["data"]["logs"]
```

## ARM64 / Multi-Arch Gotchas

If the CapRover host is ARM64 (`uname -m` returns `aarch64`):

- **Do not use amd64-only pre-built images** — they will silently fail or crash with exec format errors
- **Build from Dockerfile on the host** (workflow #3 above) to get native ARM64 images
- For apps that need Mono (e.g. Windows .exe files on Linux ARM64): install `mono-runtime` in the Dockerfile and use `mono ./App.exe` as the entrypoint
- Detect arch at runtime in scripts: `$(uname -m)` returns `aarch64` on ARM64

## Common Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| `HTTP 500` on port update | CapRover bug | Set ports at app creation, or use serviceUpdateOverride |
| Container crashes, no logs | Wrong arch image (amd64 on arm64) | Build from Dockerfile on host |
| Port open but server not responding | Server listening on `127.0.0.1` only | Check server bind address; use `0.0.0.0` |
| World/data lost on restart | No volume mount | Add `serviceUpdateOverride` with `Mounts` |
| Logs empty | App writes logs to file, not stdout | Override entrypoint to redirect to stdout |
| `volumes: []` in API but data persists | serviceUpdateOverride holds the mount — API and Swarm state diverge | Check serviceUpdateOverride, not just app definition |

## Node / Cluster Info

```python
r = api("/api/v2/user/system/info", token=token)
nodes = r["data"]["nodes"]
```

## References

- Full API endpoint list + request/response shapes: `references/api.md`
- Reusable Python helper class: `scripts/caprover.py`
