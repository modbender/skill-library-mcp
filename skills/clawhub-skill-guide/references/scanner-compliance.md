# Scanner Compliance Deep Dive

After publishing a skill to ClawHub, an automated security scanner evaluates it
across 5 categories. Each category receives a rating:

| Rating | Meaning |
|--------|---------|
| ✓ | Pass — no concerns |
| ℹ | Informational — minor observations, not blocking |
| ! | Warning — significant concerns that reduce trust |

The goal is **all ✓ marks**. This guide covers what triggers each rating and
how to fix issues.

---

## Category 1: PURPOSE & CAPABILITY

**What the scanner checks:**
- Does the description accurately reflect what the skill does?
- Are all external services and credentials declared?
- Are there undeclared capabilities or requirements?

### ✓ Pass

- Description clearly states what the skill does
- All referenced APIs, services, and credentials appear in frontmatter
- `requires` list matches actual dependencies
- No hidden functionality beyond what's described

### ℹ Informational

- Description is vague or overly broad relative to actual functionality
- Minor mismatch between described and actual capabilities

### ! Warning

- Skill accesses services not mentioned in description
- Credentials referenced in body but not declared in frontmatter
- Significant functionality not reflected in description

### Fix Pattern

1. Audit SKILL.md body for every external service, API, or credential mentioned
2. Ensure each appears in the description and `env` / `requires` frontmatter
3. Make description specific — match actual functionality, not aspirational scope

---

## Category 2: INSTRUCTION SCOPE

**What the scanner checks:**
- Do instructions stay within the skill's stated purpose?
- Does the skill instruct the agent to modify system config automatically?
- Are privileged operations properly gated?

### ✓ Pass

- All instructions relate to the skill's declared purpose
- Config changes presented as templates for **manual review**
- Privileged operations documented as requiring explicit user approval
- `requireMention:false` usage documented with data exposure implications

### ℹ Informational

- Instructions slightly broader than description suggests
- Config recommendations exist but aren't clearly marked as manual-review
- `requireMention:false` present without clear documentation

### ! Warning

- Language like "automatically apply," "agent patches config," or "auto-configure"
- Instructions directing the agent to modify gateway config without user review
- Scope creep — instructions for actions beyond the skill's stated purpose

### Fix Pattern

1. Replace all "automatic" config language with "manual review required"
2. Present config changes as templates or examples, not directives
3. Add explicit: "**All config changes require manual review. Nothing is applied automatically.**"
4. If `requireMention:false` is recommended, explain what data the agent will see

---

## Category 3: INSTALL MECHANISM

**What the scanner checks:**
- Do scripts download external code (curl, wget, npm install, pip install)?
- Do scripts write outside the skill workspace?
- Is code obfuscated or minified?
- Are scripts documented and inspectable?

### ✓ Pass

- Scripts only write within the skill workspace directory
- No network calls in scripts (no curl, wget, nc, etc.)
- Code is plain, readable, and documented
- SKILL.md includes "inspect before running" warning
- Script line counts and purposes documented

### ℹ Informational

- Scripts exist but without explicit inspection warning
- Scripts are mostly safe but documentation could be clearer

### ! Warning

- Scripts download external code or resources
- Scripts write to locations outside the skill directory
- Obfuscated or minified executable code
- No documentation of what scripts do

### Fix Pattern

1. Add to SKILL.md:
   ```
   The included scripts only create files within the skill workspace.
   They make no network calls and write no files outside the skill
   directory. **Inspect them before running.**
   ```
2. Remove any curl/wget/network calls from scripts
3. Use relative paths or `$SKILL_DIR` — never absolute system paths
4. Document each script's purpose and line count

→ Full patterns: [script-safety.md](script-safety.md)

---

## Category 4: CREDENTIALS

**What the scanner checks:**
- Are all env vars / credentials declared in frontmatter?
- Are sensitive values marked `sensitive: true`?
- Does the skill request credentials unrelated to its purpose?

### ✓ Pass

- Every env var referenced in the body appears in frontmatter `env:` array
- Sensitive credentials (API keys, tokens, passwords) marked `sensitive: true`
- No requests for credentials outside the skill's scope
- Prerequisites table lists all required accounts/services

### ℹ Informational

- Env vars declared but `sensitive` flag missing on what appears to be a secret
- Minor mismatch between body references and frontmatter

### ! Warning

- Body references credentials not declared in frontmatter at all
- Skill requests credentials unrelated to its stated purpose
- Sensitive credentials without any `sensitive` flag

### Fix Pattern

1. Search SKILL.md body for every env var name, API key reference, token mention
2. Add each to the `env:` array with `name`, `description`, `required`, `sensitive`
3. Mark all keys, tokens, passwords, and secrets as `sensitive: true`
4. Add a Prerequisites table mapping each credential to its source

---

