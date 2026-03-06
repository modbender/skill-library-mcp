# Setup - Automator

Use this setup when activation preferences are unknown or memory is empty.
This setup phase is read-only and must not create files by itself.
Any local write needs explicit user confirmation first.

## Your Attitude

Be practical and precise.
The user should feel that automation is controlled, observable, and reversible whenever possible.

## Priority Order

### 1. First: Integration Preferences

In the first exchanges, confirm activation behavior:
- Should this skill activate whenever they ask to automate macOS app workflows?
- Should the skill warn proactively before write or delete actions?
- Are there directories or apps that must remain read-only?

### 2. Then: Map Their Automation Surface

Clarify scope before execution:
- Existing `.workflow` files to run.
- Apps and files that workflows can touch.
- Expected output format from each run.

### 3. Finally: Capture Reliability Defaults

If the user wants persistent defaults, store:
- Preferred confirmation level for write and destructive operations.
- Preferred command verbosity and output format.
- Known working workflow paths and action names.

If the user wants minimal setup, apply conservative defaults and continue.

## What You Are Saving Internally

Store only reusable context:
- Activation and safety preferences.
- Verified workflow paths and action patterns.
- Known failure signatures and successful recovery steps.

After memory updates, summarize user-facing impact in plain language.
