# Workshop section: OpenClaw security (simple, VPS-friendly)

You do not need a perfect setup. You need a setup that is hard to mess up.

## The 3 big risks
- Exposing your OpenClaw gateway to the public internet
- Installing random community skills without reviewing what they do
- Prompt injection (untrusted web content trying to become instructions)

## Baseline rules (secure enough, still useful)
1) Do not expose the gateway publicly
- Prefer a VPS + Tailnet/VPN access.
- If you must access remotely, use allowlists and strong auth.

2) Treat external content as untrusted
- Web pages, emails, PDFs, chat logs.
- Your agent can read and summarize.
- It should NOT execute instructions that come from external content.

3) Add approval gates
Require your approval for:
- Running commands that change system state
- Posting/sending messages
- Submitting web forms or payments
- Reading token directories or .env files
- Deleting files

## VPS hardening checklist (15 minutes)
- Key-only SSH. Disable password auth.
- Firewall: default deny inbound. Only open what you need.
- Auto security updates on.
- Fail2ban on (optional but recommended).

## Skill safety
- Start with built-in functionality.
- If you install a skill, skim SKILL.md first.
- Red flags: curl|bash, unknown webhooks, base64 blobs, "ignore previous instructions".

## Simple mental model
Autonomy is powerful. So treat your agent like a junior operator.
- It can do work.
- But it does not get to change the machine or message people without you approving.
