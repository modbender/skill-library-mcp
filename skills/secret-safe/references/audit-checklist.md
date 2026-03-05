# Skill Security Audit Checklist

Use this checklist when reviewing any skill — yours or a third-party skill from ClawHub —
before enabling it on your OpenClaw instance.

---

## Pre-Install Audit (Third-Party Skills)

Read the full `SKILL.md` before installing. Check each item:

### Credential Handling
- [ ] The skill does NOT ask users to paste secrets into the chat
- [ ] The skill does NOT echo, print, or return any credential value
- [ ] All required credentials are declared via `requires.env` in frontmatter
- [ ] The skill does NOT read `.env` files and dump their contents
- [ ] The skill does NOT store credentials in files it creates

### Shell/Script Safety
- [ ] No `set -x` in bundled scripts (would expose env vars in trace output)
- [ ] No credentials passed as positional arguments (visible in `ps aux`)
- [ ] Scripts use `2>/dev/null` or structured error handling (not raw error echo)
- [ ] Any output piped back to the agent is filtered for sensitive patterns

### Network / Exfiltration
- [ ] The skill only contacts URLs explicitly described in its documentation
- [ ] No unexplained `curl`, `wget`, or `fetch` calls to hardcoded IPs or unusual domains
- [ ] No encoded or obfuscated command strings (base64, eval, etc.)
- [ ] No "prerequisite install" steps that download and execute unsigned binaries

### Filesystem Access
- [ ] The skill only accesses files/paths relevant to its stated purpose
- [ ] The skill does NOT read credential files like `~/.ssh/`, `~/.aws/`, `~/.gnupg/`
- [ ] The skill does NOT access OpenClaw config files (`~/.openclaw/`) unless it's an OpenClaw management skill

### Scope Creep
- [ ] The skill's required permissions match its stated function
  (e.g., a weather skill should NOT need filesystem write access)
- [ ] The skill does NOT have `always: true` in metadata unless that's genuinely needed

---

## Pre-Publish Audit (Your Own Skills)

### Credential Patterns
- [ ] No hardcoded API keys, tokens, or passwords in `SKILL.md` or any bundled files
- [ ] No instructions that ask users for credentials via chat
- [ ] All secret access uses `$ENV_VAR` syntax, not interpolated strings
- [ ] `requires.env` gate in frontmatter for every secret the skill uses

### Output Safety
- [ ] Error messages never reflect credential values
- [ ] Success messages don't include auth tokens from responses (e.g., OAuth access tokens)
- [ ] Log output (if any) strips sensitive fields before writing

### Script Review
- [ ] Ran `grep -r "echo.*KEY\|echo.*TOKEN\|echo.*SECRET\|echo.*PASSWORD" ./` — result clean
- [ ] Ran `grep -r "set -x" ./` — result clean or `set -x` is justified and scoped
- [ ] Ran `grep -rE "curl.*Bearer [a-zA-Z0-9]" ./` to catch hardcoded tokens — result clean

---

## Red Flags That Should Block Installation

Stop immediately and do not install if you see:

🚨 A skill that asks you to run a shell command to "install a prerequisite"
   that isn't from a known package manager (brew, npm, pip, apt)

🚨 A `curl | bash` or `wget | sh` pattern anywhere in the instructions

🚨 Base64-encoded strings being decoded and executed: `echo "..." | base64 -d | bash`

🚨 Instructions to add the skill's author's domain to a trusted list

🚨 A skill with 5 installs and no reviews that promises to do everything a
   popular high-install skill does

🚨 Any mention of sending data to a webhook URL that isn't documented

---

## Quick Scan Commands

Run these from the skill directory before enabling:

```bash
# Check for hardcoded secrets patterns
grep -rEi "(api_key|secret|password|token|bearer)\s*=\s*['\"][a-zA-Z0-9_\-]{10,}" .

# Check for dangerous shell patterns
grep -rE "(curl|wget)\s+.*\|\s*(bash|sh|zsh)" .
grep -r "base64 -d" .
grep -r "eval \$(" .
grep -r "set -x" .

# Check for credential echoing
grep -rEi "echo.*(\$[A-Z_]*KEY|\$[A-Z_]*TOKEN|\$[A-Z_]*SECRET)" .

# Check for file exfiltration patterns
grep -rE "(~/.ssh|~/.aws|~/.gnupg|~/.openclaw)" .
```

All results should be empty or explained by the skill's documented purpose.

---

## Reporting a Suspicious Skill

If you find a skill that fails this audit on ClawHub:

1. Click "Report" on the skill's ClawHub page
2. Use the category "Credential leak" or "Malicious behavior"
3. Paste the specific line(s) that triggered your concern
4. Skills with 3+ unique reports are auto-hidden pending review

You can also open an issue at https://github.com/openclaw/clawhub
