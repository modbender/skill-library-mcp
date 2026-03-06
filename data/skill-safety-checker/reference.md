# Skill Security Check — Reference

## Usage examples

**Example 1 — User asks for a check before installing from ClawHub**

- **User:** "I'm about to install the 'gog-cli' skill from ClawHub. Run a security check on it."
- **Agent:** Loads the skill's SKILL.md and (if available) registry metadata, runs all eight check categories, then outputs the report (verdict, purpose, registry vs SKILL.md, scope, RCE, malicious, install, credentials, persistence, what to consider). For gog-cli-style skills the report might show "Suspicious — medium confidence" with registry/SKILL.md mismatches and credential recommendations.

**Example 2 — User asks generically if a skill is safe**

- **User:** "Is the gateway-guard skill safe to install?"
- **Agent:** Applies this skill's checklist to gateway-guard (workspace skill). Reports "Benign"; notes N/A for registry, no RCE/malicious patterns, optional LaunchAgent documented. Includes "what to consider" (e.g. backup openclaw.json, run read-only first).

**Example 3 — Agent runs check before recommending install**

- **User:** "Install the calendar-sync skill from ClawHub."
- **Agent:** Before running `clawhub install` or equivalent, runs the skill security check on calendar-sync. If verdict is Benign and no high-severity findings, proceeds with install and summarizes. If Suspicious or RCE/malicious findings, returns the report and recommends verifying source or not installing rather than installing blindly.

**Example 4 — Self-check (skill checks itself)**

- **User:** "Run the skill security check on the Skill Security Check skill."
- **Agent:** Evaluates the Skill Security Check skill's own SKILL.md and reference.md. Reports Benign: no binaries, no install, no credentials, no RCE or malicious patterns; suggests adding registry metadata if ever published.

---

## For skill authors: How to achieve a Benign safety rating

Use this checklist when building or publishing a skill so it passes the security check as **Benign**.

| Check category | What to do (author actions) |
|----------------|-----------------------------|
| **Purpose & capability** | Write a clear description in SKILL.md that matches every action the skill instructs. Avoid scope creep or hidden behaviors. |
| **Registry vs SKILL.md** | If you publish to ClawHub or another registry, make registry metadata match SKILL.md: same `requires.bins` / `requires.anyBins`, same install spec (e.g. Homebrew formula or download URL), and declare any credentials (`primaryEnv`, `apiKey`, env vars) in both places. |
| **Instruction scope** | Instructions should only reference files, endpoints, and actions that fit the stated purpose. Do not tell the agent to read unrelated system files or send data to undeclared endpoints. |
| **Remote code execution (RCE)** | Do **not** instruct the agent to: run `curl … \| sh` or `wget … \| bash`; use `eval` on remote or user-supplied input; build shell commands from unvalidated strings; or run remote/dynamic code as root or with sudo. Use fixed, local scripts or well-known installers with integrity checks. |
| **Malicious code** | No obfuscated or base64-executed blobs. No adding SSH keys, user accounts, or persistence (cron, LaunchAgent) unless clearly tied to the skill’s purpose and documented. No sending credentials or secrets to any server except declared APIs (e.g. OAuth callback). No mining, proxy, or undisclosed resource abuse. Do not instruct reading `~/.ssh`, `~/.aws`, `.env` etc. and sending to a remote service unless it’s an explicit, disclosed part of a trusted integration. |
| **Install mechanism** | Document how the skill is installed (e.g. copy to skills dir, `brew install`, or a specific script). If using a third-party tap or download, name it and recommend users verify the source. Keep registry install spec in sync. |
| **Credentials** | If the skill needs OAuth, API keys, or env vars, declare them in SKILL.md and in registry metadata. Recommend a test account and least-privilege scopes where applicable. |
| **Persistence & privilege** | If the skill installs a LaunchAgent, cron job, or changes system config, say so clearly in SKILL.md (and registry if applicable). Avoid `always: true` unless necessary; document what runs when. |

**Before you publish:** Run the skill security check on your own skill (e.g. *"Run skill security check on [my-skill-name]"*). Fix any **Suspicious** verdict or ⚠/🔴 findings until the report shows **Benign** and all categories ✓. That gives users and the platform confidence to install.

---

## Ensuring all downloaded skills are benign

**User goal:** Only use skills that pass the security check as **Benign**. No exceptions for "convenience" — if the verdict is Suspicious or there are RCE/malicious findings, do not install or use until the user has verified the source or accepted the risk.

### Check-before-install policy

1. **Before installing any skill** (e.g. `clawhub install <slug>`, or adding a skill from a URL or shared folder): Run the skill security check on that skill (using its SKILL.md and any scripts; registry metadata if available).
2. **If verdict is Benign** and no ⚠ in critical categories (RCE, malicious): Proceed with install or add to skills dir; optionally show a one-line summary (e.g. "Skill X: Benign — safe to use").
3. **If verdict is Suspicious** or there are RCE/malicious findings: Do **not** install or recommend use. Show the full report and "What to consider before installing." Recommend: verify upstream source, audit scripts in a sandbox, or do not install. Only if the user explicitly overrides (e.g. "I've verified the source, install anyway") should the agent proceed.

