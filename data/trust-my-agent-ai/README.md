<p align="center">
  <h1 align="center">🛡️ TrustMyAgent</h1>
  <p align="center"><strong>Security bodyguard for OpenClaw agents</strong></p>
  <p align="center">
    <a href="https://www.trustmyagent.ai">Website</a> &bull;
    <a href="https://www.trustmyagent.ai/trust-center.html">Trust Center</a> &bull;
    <a href="#quick-start">Quick Start</a> &bull;
    <a href="#contributing">Contributing</a>
  </p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://openclaw.ai"><img src="https://img.shields.io/badge/OpenClaw-skill-green.svg" alt="OpenClaw Skill"></a>
  <img src="https://img.shields.io/badge/checks-41-brightgreen.svg" alt="41 Security Checks">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
</p>

---

An EDR-like security agent for [OpenClaw](https://openclaw.ai) agents. Runs 41 security checks across 14 domains, calculates a trust score (0-100), and sends telemetry to a centralized [Trust Center](https://www.trustmyagent.ai/trust-center.html) dashboard where humans and other agents can verify trustworthiness.

**Stateless by design** - runs entirely in memory, stores nothing locally, leaves no traces on the host.

## Why

AI agents are powerful but opaque. When an agent runs on a machine, how do you know it isn't:

- Leaking secrets from environment variables?
- Spawning suspicious processes?
- Accessing files it shouldn't?
- Running with excessive privileges?
- Connecting to exfiltration services?

TrustMyAgent answers these questions every 15 minutes and publishes the results to a public Trust Center so anyone can verify an agent's security posture.

## Quick Start

### As an OpenClaw Skill (recommended)

Copy into your workspace skills directory:

```bash
# From your OpenClaw workspace
mkdir -p skills/trustmyagent
cp -r /path/to/trust-my-agent-ai/* skills/trustmyagent/
```

After installation, ask the agent to run the setup:

> "Set up TrustMyAgent"

The agent will follow the Setup instructions in SKILL.md to install dependencies, run a test assessment, and create the cron job (`*/15 * * * *`) in the `agent:security:main` session stream. See SKILL.md for the full setup steps.

### Standalone

```bash
# Run assessment and send telemetry (agent name from IDENTITY.md)
python3 run.py

```

### Requirements

- Python 3.8+
- `openssl` (for TLS checks)
- No pip dependencies - stdlib only

## Security Domains

| Domain | Checks | Examples |
|--------|--------|---------|
| **Physical Environment** | PHY-001 to PHY-005 | Disk encryption, container isolation, non-root execution |
| **Network** | NET-001 to NET-005 | Dangerous ports, TLS/SSL, DNS resolution, certificates |
| **Secrets** | SEC-001 to SEC-005, MSG-005 | Env var secrets, cloud creds, private keys, conversation leaks |
| **Code** | COD-001 to COD-004 | Git security, no secrets in repos |
| **Logs** | LOG-001 to LOG-004 | System logging active, audit readiness |
| **Skills** | SKL-001 to SKL-005, MSG-001, MSG-003 | Skill manifests, MCP server trust |
| **Integrity** | INT-001 to INT-005, MSG-002, MSG-006 | Backdoors, suspicious tool calls, URL reputation |
| **Social Guards** | SOC-001 to SOC-006, MSG-004 | Action logging, session transparency, Moltbook integrity, owner reputation |
| **Incident Prevention** | INC-001 to INC-005 | Process spawning, system load, port scanning |
| **Node Security** | NODE-001 to NODE-005 | Remote execution approval, token permissions, exec allowlists |
| **Media Security** | MEDIA-002 to MEDIA-003 | Temp directory permissions, file type validation |
| **Gateway Security** | GATEWAY-001 to GATEWAY-002 | Binding address, authentication |
| **Identity Security** | IDENTITY-001 to IDENTITY-002 | DM pairing allowlist, group chat allowlist |
| **SubAgent Security** | SUBAGENT-001 to SUBAGENT-002 | Concurrency limits, target allowlists |

## Trust Scoring

| Tier | Score | Meaning |
|------|-------|---------|
| **HIGH** | 90-100 | Ready for business |
| **MEDIUM** | 70-89 | Needs review |
| **LOW** | 50-69 | Elevated risk |
| **UNTRUSTED** | 0-49 | Critical security gaps |

- Any **critical** failure caps the score at 49 (UNTRUSTED)
- 3+ **high** severity failures cap the score at 69 (LOW)

## Check Types

**Bash checks** (20) - Shell commands that inspect the host environment. Defined in `checks/openclaw_checks.json`.

**Python/Message sensors** (10) - Programmatic checks that analyze secrets, session transcripts, MCP configs, skill manifests, Moltbook posts, and owner reputation. Defined in `checks/message_checks.json`.

**OpenClaw infrastructure checks** (11) - Python checks for node execution, media handling, gateway, identity, and subagent security. Defined in `checks/nodes_media_checks.json`.

All check types auto-detect macOS vs Linux and use platform-appropriate commands.

## Architecture

```
┌─────────────────┐      POST /api/telemetry      ┌──────────────────┐
│   Agent Host     │  ─────────────────────────►   │ 🛡️ TrustMyAgent Server│
│                  │                                │  (Cloudflare)    │
│  run.py          │                                │  ├─ R2 storage   │
│  ├─ bash checks  │                                │  ├─ agents index │
│  └─ python checks│                                │  └─ trend history│
│                  │                                │                  │
│  (no local state)│                                └──────────────────┘
└─────────────────┘                                        │
                                                    trust-center.html
                                                    (public dashboard)
```

## Configuration

The agent name is automatically read from your `IDENTITY.md` file (`# Name` section). Falls back to the `OPENCLAW_AGENT_NAME` env var, then `"OpenClaw Agent"`.

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `OPENCLAW_AGENT_ID` | Agent identifier | SHA256 of hostname |
| `OPENCLAW_AGENT_NAME` | Override IDENTITY.md name | — |
| `TRUSTMYAGENT_TELEMETRY_URL` | Server endpoint | `https://www.trustmyagent.ai/api/telemetry` |

| CLI Flag | Description |
|----------|-------------|
| `--checks`, `-c` | Path to custom checks JSON |
| `--timeout`, `-t` | Per-check timeout in seconds (default: 30) |
| `--quiet`, `-q` | Minimal output |

## Writing Custom Checks

### Bash check

Add to `checks/openclaw_checks.json`:

```json
{
  "check_id": "CUSTOM-001",
  "name": "My custom check",
  "description": "What this check verifies",
  "category": "integrity",
  "severity": "medium",
  "command": "echo 'SAFE'",
  "expected_output": "SAFE",
  "pass_condition": "contains"
}
```

### Python check

Add the definition to `checks/message_checks.json` and the handler to `run.py`:

```python
@python_check("CUSTOM-002")
def check_something(check: dict) -> Tuple[bool, str]:
    # Return (passed: bool, message: str)
    return True, "Everything looks good"
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. We welcome:

- New security checks for emerging threat vectors
- Platform support improvements (Windows, ARM)
- Integration with additional agent frameworks
- Trust Center dashboard enhancements

## License

[MIT](LICENSE) - built by [Anecdotes AI](https://anecdotes.ai) for the [OpenClaw](https://openclaw.ai) ecosystem.
