---
name: skill-security-check
description: Runs VirusTotal-style security checks on OpenClaw/Cursor skills before install, including remote code execution (RCE) and malicious code (obfuscation, exfiltration, backdoors). Use when evaluating a skill from a registry (e.g. ClawHub), before granting OAuth/API credentials, or when the user asks for a security review of a skill.
---

# Skill Security Check

Runs structured security checks against skills (especially from registries) and produces a report similar to VirusTotal-style analysis: purpose vs capability, registry vs SKILL.md consistency, **remote code execution (RCE)**, **malicious code** (obfuscation, backdoors, exfiltration, mining, secret reads), install mechanism, credentials, and persistence/privilege.

## User goals

- **Achieve a Benign safety rating on the skill I made** — Authors use the check (and the author checklist in [reference.md](reference.md)) to fix issues until their skill reports Benign before publishing.
- **Ensure all downloaded skills are Benign** — Before using or trusting any skill obtained from a registry (e.g. ClawHub), a URL, or a shared folder, run this security check. Only treat the skill as safe to use if the verdict is **Benign**; if **Suspicious** or any RCE/malicious findings, do not install or follow "what to consider" (verify source, audit in sandbox, or do not install).

**Agent rule for "ensure all downloaded skills are benign":** Whenever the user installs or adds a skill (e.g. `clawhub install`, download, or copy into skills dir), run the skill security check on that skill. If the verdict is not Benign, show the report and do not recommend using the skill until the user has verified the source or the report is resolved. For existing skills in the user's skills directory, the user can ask to "check all my downloaded skills" or "ensure all my skills are benign" — run the check on each and list which are Benign vs Suspicious.

## Pain points this skill addresses

- **"Is this skill safe to install?"** — Users and agents often see skills on ClawHub or elsewhere with no clear way to judge risk. This skill gives a structured, repeatable checklist and a single verdict (Benign / Suspicious) plus what to consider before installing.
- **"The skill wants my OAuth / API keys"** — Credentials are a common attack surface. The check verifies that credential requirements are declared and proportionate, and recommends test accounts and least privilege so users don’t blindly grant access.
- **"Registry and SKILL.md don’t match"** — When the registry listing omits binaries, install steps, or credentials that SKILL.md requires, installs can fail or users get surprised. The skill flags these mismatches so publishers can fix them or users can decide with full context.
- **"Could it run malicious code or steal my data?"** — Explicit RCE and malicious-code checks (curl|sh, eval, obfuscation, exfiltration, secret reads) address the fear that a skill might execute untrusted code or send secrets off-box. Findings here drive a "do not install" or "audit first" recommendation.
- **"I need one process, not ad-hoc judgment"** — A single, documented flow (purpose → registry consistency → scope → RCE → malicious → install → credentials → persistence) ensures consistent evaluations and report format every time.

## When to use

- User is about to install a skill from ClawHub or another registry and wants a security pass.
- User asks to "check this skill for safety", "security review this skill", or "is this skill safe to install?"
- **User goal: ensure all downloaded skills are benign** — Run the check on every newly added skill and (on request) on all skills in the user's skills dir; only treat Benign as safe to use.
- Skill requests OAuth, API keys, or `client_secret.json` and you need to flag risks.
- Comparing registry listing metadata to the skill's SKILL.md for mismatches.

## Check categories (run in order)

### 1. Purpose & capability

- **Align:** Does the SKILL.md description match the actions/commands it instructs? (e.g. "Google Workspace CLI" ↔ Gmail/Calendar/Drive commands.)
- **Flag:** If the stated purpose and the actual instructions clearly diverge, note it and treat as suspicious.

### 2. Registry vs SKILL.md consistency

