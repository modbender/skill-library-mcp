# OpenClaw Deployment

## Install & Onboard
```
npm install -g openclaw@latest
openclaw onboard [--install-daemon]
openclaw doctor
```

## Docker
See `https://docs.openclaw.ai/install/docker`. Also: Podman, Nix, Ansible.

## Gateway Service
```
openclaw gateway install [--port <port>] [--runtime <node|bun>] [--token <token>] [--force]
openclaw gateway start|stop|restart|status|uninstall
```
Default runtime: Node (bun not recommended for WhatsApp/Telegram).

## Node Host
```
openclaw node install --host <gateway-host> [--port <port>] [--runtime <node|bun>]
openclaw node start|stop|restart|uninstall|status
```

## Update / Rollback
`openclaw update` → re-run `openclaw doctor`.
Rollback: reinstall pinned version.

## Production Checklist
- [ ] Strong `gateway.auth.token`
- [ ] Loopback bind (or VPN/Tailscale)
- [ ] `openclaw security audit` periodic
- [ ] `openclaw secrets audit` for plaintext
- [ ] `openclaw devices list` for unauthorized devices
- [ ] Node runtime (not bun) for stability
