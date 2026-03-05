# Platform playbook: Docker / Docker Compose

## Threat assumptions

- Docker does **not** make an exposed service safe. If you publish `18789/tcp` to `0.0.0.0`, the internet (or your LAN) can still reach it.
- Volume mounts (`~/.openclaw`, workspace) often contain the most sensitive data (credentials, transcripts, API keys).
- Container user/root choices matter: a root container + broad mounts can become a host compromise.

## Audit checks (Docker)

1. **Published ports**
   - Confirm the Gateway port is **not** published to all interfaces.
   - Good: `127.0.0.1:18789->18789/tcp` (local only)
   - Risky: `0.0.0.0:18789->18789/tcp` (LAN/internet reachable)

   Commands:
   ```bash
   docker port openclaw-gateway 18789
   docker compose ps
   ```

2. **Gateway auth and bind mode**
   - Even with localhost port publishing, keep Gateway auth enabled.
   - If you are running remote access, prefer SSH tunnel or Tailscale Serve.

3. **Volume mounts**
   - Identify what is mounted into the container:
     - `~/.openclaw` (state/credentials/config)
     - workspace directory
   - Ensure mounts are as narrow as possible and avoid mounting your entire home directory.

4. **Container identity and privileges**
   - Confirm the container runs as a non-root user where possible.
   - Avoid privileged mode, host networking, and unnecessary Linux capabilities.

5. **Updates**
   - Track the OpenClaw image/tag you run.
   - Treat Docker image rebuilds and updates as part of your operational security.

## Hardening actions (strong defaults)

### 1) Publish the Gateway to localhost only

In `docker-compose.yml`, publish the port with an explicit host IP:

```yaml
ports:
  - "127.0.0.1:18789:18789"
```

If you need LAN access, prefer a VPN/tailnet. If you must expose to LAN, firewall it to a tight allowlist.

### 2) Avoid public exposure on cloud VMs

- Cloud + Docker is the highest-risk combination if you publish the port.
- Ensure security groups/firewalls block 18789 from `0.0.0.0/0`.

### 3) Reduce secrets sprawl

- Keep provider credentials in `~/.openclaw/.env` on the host (or a secrets manager), not in the repo.
- Ensure host filesystem permissions on the mounted state dir are user-only.

### 4) Treat browser + exec as high-risk

- Deny `group:runtime` and `group:fs` tools by default for any untrusted chat surface.
- Treat browser control as operator access.

## Verification

- `docker port openclaw-gateway 18789` shows only `127.0.0.1:...` (or no published port).
- `openclaw security audit --deep` shows no Critical findings.
- External reachability tests from a different machine/network fail.
