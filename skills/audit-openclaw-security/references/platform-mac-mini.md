# Platform playbook: Mac mini (always-on host)

## Threat assumptions

- The host is on a home/office LAN; attackers may exist on the local network (guest Wi‑Fi, compromised IoT, etc.).
- macOS hosts often have rich user data (iCloud, Keychain, documents) and are high-value if the agent can access the filesystem or browser.

## Audit checks (macOS)

1. Confirm Gateway is loopback-bound unless you have a tight, intentional plan for remote access.
2. Confirm Gateway auth is enabled (token/password) and **Control UI device identity is not bypassed**.
3. Confirm mDNS/Bonjour discovery is set to minimal/off unless needed.
4. Confirm file permissions on OpenClaw state/config/credentials are user-only.
5. Confirm transcript/log retention is intentional:
   - transcripts: `~/.openclaw/agents/<agentId>/sessions/*.jsonl`
   - logs: `/tmp/openclaw/openclaw-YYYY-MM-DD.log` (or `logging.file`)

## Hardening actions

### 1) Create separation

- Run OpenClaw under a dedicated macOS user (e.g., `openclaw`) with:
  - no iCloud login
  - minimal local permissions
  - no access to personal documents by default

### 2) Disk and OS security

- Enable FileVault for full-disk encryption.
- Keep macOS updated.
- Enable the macOS application firewall and stealth mode where appropriate.

### 3) Network

- Do not port-forward the Gateway.
- If you need remote access, use:
  - SSH tunnel from your admin machine to `127.0.0.1:18789`, or
  - Tailscale Serve (prefer Serve; avoid public Funnel)

### 4) OpenClaw configuration

- Keep `gateway.bind` = `"loopback"`.
- Set `gateway.auth.mode` to token or password and rotate it.
- Avoid Control UI insecure modes:
  - keep `gateway.controlUi.allowInsecureAuth` **off**
  - keep `gateway.controlUi.dangerouslyDisableDeviceAuth` **off**
- Reduce discovery information disclosure:
  - config: `discovery.mdns.mode: "minimal"` or `"off"`
  - env (alternative): `OPENCLAW_DISABLE_BONJOUR=1`
- Lock down DMs and group behaviour:
  - DM pairing
  - group mention gating

### 5) Tools and browser control

- Use least-privilege tool profiles.
- Treat browser control as “operator access”:
  - use a dedicated browser profile
  - do not expose browser control endpoints remotely

### 6) Logging and retention

- Keep tool/log redaction on.
- Set a retention window for transcripts and logs; prune periodically.

## Verification

- `openclaw security audit --deep` returns no Critical issues.
- `lsof -iTCP -sTCP:LISTEN` shows 18789 is bound to loopback only.
- `ls -la ~/.openclaw` indicates restrictive permissions.
