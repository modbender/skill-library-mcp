# ⚠️ TEST FIXTURES WARNING

The `tests/` directory contains **intentionally malicious test fixtures** used to validate the auditor's detection capabilities. These fixtures exist solely for automated testing (`bash test.sh`).

## DO NOT execute these fixtures on a production system.

They are **inert pattern files** — they contain malicious-looking code patterns but perform no actual harmful behavior when scanned by the auditor. They are only dangerous if manually executed outside the test harness.

## What the malicious fixtures contain:

| Fixture | Patterns |
|---------|----------|
| malicious-basic | Credential harvesting + network exfiltration |
| malicious-obfuscated | Base64-encoded URLs and shell commands |
| malicious-sysread | /etc/passwd, ~/.ssh, ~/.aws/credentials reads |
| malicious-crypto | Hardcoded ETH/BTC wallet addresses |
| malicious-timebomb | Date/time comparison triggers |
| malicious-symlink | Symlinks targeting sensitive system paths |
| malicious-prompt-injection | Agent manipulation directives in docs |
| malicious-download-exec | curl\|bash, wget\|sh, eval $(curl) chains |
| malicious-privilege-escalation | sudo, chmod 777/setuid, system path writes |

## Clean fixtures (should always PASS):

- `clean-basic` — Minimal valid skill
- `clean-with-creds-docs` — Credential mentions in docs only (false positive test)
- `clean-with-network` — Legitimate network usage
- `clean-with-dotfiles` — Standard dotfiles (.gitignore, .editorconfig)

## Exclusion from published package

The `.clawignore` file excludes `tests/` from the distributed ClawHub package. If you obtained this skill and see the `tests/` directory, it was included for development/verification purposes only.
