# Port Monitoring Policy For OpenClaw

## Objective

Continuously identify listening services, detect insecure ports/protocols, and flag ports not approved by baseline policy.

## Baseline File

Use `~/.openclaw/security/approved_ports.json` as a JSON array:

```json
[
  { "port": 22, "protocol": "tcp", "command": "sshd" },
  { "port": 443, "protocol": "tcp", "command": "nginx" }
]
```

`command` is optional but recommended for tighter control.

## Monitoring Command

Run:

`python3 scripts/port_monitor.py --json`

## Required Analyst Actions

1. Review all `unapproved-port` findings.
2. Review all `insecure-port` findings and propose secure alternatives.
3. Confirm whether `public-bind` findings are necessary exposure.
4. Ask for user approval before any root-level remediation steps.

## Insecure Port Guidance

Enforce upgrades where possible:

1. `80 -> 443` (HTTPS instead of HTTP)
2. `23 -> 22` (SSH instead of Telnet)
3. `21 -> 22/990` (SFTP/FTPS instead of FTP)
4. `110 -> 995` (POP3S)
5. `143 -> 993` (IMAPS)
6. `389 -> 636` (LDAPS)

## Acceptance Criteria

1. Every open listening port is either approved or explicitly flagged.
2. Every insecure port includes a replacement recommendation.
3. Every externally bound service (`*`, `0.0.0.0`, `::`) is justified or marked for restriction.
