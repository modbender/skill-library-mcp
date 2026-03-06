# Joplin Configuration Guide

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JOPLIN_BASE_URL` | No | `http://localhost:41184` | Joplin API URL |
| `JOPLIN_TOKEN` | **Yes** | - | API Token from Web Clipper |

---

## Get API Token

1. Open Joplin → **Tools** → **Options** → **Web Clipper**
2. Enable service and copy the token

---

## Test Connection

```bash
python3 joplin.py ping
```

---

## Configuration Examples

```bash
# Local
JOPLIN_BASE_URL=http://localhost:41184

# Remote
JOPLIN_BASE_URL=https://joplin.example.com
```