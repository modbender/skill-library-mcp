# OpenClaw Nodes and Platforms

For full command syntax, see `cli-full.md` → Nodes / Node Host / Devices sections.

## Platform Notes

| Platform | Notes |
|----------|-------|
| Windows | Use WSL2. Keep gateway on loopback unless intentional. |
| macOS | `nodes notify` macOS-only. `dns setup --apply` needs sudo. |
| Linux | `gateway install` defaults to Node (bun not recommended). |

## Node Host
Run node connecting to remote gateway:
```
openclaw node run --host <gateway-host> --port 18789
openclaw node install [--host] [--port] [--tls] [--runtime <node|bun>] [--force]
openclaw node status|start|stop|restart|uninstall
```

## Node Security Baseline
- Require gateway token for non-loopback
- Restrict channel access via `allowFrom` / `groups` config
- Verify node identity before `nodes approve`
- Treat camera/screen/location/invoke as highest-risk
- Use `security audit` to check misconfigurations