- **Required binaries:** Does the registry listing declare the same `requires.bins` / `requires.anyBins` as SKILL.md (or `metadata.openclaw.requires.bins`)? If registry shows none but SKILL.md requires a binary (e.g. `gog`), that’s an inconsistency to call out.
- **Install spec:** Does the registry show an install spec (e.g. Homebrew formula, download URL)? If SKILL.md references a Homebrew tap or install steps but the registry has no install metadata, note the mismatch — it’s unclear whether the platform will install the binary or expect it preinstalled.
- **Credentials:** Does the registry declare `primaryEnv`, `apiKey`, or env vars for credentials? If SKILL.md asks for OAuth `client_secret.json` or env vars but the registry lists none, note the omission so the user can confirm before granting access.

### 3. Instruction scope

- **On-topic:** Instructions should stay within the skill’s stated purpose (e.g. workspace CLI ↔ OAuth setup and CLI commands only).
- **Red flags:** Instructions that tell the agent to read unrelated system files, contact unexpected endpoints, or exfiltrate data — mark as suspicious and warn.

### 4. Remote code execution (RCE)

- **Unsafe execution patterns:** Does the skill tell the agent to run code that comes from the network, user input, or another skill without validation? (e.g. `curl … | sh`, `wget … -O - | bash`, `eval "$(…)"`, running a script URL directly.)
- **Piped installs:** Any instruction to pipe remote content into shell/interpreter (curl/wget to bash/python/node) is high risk — treat as suspicious unless the URL is a well-known, integrity-checked official source.
- **Dynamic code:** Instructions to fetch and execute scripts, or to construct and run commands from untrusted or unvalidated strings (e.g. interpolating user/API data into shell commands without sanitization).
- **Privileged execution:** Running as root, with sudo, or modifying system paths so that later commands run in a privileged context — escalates impact of any RCE.

### 5. Malicious code

- **Obfuscation:** Heavily obfuscated scripts or base64/encoded blobs that are decoded and executed — flag for review; legitimate installers rarely rely on this.
- **Backdoors / persistence:** Instructions or scripts that add user accounts, SSH keys, cron jobs, or LaunchAgents not clearly tied to the skill's stated purpose.
- **Data exfiltration:** Sending credentials, keys, or local files to remote servers (other than declared APIs the user expects, e.g. OAuth callback). Any undisclosed or secondary endpoint is suspicious.
- **Cryptomining / abuse:** Instructions that run long-running CPU-heavy processes, miners, or resource abuse; or that use the host for proxy/relay without clear disclosure.
- **Sensitive reads:** Telling the agent to read `~/.ssh`, `~/.aws`, `.env`, or other secrets and pass them to a remote service or script — treat as malicious unless explicitly required and disclosed for a known, trusted integration.

### 6. Install mechanism

- **Declared install:** Is the install method (e.g. `brew install …`, third-party tap, download) clearly stated and consistent between registry and SKILL.md?
- **Third-party taps/scripts:** Installing from a third-party Homebrew tap or running install scripts is moderately risky if the source isn’t trusted. Recommend: verify upstream repo/releases and prefer manual install + test before trusting automated install.

### 7. Credentials

- **Proportionate:** Requesting OAuth or API keys for a Google/API-focused skill is expected; note whether scope is least-privilege (e.g. test account, limited scopes).
- **Declared:** If the skill needs credentials, they should appear in registry metadata (e.g. `primaryEnv`, `skills.entries.<name>.apiKey`) so the platform and user know what’s required.
- **Recommendation:** Prefer a dedicated/test account and least privilege; do not grant primary account access if uncomfortable.

### 8. Persistence & privilege

- **always:true:** Skills that load on every run have higher impact; note if present.
- **System-wide changes:** Does the skill install LaunchAgents, cron jobs, or modify system config? If yes, state clearly in the report.
- **User-invocable / autonomous:** Note if the skill is user-invocable or allowed to run autonomously; not a standalone red flag but part of the overall risk picture.

## Output format (report to user)

Produce a short report with:

