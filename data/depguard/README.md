# DepGuard

**Dependency audit, vulnerability scanning, and license compliance for every project.**

DepGuard is an [OpenClaw](https://openclaw.sh) skill that scans your dependencies for known vulnerabilities, enforces license policies, and generates compliance reports — all locally, no code leaves your machine.

## Why DepGuard?

Every dependency is an attack surface. DepGuard helps you:

1. **Scan for vulnerabilities** using native audit tools (npm audit, pip-audit, cargo audit, govulncheck)
2. **Check licenses** — find copyleft, unknown, or problematic licenses before they become legal issues
3. **Block commits** that introduce vulnerable dependencies (via git hooks)
4. **Auto-fix** by upgrading to patched versions
5. **Generate SBOMs** in CycloneDX format for compliance requirements
6. **Enforce policies** — block specific licenses, require minimum versions

## Quick Start

### Install via ClawHub

```bash
clawhub install depguard
```

### Scan dependencies (Free)

```
> Scan my dependencies for vulnerabilities
```

### Set up continuous monitoring (Pro)

```
> Install DepGuard git hooks
```

### Generate compliance report (Team)

```
> Generate a license compliance report
```

## Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | One-shot vulnerability scan + license check |
| **Pro** | $19/user/mo | Git hooks, continuous monitoring, auto-fix |
| **Team** | $39/user/mo | + Policy enforcement, SBOM generation, compliance reports |
| **Enterprise** | $59/user/mo | + SSO, audit logs, SLA |

**Get your license:** [depguard.pages.dev/pricing](https://depguard.pages.dev/pricing)

## Supported Package Managers

npm, yarn, pnpm, pip, cargo, go, composer, bundler, maven, gradle

## Privacy

- All scanning happens locally using native audit tools
- No code or dependency data is sent externally
- License validation is offline (JWT-based, no phone-home)

## License

DepGuard skill code is MIT licensed. Premium features require a commercial license key.
