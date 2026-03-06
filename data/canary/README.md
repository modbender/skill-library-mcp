# ðŸ¦ Canary

**Secrets exposure detection for OpenClaw agents.**

Canary scans your local environment for leaked API keys, tokens, passwords, and credentials. It explains what it finds in plain language and offers to fix problems with your permission.

---

## What It Does

- **Light scan on startup** â€” silently checks `.env` files and permissions every time OpenClaw starts. Alerts only when something is wrong.
- **Deep scan on demand** â€” comprehensive sweep of 70+ file locations across 10 categories when you ask.
- **Auto-fix with confirmation** â€” locks down file permissions, moves hardcoded keys to `.env`, cleans shell history, and more. Never changes anything without your OK.
- **Plain language** â€” no security jargon. Designed for users who don't know what `chmod` means.

## What It Looks For

| Category | Examples |
|----------|----------|
| API Keys | OpenAI, Anthropic, AWS, GCP, Stripe, GitHub, Slack, and 20+ more |
| Passwords | Plaintext in configs, database connection strings |
| Private Keys | SSH keys, PEM files, JWTs |
| Cloud Credentials | AWS, Azure, GCP, DigitalOcean, Heroku |
| Tokens & Sessions | OAuth, bearer tokens, webhook URLs |
| Local Files | Credential exports, password manager CSVs, Terraform state, Kubernetes configs |

## Detection Methods

Canary uses 11 detection methods: regex pattern matching (30+ service-specific patterns), Shannon entropy analysis, file permission checks, git history scanning, filename and file size heuristics, symlink detection, base64 decoding, duplicate secret detection, stale credential detection, and directory scanning with safety limits.

Context-dependent patterns (UUIDs, hex strings) require nearby service-specific keywords to reduce false positives.

## Security Hardening

Canary has been through **two full security audit cycles**. 15 vulnerabilities were identified and resolved:

- **Self-integrity verification** â€” SHA-256 hash of SKILL.md checked on every startup from two separate storage locations
- **Config file protection** â€” path validation, scope limits on exclusions, tamper detection, first-run baseline protection, symlink rejection
- **Auto-fix safety** â€” encrypted backups before every fix, TOCTOU re-verification, rollback via conversation, secure deletion after 7 days
- **Information leakage prevention** â€” prefix-only secret previews with length hints, connection string password masking, hashed file paths in scan state
- **Anti-exploitation** â€” lower trust for temp directory findings, context-dependent regex, critical findings never suppressed, no shell execution of config paths

## Severity Levels

- ðŸ”´ **Action needed** â€” real exposure right now
- ðŸŸ¡ **Heads up** â€” moderate risk, fix when convenient
- ðŸŸ¢ **Good** â€” checked and clean

## Platform Support

| Platform | Support |
|----------|---------|
| macOS | Full |
| Linux | Full |
| Windows | Partial (ACL differences, guided fixes instead of chmod) |

## Privacy

- All scanning happens locally. Nothing leaves your machine.
- No telemetry, no analytics, no network calls.
- Secret values are never stored or logged.
- Conversation previews show prefix only: `sk-...(52 chars)`
- Scan state stores file paths as SHA-256 hashes, not plaintext.

## File Structure

```
canary/
  SKILL.md                    # Core skill definition (719 lines)
  README.md                   # This file
  claude-project/
    system-prompt.md          # System prompt for Claude Project
    project-instructions.md   # Setup guide
  .canary/                    # Created at runtime
    config.yml                # User scan paths & exclusions
    last_scan.yml             # Scan state (hashed paths, counts)
    integrity.sha256           # SKILL.md integrity hash
    backups/                  # Encrypted pre-fix backups
```

## Installation

```bash
clawhub install canary
```

Or manually: copy the `SKILL.md` file into your OpenClaw skills directory.

## Usage

Canary runs automatically on startup. For a full scan:

> "Run a security check"
> "Am I leaking any secrets?"
> "Scan my environment"

## Claude Project

This repo includes files to set up Canary as a **Claude Project** on claude.ai. See the [`claude-project/`](./claude-project/) folder for setup instructions.

## Known Limitations

- Local scanning only â€” cannot check remote servers or cloud dashboards
- Cannot rotate or revoke credentials â€” provides guided instructions
- Encrypted files and password-protected archives are opaque
- Entropy analysis can flag non-secret high-entropy strings (hashes, test data)
- Windows has partial support due to ACL differences

## Version

**v1.0.0** â€” Initial release. Secrets exposure detection with auto-fix. Security-hardened through two audit cycles.

## License

[MIT](LICENSE)

---

*Canary is intended for defensive security and self-auditing only. Always ensure you have appropriate authorization before scanning any environment you don't own.*