1. **Verdict:** Benign / Suspicious (low / medium / high confidence). One line.
2. **Purpose & capability:** ✓ Aligned or ⚠ mismatch (one sentence).
3. **Registry vs SKILL.md:** ✓ Consistent or ⚠ list specific mismatches (binaries, install, credentials).
4. **Instruction scope:** ✓ On-topic or ⚠ red flags (e.g. unexpected file access, endpoints).
5. **Remote code execution (RCE):** ✓ No unsafe patterns or ⚠/🔴 list (e.g. curl|sh, eval of remote input, unvalidated command construction). Any RCE pattern raises confidence of "Suspicious".
6. **Malicious code:** ✓ No signs or ⚠/🔴 list (obfuscation, backdoors, exfiltration, mining, secret reads to remote). Any finding here strongly favors "Suspicious" and may warrant "do not install".
7. **Install mechanism:** ✓ Clear and consistent or ⚠ third-party/undeclared (and recommendation).
8. **Credentials:** ✓ Declared and proportionate or ⚠ undeclared / broad scope (and recommendation).
9. **Persistence & privilege:** ✓ No concerning persistence or ⚠ list (always:true, system changes).
10. **What to consider before installing:** 3–5 bullet points (verify source, install manually if unsure, use test account, clarify registry vs SKILL.md with publisher if needed, do not grant primary account access if uncomfortable; if RCE/malicious findings, recommend do not install or audit scripts first).

## What to consider before installing (template)

When the report is suspicious or has inconsistencies, include guidance like:

- Verify the upstream project/homepage and any tap or install source; inspect repo and releases.
- Prefer installing any required binary yourself and testing it independently before trusting an automated installer.
- Only provide OAuth/API credentials from an account you control; prefer a dedicated/test account with least privilege.
- If registry and SKILL.md disagree on install/requirements, ask the publisher to align them.
- If uncomfortable, do not grant access to primary accounts; consider running the CLI or tool locally instead.
- If RCE or malicious code signs were found, recommend do not install or audit scripts in a sandbox first.

## Usage examples

**User asks for a safety check:**
- *"Run a security check on the gog-cli skill from ClawHub."* → Load the skill’s SKILL.md (and registry listing if available), run all check categories in order, output the 10-point report and "What to consider before installing."
- *"Is this skill safe to install?"* / *"Security review this skill."* → Same: run the check and return the report.

**Before recommending install:**
- User says *"Install the X skill"* and the skill is from a registry or requests credentials → Run this security check first; if verdict is Suspicious or there are RCE/malicious findings, show the report and recommend verifying source or not installing before proceeding.

**Self-check or local skill:**
- *"Run the skill security check on gateway-guard"* → Evaluate the workspace skill (no registry); report N/A for registry vs SKILL.md, still run RCE, malicious code, install, credentials, persistence. Output the same report format.

**Concrete prompt to trigger the check (for users):**
- "Check this skill for safety"
- "Security review [skill name]"
- "Is [skill] safe to install?"
- "Run skill security check on [skill name or path]"

## For authors: Achieving a Benign rating

If you publish a skill and want it to receive a **Benign** verdict when evaluated by this check:

- **Purpose & capability:** Keep your SKILL.md description and instructions aligned; no hidden or off-topic actions.
- **Registry vs SKILL.md:** If the skill is on a registry, declare the same requirements in both places: required binaries, install spec (if any), and credentials (primaryEnv / apiKey / env).
- **No RCE:** Do not instruct the agent to run `curl|sh`, `wget|bash`, eval of remote/user input, or unvalidated command construction; avoid root/sudo for remote or dynamic code.
- **No malicious patterns:** No obfuscation, backdoors, undisclosed exfiltration, mining, or reading secrets and sending to remote. Document any persistence (LaunchAgent, cron) and privilege clearly.
- **Install & credentials:** Document install steps and required credentials; recommend test accounts and least privilege where relevant.
- **Run the check yourself:** Before publishing, run "Run skill security check on [your skill]" and fix any ⚠ or 🔴 findings.

Full author checklist and details: [reference.md](reference.md#for-skill-authors-how-to-achieve-a-benign-safety-rating).

## Additional resources

- Detailed checklist and example report: [reference.md](reference.md)
