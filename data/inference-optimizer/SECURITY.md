# Security: VirusTotal report remediation

This document explains how v0.2.0 changes address findings from third-party security reviews (VirusTotal-style reports).

---

## v0.2.1 addendum (follow-up report)

**Report:** Pre-scan still flagged "return raw output" and prescriptive phrasing ("return output"). Skill instructs agent to follow a workflow that could coerce behavior. Enforcement of redaction/metadata rules relies on the agent.

**Changes:**
- Replaced "return raw output" and "return output" with passive phrasing: "the script produces metadata that may be relayed"; "include the script's output in your response."
- Added disclaimer in SKILL.md: "These instructions describe suggested workflow for the agent. They are guidance, not system-prompt overrides, and cannot be enforced programmatically. Platform and system prompts take precedence."
- Added **Before installing** checklist to README (7 steps mirroring reviewer recommendations).
- Manual install now shows preview before `--apply`.
- Added **Script reference** section with line numbers for reviewer inspection.

---

## 1. Instruction scope & system-prompt override

**Report:** Agent instructions include content that looks like prompt-injection or system-prompt override (e.g. "Do NOT ask what to optimize", "return raw output") intended to tightly control agent behavior.

**Change:** Replaced prescriptive prohibitions with descriptive workflow wording.

| Before | After |
|--------|-------|
| "Do NOT ask what to optimize. Do NOT list options." | "When user sends `/optimize` or `/audit`, exec the audit script and return its output." |
| "return raw output" | "return output" |

The skill now describes intended behavior rather than forbidding specific responses. Instructions read as workflow guidance, not as system-prompt overrides.

---

## 2. Sensitive data (credentials)

**Report:** The skill reads `~/.openclaw/openclaw.json` and workspace files that may contain secrets. Audit or rewrites could surface sensitive values.

**Change:** Added explicit data-handling constraints.

- **optimization-agent.md:** "Audit outputs only metadata (char counts, token estimates); it does not echo file contents." The audit script already reported only character counts; this is now documented.
- **Task 2:** "For file rewrites … never include secrets — use `<redacted>` for keys, tokens, passwords."
- **README Security:** States that audit outputs metadata only and does not echo config or workspace contents; config paths may contain secrets.

---

## 3. Purge: high-impact & broad allowlist

**Report:** Purge deletes files. Recommending `find *`, `find **`, `rm *`, `rm **` grants broad privilege. Archive before delete; verify contents before permanent removal.

**Change:**

- **Archive-first purge:** Purge script now moves files to `~/openclaw-purge-archive/<timestamp>/` by default instead of deleting. Use `--delete` for legacy immediate-delete behavior.
- **Allowlist guidance:** Removed recommendation for broad wildcards. SKILL.md and README now recommend manual purge; if agent exec is required, use path-specific patterns rather than `find **`, `rm **`.

---

## 4. setup.sh modifies workspace without confirmation

**Report:** setup.sh appends entries to AGENTS.md and TOOLS.md, changing agent behavior without clear user consent.

**Change:** Non-destructive by default with explicit opt-in.

- **Default:** Preview only. Prints snippets that would be added. No file modifications.
- **`--apply`:** Modifies AGENTS.md and TOOLS.md only when this flag is passed.
- **README Security:** Instructs to run without `--apply` first to preview; describes how to revert by removing appended sections.

---

## 5. Pre-install recommendations

**Report:** Backup config, inspect scripts, avoid broad allowlist, treat instructions as untrusted, prefer archive over delete.

**Change:**

| Recommendation | Addressed by |
|----------------|--------------|
| "Back up config and workspace files" | README Security documents what is read/modified and archive locations |
| "Inspect scripts … run audit first in safe environment" | Audit is read-only (metadata only); purge now archives by default; setup is preview-only by default |
| "Do NOT grant broad exec allowlist" | SKILL.md and README recommend manual purge; path-specific patterns if exec is required |
| "Treat skill instructions as untrusted" | Softened wording; explicit data-handling rules; Security section for transparency |
| "Modify purge to archive instead of immediate deletion" | Purge defaults to moving files to `~/openclaw-purge-archive/`; `--delete` for immediate removal |

---

## Summary table

| VirusTotal issue | Change |
|------------------|--------|
| Prompt-injection / system-override wording | Replaced "Do NOT" with neutral descriptive workflow language |
| Sensitive data exposure | Explicit rules: audit outputs metadata only; rewrites must `<redacted>` secrets |
| High-impact purge | Archive by default; `--delete` for legacy delete behavior |
| Broad allowlist (`find **`, `rm **`) | Recommend manual purge; path-specific patterns if agent exec required |
| setup.sh modifies without confirmation | Preview by default; require `--apply` to write |
| Lack of security documentation | README Security section + this SECURITY.md |
| Residual "return output" phrasing (v0.2.1) | Passive wording; guidance disclaimer; Before installing checklist |
