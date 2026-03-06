# Validator Patterns — Self Discipline

Validators are executable scripts that enforce rules automatically. They make "don't do X" actually impossible, not just a suggestion.

## Why Validators Beat Instructions

```
┌─────────────────────────────────────────────────────────────┐
│                 INSTRUCTION vs VALIDATOR                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Instruction: "Never send secrets in messages"            │
│   - Relies on model memory                                  │
│   - Can be "forgotten" in long context                     │
│   - No enforcement mechanism                                │
│   - Failure = secret sent                                   │
│                                                             │
│   Validator: pre-send/no-secrets.sh                        │
│   - Runs before every send                                  │
│   - Cannot be bypassed                                      │
│   - Explicit failure with explanation                       │
│   - Failure = message blocked                               │
│                                                             │
│   The validator makes the instruction redundant.            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Validator Types

### Pre-Commit Validators

Run before git commits. Location: `~/self-discipline/validators/pre-commit/`

```bash
#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
# Environment variables accessed: none
# External endpoints called: none
# Local files read: staged files via git
# Local files written: none

# Validator: no-secrets-in-code
# Incident: INC-002

# Check staged files for secrets
STAGED=$(git diff --cached --name-only)

for file in $STAGED; do
  if grep -qE '(api_key|password|secret)\s*=' "$file" 2>/dev/null; then
    echo "❌ BLOCKED: Potential secret in $file"
    echo "Rule: no-secrets-in-code (INC-002)"
    exit 1
  fi
done

exit 0
```

### Pre-Send Validators

Run before sending messages/outputs. Location: `~/self-discipline/validators/pre-send/`

```bash
#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
# Environment variables accessed: none
# External endpoints called: none
# Local files read: message content (argument $1)
# Local files written: none

# Validator: no-urls-with-secrets
# Incident: INC-001
# Severity: CRITICAL

MESSAGE="$1"

# Check for URLs with auth parameters
if echo "$MESSAGE" | grep -qE 'https?://[^\s]*[?&](pass|password|token|key|secret|auth)='; then
  echo "❌ BLOCKED: URL contains embedded credentials"
  echo "Rule: no-urls-with-secrets (INC-001)"
  echo ""
  echo "The URL contains a query parameter that looks like a secret."
  echo "Do not send URLs with ?pass=, ?token=, ?key=, etc."
  exit 1
fi

exit 0
```

### Pre-Action Validators

Run before specific dangerous actions. Location: `~/self-discipline/validators/pre-action/`

```bash
#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
# Environment variables accessed: none
# External endpoints called: none
# Local files read: none
# Local files written: none

# Validator: confirm-delete
# Incident: INC-003

ACTION="$1"
TARGET="$2"

if [[ "$ACTION" == "delete" ]]; then
  # Check if target is in protected paths
  PROTECTED_PATHS=(
    "/opt/docker"
    "/etc"
    "~/.ssh"
    "~/clawd"
  )
  
  for path in "${PROTECTED_PATHS[@]}"; do
    if [[ "$TARGET" == "$path"* ]]; then
      echo "⚠️ CONFIRMATION REQUIRED"
      echo "Attempting to delete in protected path: $TARGET"
      echo "Rule: confirm-delete (INC-003)"
      echo ""
      echo "Please confirm with user before proceeding."
      exit 1
    fi
  done
fi

exit 0
```

### Periodic Validators

Run on heartbeat or schedule. Location: `~/self-discipline/validators/periodic/`

```bash
#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
# Environment variables accessed: none
# External endpoints called: none
# Local files read: ~/self-discipline/rules.md
# Local files written: ~/self-discipline/validator-log.md

# Validator: rules-integrity
# Purpose: Verify rules.md hasn't been corrupted

RULES_FILE="$HOME/self-discipline/rules.md"

if [[ ! -f "$RULES_FILE" ]]; then
  echo "⚠️ WARNING: rules.md missing"
  exit 1
fi

# Check file isn't empty
if [[ ! -s "$RULES_FILE" ]]; then
  echo "⚠️ WARNING: rules.md is empty"
  exit 1
fi

# Check it has the expected header
if ! grep -q "^# Active Discipline Rules" "$RULES_FILE"; then
  echo "⚠️ WARNING: rules.md header missing or corrupted"
  exit 1
fi

echo "✅ rules.md integrity verified"
exit 0
```

## Validator Template

```bash
#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
# Environment variables accessed: [list or "none"]
# External endpoints called: [list or "none"]
# Local files read: [list or "none"]
# Local files written: [list or "none"]

# Validator: [kebab-case-name]
# Created: YYYY-MM-DD
# Incident: INC-XXX
# Severity: critical | medium
# Description: [One line description]

# Input:
# $1 = [what the first argument contains]
# $2 = [optional second argument]

# --- Validation Logic ---

[your checks here]

# On failure:
if [failure condition]; then
  echo "❌ BLOCKED: [Reason]"
  echo "Rule: [rule-name] (INC-XXX)"
  echo ""
  echo "[Additional context or help]"
  exit 1
fi

# On success:
exit 0
```

## Integration Points

### With Git

Add to `.git/hooks/pre-commit`:

```bash
#!/usr/bin/env bash

# Run all pre-commit validators
for validator in ~/self-discipline/validators/pre-commit/*.sh; do
  if [[ -x "$validator" ]]; then
    if ! "$validator"; then
      exit 1
    fi
  fi
done
```

### With Agent Runtime

The agent should check validators before:
- Sending messages (pre-send)
- Executing dangerous actions (pre-action)
- Committing code (pre-commit)

### With Heartbeat

Add to HEARTBEAT.md:

```markdown
## Discipline Check
Every heartbeat, run periodic validators:
~/self-discipline/validators/periodic/*.sh
```

## Best Practices

### 1. Validators NEVER Modify

A validator only checks and returns pass/fail. It should never:
- Delete files
- Modify content
- Send messages
- Make API calls

### 2. Clear Error Messages

When blocking, always include:
- What was blocked
- Why (the rule)
- Reference to incident
- How to fix (if applicable)

### 3. Include Security Manifest

Every script must declare what it accesses. This is auditable.

### 4. Test Before Deploying

```bash
# Test a validator
echo "test message" | ~/self-discipline/validators/pre-send/no-secrets.sh -

# Or for validators that take arguments
~/self-discipline/validators/pre-action/confirm-delete.sh delete /opt/docker
```

### 5. Version Control Validators

Keep validators in git. They're code and should be reviewed.

## Common Validator Patterns

| Pattern | Type | Checks |
|---------|------|--------|
| Secret detection | pre-send | Passwords, tokens, keys in messages |
| URL validation | pre-send | Auth params in URLs |
| Protected paths | pre-action | Deletions in sensitive directories |
| File format | pre-commit | Required fields, syntax |
| State integrity | periodic | Critical files exist and valid |

## When to Create a Validator

| Severity | Repeat? | Create Validator? |
|----------|---------|-------------------|
| 🔴 CRITICAL | First time | ✅ YES — mandatory |
| 🔴 CRITICAL | Repeat | ✅ YES — with escalation |
| 🟡 MEDIUM | First time | ⚠️ Optional |
| 🟡 MEDIUM | Repeat | ✅ YES — promote to critical |
| 🟢 LOW | Any | ❌ No — instruction sufficient |
