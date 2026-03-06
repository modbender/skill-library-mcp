# OpenClaw Nodes and Platforms

Reference normalized against:
- `https://docs.openclaw.ai/platforms`
- `https://docs.openclaw.ai/platforms/windows`
- `https://docs.openclaw.ai/platforms/macos`
- `https://docs.openclaw.ai/platforms/linux`
- `https://docs.openclaw.ai/cli/pairing`

Last verified: 2026-02-17.

## Windows (WSL2)
- Use a Linux distro on WSL2 for stable daemon behavior.
- Keep gateway on loopback unless remote access is intentionally configured.
- For remote node access, prefer private networking (for example Tailscale).

## macOS
- Use macOS-specific platform guidance from docs for companion integrations.
- Ensure required local permissions are granted before enabling device features.

## Linux
- Install gateway service for persistent runtime.
- Validate prerequisites for browser tooling when using managed browser commands.

## Mobile Nodes and Pairing
- Run `openclaw pairing` to start pairing flow.
- Complete pairing from OpenClaw mobile app.
- Verify node availability from dashboard or status commands.

## Node Security Baseline
- Require gateway token for non-loopback bind.
- Restrict who can message/control agent via channel policy.
- Review permissions before enabling camera, microphone, or location features.
- Treat pairing and sensor access as high-risk actions requiring explicit approval.
