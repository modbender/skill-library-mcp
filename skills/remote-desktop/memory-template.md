# Memory Template — Remote Desktop

Create `~/remote-desktop/memory.md` with this structure:

```markdown
# Remote Desktop Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
<!-- What you know about their setup -->
<!-- Client OS, common targets, network situation -->

## Preferences
<!-- How they like to connect -->
<!-- Default protocol, resolution, tunnel preference -->

## Saved Hosts
<!-- Quick reference to hosts/ folder -->
<!-- host: protocol, last connected -->

---
*Updated: YYYY-MM-DD*
```

## Host Profile Template

For each host, create `~/remote-desktop/hosts/{hostname}.md`:

```markdown
# {Hostname}

## Connection
host: 192.168.1.X
protocol: rdp | vnc | ssh-x11
user: username
port: default | custom

## Tunnel (if needed)
tunnel: ssh user@jumphost -L LOCAL:TARGET:REMOTE

## Command
<!-- Working command that connects -->
xfreerdp /v:HOST /u:USER /size:1920x1080

## Notes
<!-- OS version, quirks, last working date -->

---
*Last connected: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning their setup | Ask before saving info |
| `complete` | Know their common hosts | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |
