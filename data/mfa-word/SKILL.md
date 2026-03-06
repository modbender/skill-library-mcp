---
name: mfa-word
description: Challenges the user for a secret word before allowing access to sensitive files or system commands.
metadata:
  openclaw:
    category: security
    tags: [security, mfa, privacy, zero-trust, audit-logs]
---

# MFA Word (Security Gatekeeper)

## Operational Protocol
1. **Detection:** Before you (the AI) perform any action involving sensitive patterns (like .env, .ssh, passwords, or deletions), you MUST call `check_gate_status`.
2. **Standard Mode:** If `check_gate_status` returns "OPEN", you may proceed. This session is valid for 15 minutes.
3. **Dead Man's Switch:** If `check_gate_status` returns "OPEN_ONCE", perform the requested task, then immediately inform the user that the session has re-locked for security.
4. **Challenge:** If `check_gate_status` returns "LOCKED", you must stop and say: "This request involves sensitive data. Please provide your Secret Word to continue."
5. **Validation:** Once the user provides a word, call `verify_access`. Only proceed if it returns "Access Granted."

## Tools

### initialize_mfa
Sets up the security layer and user preferences.
- `secret`: The primary secret word.
- `super_secret`: The emergency reset word.
- `sensitive_list`: Array of strings or patterns to protect (default: .env, password, config, sudo).
- `use_dead_mans_switch`: Boolean. If true, the gate locks after every single sensitive action.

### verify_access
Validates the secret word provided by the user.
- `word`: The word provided by the user in chat.

### check_gate_status
Internal tool to check if the current session is authenticated.

### reset_mfa
Resets the secret word using the super secret word.
- `super_word`: The emergency reset word.
- `new_secret`: The new primary secret.