## Category 5: PERSISTENCE & PRIVILEGE

**What the scanner checks:**
- Does the skill recommend `always:true` (always-on activation)?
- Are config changes automatic or gated behind manual review?
- For multi-user skills, is agent isolation recommended?
- Does the skill create persistent background processes?

### ✓ Pass

- No `always:true` recommendations
- Config changes explicitly presented as templates for manual review
- Multi-user or shared skills recommend a separate OpenClaw agent
- No persistent daemons or background processes
- Skill operates within its own workspace boundary

### ℹ Informational

- Multi-user patterns exist but isolation not explicitly recommended
- Config changes mentioned without clear manual-review gating

### ! Warning

- `always:true` recommended without justification
- Config changes presented as automatic directives
- No isolation recommendation for skills that process multi-user data
- Background processes or system-level modifications

### Fix Pattern

1. Never recommend `always:true` unless truly necessary — and justify it
2. Frame all config changes as: "Review this template and apply manually"
3. For multi-user skills, add a Security Model section recommending a dedicated agent
4. Ensure all operations are stateless and workspace-scoped

---

## Case Study: A Debate Moderator Skill

This traces the real progression of a multi-user skill through scanner iterations.

### v1.0.0 — Initial Publish

**Scanner results:**
- PURPOSE & CAPABILITY: ✓
- INSTRUCTION SCOPE: **!** — Instructions told agent to "apply config changes" automatically
- INSTALL MECHANISM: ℹ — Scripts existed but no inspection warning
- CREDENTIALS: **!** — Skill used env vars for API keys but none declared in frontmatter
- PERSISTENCE & PRIVILEGE: ℹ — Multi-user skill without agent isolation recommendation

**Issues identified:**
1. SKILL.md said "add this to your gateway config" as a directive, not a suggestion
2. Env vars referenced in body (`DEBATE_API_KEY`) not in frontmatter
3. Setup scripts had no "inspect before running" documentation
4. No recommendation to run as a separate agent

### v1.1.0 — First Fix Round

**Changes:**
- Added Prerequisites section with requirements table
- Changed all config language from "apply this config" to "review this template"
- Added "inspect before running" note for scripts
- Added basic security notes

**Scanner results:**
- PURPOSE & CAPABILITY: ✓
- INSTRUCTION SCOPE: ℹ — Better but some residual automatic-sounding language
- INSTALL MECHANISM: ✓ — Inspection warning resolved this
- CREDENTIALS: **!** — Body mentioned env vars still not in frontmatter YAML
- PERSISTENCE & PRIVILEGE: ℹ — Still missing explicit isolation recommendation

**Lesson:** Adding a Prerequisites *section in the body* is not enough. The scanner
checks **frontmatter** for credential declarations. Body-only documentation of
env vars does not satisfy the CREDENTIALS check.

### v1.2.0 — Second Fix Round

**Changes:**
- Added `env:` array to frontmatter with all env vars, including `sensitive: true`
- Added `requires:` array listing external dependencies
- Replaced remaining "configure your agent" with "review and manually apply"
- Added explicit: "**All config changes require manual review.**"
- Added Security Model section recommending dedicated agent with restricted permissions
- Documented script line counts and purposes

**Scanner results:**
- PURPOSE & CAPABILITY: ✓
- INSTRUCTION SCOPE: ✓
- INSTALL MECHANISM: ✓
- CREDENTIALS: ✓
- PERSISTENCE & PRIVILEGE: ✓

### Key Takeaways

1. **Frontmatter is king for CREDENTIALS.** Body documentation is for humans;
   the scanner reads frontmatter for credential declarations.
2. **Language matters for INSTRUCTION SCOPE.** "Apply this" → warning.
   "Review and manually apply" → pass.
3. **Script inspection warnings are cheap wins.** One sentence resolves
   INSTALL MECHANISM concerns.
4. **Agent isolation is required for multi-user skills.** A Security Model
   section with "run as a separate agent" satisfies PERSISTENCE & PRIVILEGE.
5. **Iterate with version bumps.** Each publish gets a fresh scan. Bump
   version, fix issues, republish, check again.

---

## Quick Compliance Checklist

Before publishing, verify:

- [ ] `name` and `description` in frontmatter
- [ ] `env:` array declares every credential/env var used in the body
- [ ] Sensitive values marked `sensitive: true`
- [ ] `requires:` lists external dependencies
- [ ] No "automatic" config language — all changes are "manual review"
- [ ] Scripts documented with line counts, purposes, and "inspect before running"
- [ ] No curl/wget/network calls in scripts (or explicitly declared if necessary)
- [ ] Multi-user skills include agent isolation recommendation
- [ ] No `always:true` without clear justification
- [ ] Description matches actual functionality — not broader, not narrower
- [ ] No personal data, test databases, or generated artifacts