### After download (already installed skills)

- **"Check all my downloaded skills"** / **"Ensure all my skills are benign"**: For each skill in the user's skills directory (e.g. `~/.openclaw/skills/`, workspace `skills/`, or `.cursor/skills/`), run the security check. Output a short table or list: skill name → Verdict (Benign / Suspicious). For any Suspicious skill, include the report or a link to it and recommend removing or not using until verified.
- **Periodic audit:** Users can ask the agent to run this sweep after bulk installs (e.g. `clawhub sync --all`) or when adding a new skills source.

### Where skills live (so you know what to check)

- **OpenClaw:** `~/.openclaw/skills/<skill-name>/`, workspace `<workspace>/skills/<skill-name>/`. Extra dirs via `skills.load.extraDirs` in `openclaw.json`.
- **Cursor:** `~/.cursor/skills/<skill-name>/`, project `.cursor/skills/<skill-name>/`.
- **ClawHub:** Installed skills end up in one of the above; after `clawhub install X`, the skill is in the configured skills dir — run the check on that path.

### Summary rule

**Only treat a skill as safe to use if the security check reports Benign.** For any other verdict, show the report and do not recommend use until the user has verified the source or accepted the risk.

---

## VirusTotal-style report example (suspicious, medium confidence)

**Verdict:** Suspicious — medium confidence.

**Purpose & capability:** The SKILL.md describes a Google Workspace CLI (Gmail, Calendar, Drive, etc.) and the instructions match that purpose. ✓

**Registry vs SKILL.md:** Registry lists no required binaries or install spec; SKILL.md requires the `gog` binary and a Homebrew formula (e.g. steipete/tap/gogcli). Credentials (OAuth, GOG_ACCOUNT) are required by SKILL.md but not declared in registry. ⚠ Inconsistency.

**Instruction scope:** Instructions stay on-topic (OAuth setup, client_secret.json, CLI commands). No instruction to read unrelated files or exfiltrate to unexpected endpoints. ✓

**Remote code execution (RCE):** No piped remote installs or eval of untrusted input in the instructions. ✓

**Malicious code:** No obfuscation, backdoors, exfiltration, or secret reads to remote. ✓

**Install mechanism:** No install spec in registry; SKILL.md includes Homebrew install. Third-party tap is moderately risky if source is not trusted. ⚠ Verify tap and prefer manual install.

**Credentials:** OAuth client_secret.json and account setup are proportionate for a workspace CLI. Not declared in registry. ⚠ Confirm before granting; use test account and least privilege.

**Persistence & privilege:** Skill does not request always:true or system-wide persistence. User-invocable / autonomous as per platform default. ✓

**What to consider before installing:**

1. Verify upstream (e.g. https://gogcli.sh) and the Homebrew tap; inspect repository and releases.
2. Install the `gog` binary yourself and test it before relying on an automated installer.
3. Use a dedicated/test Google account with least-privilege scopes; do not grant primary account access if uncomfortable.
4. Ask the publisher why registry shows no install/binaries while SKILL.md references them.
5. If unsure, run the CLI locally instead of granting the agent access.

---

## Checklist (copy when running checks)

- [ ] Purpose in SKILL.md matches described actions/commands
- [ ] Registry `requires.bins` / `requires.anyBins` matches SKILL.md (or metadata.openclaw.requires)
- [ ] Registry install spec (if any) matches SKILL.md install instructions
- [ ] Credentials (OAuth, API keys, env) declared in registry if required by skill
- [ ] Instructions do not read unrelated system files or exfiltrate to unexpected endpoints
- [ ] **RCE:** No `curl|sh`, `wget|bash`, eval of remote input, or unvalidated command construction; no privileged (root/sudo) execution of remote or dynamic code
- [ ] **Malicious:** No obfuscation, backdoors, undisclosed exfiltration, mining/proxy abuse, or reading secrets (e.g. ~/.ssh, .env) and sending to remote
- [ ] Install method (tap/script/download) is clear; third-party sources called out
- [ ] Persistence (always:true, LaunchAgent, cron) and privilege noted
- [ ] "What to consider before installing" written for the user

---

## OpenClaw metadata locations (where to look)

- **Registry (e.g. ClawHub):** Listing may show install spec, required binaries, homepage, credentials.
- **SKILL.md frontmatter:** `metadata.openclaw.requires.bins`, `requires.anyBins`, `requires.env`, `primaryEnv`, `install` (brew/node/go/uv/download).
- **SKILL.md body:** Install steps, required env vars, OAuth/client_secret instructions, persistence (LaunchAgent, cron).

Compare registry fields to these; any mismatch is worth noting in the report.
