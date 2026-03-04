# Platform playbook: Personal laptop (macOS/Windows/Linux)

## Why laptops are special

- Laptops roam across networks (coffee shops, conferences).
- They contain personal data and credentials.
- They are often used for browsing and development, increasing exposure.

## Preferred pattern

- **Don’t run OpenClaw 24/7 on your primary laptop** unless you have a strong reason.
- Prefer isolation:
  - Docker (with careful volume/network settings), or
  - a VM, or
  - a separate user account with no access to sensitive files.

## Audit checks

1. Is the Gateway loopback-bound?
2. Are DMs locked down (pairing/allowlist) and groups mention-gated?
3. Are tools constrained (workspace-only FS; exec ask/deny)?
4. Are transcripts/logs being retained longer than necessary?

## Hardening actions

### macOS laptops
- Same guidance as Mac mini, but emphasise:
  - avoid running on untrusted networks
  - disable LAN binds; use loopback-only
  - keep the bot off when travelling

### Windows laptops
- Prefer WSL2 for OpenClaw runtime.
- Ensure Windows Defender + full disk encryption (BitLocker) are enabled.
- Ensure WSL2 distro is updated and has minimal packages.

### Linux laptops
- Use a host firewall (ufw/nftables).
- Consider running OpenClaw in a dedicated user namespace/container.

## Verification

- Rerun `openclaw security audit --deep`.
- Confirm no inbound exposure beyond localhost/tailnet.
