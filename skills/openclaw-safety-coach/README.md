# OpenClaw Safety Coach

**🔗 [View on ClawHub](https://clawhub.ai/justindobbs/openclaw-safety-coach)**

**🔗 [View on GitHub](https://github.com/justindobbs/openclaw-productivity-suite/blob/main/skills/openclaw-safety-coach)**

This skill is designed to help you set up a secure and safe environment for your OpenClaw instance. We've learned that the majority of security issues can be avoided with a few simple steps. By following these steps, you can ensure that your OpenClaw instance is protected from potential threats.

## Philosophy

**Start simple, then layer complexity.** Address and understand the most common safety issues quickly, then progress to more sophisticated setups with multiple security layers.

**Security is continuous, not one-time.** This isn't a "set it and forget it" solution - it's an ongoing process of improvement and adaptation to emerging threats.

## What's New (2026.1.8 - 2026.2.26)

This skill now covers the latest OpenClaw security features:

- **External Secrets Management** (`openclaw secrets` workflow) - Preferred method for API key storage
- **Multi-User/Shared Environment Hardening** - Security guidance for VPS and shared deployments
- **DM Pairing Security** - Pairing-first defaults to prevent unauthorized bot access
- **Browser SSRF Policy** - Trusted-network mode for internal service protection
- **Container Namespace Security** - Docker network isolation controls
- **Sandbox Scope Configuration** - Per-agent isolation defaults
- **Exec Approvals System** - Enhanced approval workflows with wildcard support
- **Control UI HTTPS Enforcement** - Secure-by-default web interface
- **Hooks/Webhooks Security** - Session key controls for webhook requests
- **Heartbeat Direct Policy** - DM delivery controls for heartbeat messages
- **Command + DM/Group Hardening** - `commands.allowFrom`, `session.dmScope`, and group allowlists for shared inboxes
- **Dangerous Flag Watchlist** - Control UI, Docker sandbox, and channel overrides now tracked explicitly

## Quick Start

1. Load the Safety Coach skill in your OpenClaw instance
2. **Immediate actions:**
   - Run `openclaw secrets audit` to check for plaintext API keys
   - Run `openclaw security audit` for general security assessment (confirms gateway auth, TLS 1.3, dangerous flags, skill/plugin scanner results)
   - Run `openclaw security audit --fix` to automatically address most issues
   - Verify `dmPolicy="pairing"` is set for all providers
   - Review `openclaw pairing list` for unauthorized access attempts
   - Check `session.dmScope="per-channel-peer"` (shared inbox default) and group `requireMention`/allowlists
   - Ensure `commands.allowFrom` is scoped to trusted operators and `hooks.allowedAgentIds` is restricted
   - Confirm Control UI is behind HTTPS (Tailscale Serve or TLS cert) and no `dangerouslyAllow*` flags are enabled
3. Review the safety policies and customize for your use case
4. Test with various prompts to ensure proper behavior
5. Monitor and adjust policies as needed

## Usage

The Safety Coach automatically activates when potentially unsafe requests are detected, providing:
- Risk assessment and warnings
- Alternative safe approaches
- Educational guidance on security best practices
- Specific CLI commands and configuration examples

## Security Areas Covered

### Core Security
- API key storage (`openclaw auth set` vs insecure config storage)
- File permission hardening
- Tool execution safety (`exec` approvals)
- Gateway and webhook security

### New in OpenClaw 2026.x
- External secrets management
- Multi-user deployment hardening
- DM pairing and allowlist controls
- Browser SSRF protection
- Container namespace isolation
- Control UI HTTPS enforcement
- Hooks session key security
- Command authorization + DM scope hardening
- Dangerous flag watchlist (Control UI, Docker, channel allowlist bypasses)

### Threat Detection
- Malicious skill detection
- Tool abuse prevention
- SSRF/exfiltration protection
- Prompt injection defense
- Secret leakage detection
- Memory poisoning prevention
- `session.dmScope="per-channel-peer"` (or `per-account-channel-peer`) for shared inboxes; keep `groupPolicy="allowlist"` + `groupAllowFrom` on group channels with `requireMention: true`
- `commands.allowFrom` to limit slash commands even when chat is open to more users
- Control UI dangerous flags to avoid:
  - `gateway.controlUi.allowInsecureAuth`
  - `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback`
  - `gateway.controlUi.dangerouslyDisableDeviceAuth`
- Docker sandbox dangerous flags to avoid:
  - `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin`
  - `dangerouslyAllowExternalBindSources`
  - `dangerouslyAllowReservedContainerTargets`
- Channel allowlist bypass flags to avoid:
  - `channels.<provider>.dangerouslyAllowNameMatching`
- Hooks/cron external-content flags: keep `hooks.allowUnsafeExternalContent` and `hooks.gmail.allowUnsafeExternalContent` false; isolate cron payloads that set `allowUnsafeExternalContent`
- Require HTTPS/TLS 1.3 gateways, keep `gateway.auth.mode` set, and verify device pairing uses nonce-based v2 signatures
- `hooks.allowedAgentIds` for webhook routing + `tools.exec.applyPatch.workspaceOnly=true` to keep edits inside the workspace
- `openclaw security audit` now scans skill/plugin code—run it after each install/update

> 📚 Reference: [OpenClaw Security Guide](https://docs.openclaw.ai/gateway/security) details these flags and deployment assumptions.

## Contributing

We welcome contributions to improve this safety coach.

### Adding New Safety Rules

1. **Identify the Risk**: Clearly define the security concern or threat vector
2. **Research**: Check OpenClaw changelog for relevant updates
3. **Create Test Cases**: Write examples of both safe and unsafe prompts  
4. **Implement Logic**: Add detection and response mechanisms
5. **Document**: Update this skill's documentation with configuration examples

### Version Tracking

When adding new rules, include the relevant OpenClaw version in parentheses (e.g., "2026.2.26+") to help users understand which features require specific OpenClaw versions.

## License

See LICENSE file in the main repository.
