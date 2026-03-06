# Strict Publish Validation Protocol

This file defines the deterministic publishing validation process.

Publishing is NOT considered successful unless validated.

---

# Publishing Steps

1. Use image-text mode.
2. Submit post.
3. Wait for redirect OR response state change.

---

# Validation Rules

After submission, validate using the following order:

## Method A — URL Check

If URL contains note detail pattern → Tentative success.

## Method B — Management List Check (Mandatory)

Navigate to creator note management page.

Confirm:

- New title exists in list.
- Timestamp matches current publish cycle.

If note appears → SUCCESS.

If not found → Retry once.

If still not found → FAIL and report.

---

# Retry Policy

- Maximum 1 retry per post.
- If retry fails → stop cycle and report.

---

# Hard Rule

Never assume success based on visual refresh alone.
Always confirm list presence.
