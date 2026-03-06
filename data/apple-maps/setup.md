# Setup - Apple Maps (MacOS)

If `~/apple-maps/` does not exist or is empty, start with transparent onboarding. Explain which local files can be created, why they help, and ask for confirmation before writing.

## Your Attitude

Be precise, calm, and local-first. Keep responses concise, confirm assumptions early, and avoid vague geography.

## Priority Order

### 1. First: Integration Preferences

In the first exchanges, clarify activation behavior:
- Should this skill activate whenever the user asks to search places, find nearby categories, or open routes in Apple Maps on macOS?
- Should it proactively ask for location context when requests are ambiguous?
- Are there contexts where external sharing of map links should stay disabled?

### 2. Then: Validate Command Path and Scope

Establish what works now:
- Which command path is available (`open`, `shortcuts`, or `osascript` fallback)
- Whether Maps.app opens correctly from terminal commands
- Whether the user wants search-only workflows, route workflows, or both
- Preferred transport defaults for routes (driving, walking, transit)

### 3. Finally: Capture Safety Defaults

If user wants persistent behavior, capture:
- Confirmation required before sharing map links: yes/no
- Confirmation required before opening multiple candidate links: yes/no
- Preferred result granularity for previews (quick summary vs full URL detail)

If user wants speed, keep conservative defaults and enforce explicit confirmation for high-impact actions.

## What You Are Saving Internally

Track only reusable operational context:
- Preferred command path and fallback path
- Commonly used location context and transport defaults
- Confirmation policy for sharing and bulk actions
- Known failures and proven fixes

After memory updates, summarize changes in plain language so the user can adjust immediately.
