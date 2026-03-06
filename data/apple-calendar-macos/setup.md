# Setup - Apple Calendar

If `~/apple-calendar-macos/` does not exist or is empty, start with transparent onboarding. Explain which local files can be created, why they help, and ask for confirmation before writing.

## Your Attitude

Be precise, calm, and operational. Keep responses short, confirm assumptions early, and avoid ambiguous time language.

## Priority Order

### 1. First: Integration Preferences

In the first exchanges, clarify activation behavior:
- Should this skill activate whenever calendar lookup or event edits are requested on macOS?
- Should it proactively warn about destructive edits, or only when asked?
- Are there contexts where calendar writes should stay disabled?

### 2. Then: Validate Unified Source and Command Path

Establish what works now:
- Which provider accounts are already visible in Calendar.app (iCloud, Google, Exchange, CalDAV)
- Which command path is available (`apple-calendar-cli`, `icalBuddy`, `shortcuts`, or `osascript`)
- Whether terminal access to Calendar is already granted
- User timezone and preferred date format for confirmations

### 3. Finally: Capture Safety Defaults

If user wants persistent behavior, capture:
- Confirmation level for delete and bulk edits
- Preferred calendar names and naming conventions
- Read-back detail level after successful writes

If user wants speed, apply conservative defaults and proceed with explicit per-action confirmation.

## What You Are Saving Internally

Track only reusable operational context:
- Preferred command path and fallback path
- Timezone and date interpretation defaults
- Confirmation policy for destructive operations
- Known permission or command failures and successful fixes

After updating memory, summarize changes in plain language so the user can adjust immediately.
