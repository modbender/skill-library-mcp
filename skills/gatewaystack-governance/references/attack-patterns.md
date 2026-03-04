# Known Attack Patterns — OpenClaw

This document catalogs the specific attack patterns this governance skill is designed to mitigate, with references to the published research that documented them.

## CVE-2026-25253: Cross-Site WebSocket Hijacking → RCE

**Source:** [The Hacker News](https://thehackernews.com/2026/02/openclaw-bug-enables-one-click-remote.html), [SocrADAR](https://socradar.io/blog/cve-2026-25253-rce-openclaw-auth-token/)

**CVSS:** 8.8 (Critical)

**Mechanism:** OpenClaw's Control UI trusts `gatewayUrl` from URL query strings without validation. The server doesn't validate WebSocket origin headers. Attacker crafts a malicious web page that steals the auth token, then uses `operator.admin` and `operator.approvals` scopes to disable confirmations and execute commands on the host.

**What this skill mitigates:** The scope enforcement layer blocks unauthorized tool calls even if the attacker obtains a token. The audit log records all tool invocations, making post-incident reconstruction possible.

## Malicious Skills — Credential Exfiltration

**Source:** [Snyk ToxicSkills](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/), [Cisco AI Security](https://blogs.cisco.com/ai/personal-ai-agents-like-openclaw-are-a-security-nightmare)

**Finding:** 76 confirmed malicious payloads across ClawHub. 283 skills expose API keys and PII in plaintext. Skills exfiltrate credentials to external webhooks, install reverse shell backdoors, and deliver Atomic Stealer malware.

**What this skill mitigates:** The injection detection layer catches webhook exfiltration patterns, reverse shell commands, and credential references in tool arguments. The scope enforcement layer prevents untrusted skills from accessing sensitive tools (Bash, Write, file system).

## Indirect Prompt Injection via Email

**Source:** [Kaspersky](https://www.kaspersky.com/blog/openclaw-vulnerabilities-exposed/55263/)

**Mechanism:** Attacker sends email with injected instructions. Agent reads email, follows embedded instructions, exfiltrates private keys or credentials. No exploit required — the agent can't distinguish user instructions from untrusted data.

**What this skill mitigates:** The injection detection layer scans tool arguments for instruction injection patterns. The identity verification layer ensures tool calls are attributed to a verified user. The audit log captures the full chain of events for post-incident analysis.

## Exposed Instances — Default Network Binding

**Source:** [SecurityScorecard](https://securityscorecard.com), [The Register](https://www.theregister.com/2026/02/09/openclaw_instances_exposed_vibe_code/)

**Finding:** 135,000+ internet-exposed OpenClaw instances. Default binding to `0.0.0.0:18789` exposes the gateway to the public internet. 63% of observed deployments are vulnerable to RCE.

**What this skill mitigates:** This skill operates at the tool-call level, not the network level. However, even if an attacker reaches the agent via an exposed gateway, the governance checks still apply: identity must be verified, tools must be allowlisted, arguments must pass injection detection, and everything is audited.

## Shadow AI Deployments

**Source:** [Bitdefender](https://www.bitdefender.com/en-us/blog/labs/helpful-skills-or-hidden-payloads-bitdefender-labs-dives-deep-into-the-openclaw-malicious-skill-trap)

**Finding:** Employees deploying hundreds of AI agents on corporate machines via single-line commands. No centralized governance, no visibility, no audit trail.

**What this skill mitigates:** The audit logging layer creates a structured record of all agent activity. Combined with the AgentiControlPlane cloud dashboard (Level 2+), organizations gain centralized visibility across all OpenClaw instances.
