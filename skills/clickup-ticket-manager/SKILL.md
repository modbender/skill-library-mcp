---
name: clup
description: ClickUp Ticket Manager. Create tasks in ClickUp with quality descriptions (2-3 sentences minimum).
---

# ClickUp Ticket Manager

**CLI tool: `clup.sh` (or `clup` if symlinked)**

**Prerequisites:**
- Script must be executable: `chmod +x clup.sh`
- Required ENV variables: `CLICKUP_API_KEY`, `CLICKUP_DEFAULT_LIST_ID`
- Optional: Create symlink for system-wide access

## When to Use

User says:
- "Create a ticket for..."
- "Make a task for..."
- "I need a reminder for..."
- "Add a ClickUp ticket for..."

## Your Job

**Transform vague input into quality tickets with context!**

### Quality Rules

1. **Title:** Short, clear, actionable
2. **Description:** MINIMUM 2-3 sentences with:
   - **What** needs to be done?
   - **Why** / **What for**?
   - **Context** (system, server, user, etc.)
3. **If input is vague:** ASK before creating!

### Example Transformation

❌ **User:** "ticket for firewall rule"

✅ **You create:**
```bash
./clup.sh --title "Firewall Rule for Production System" \
     --description "Open port 443 from server web-01 (10.0.1.5) to db-prod (10.0.2.10). Required for API communication after migration. Coordination with network team needed."
```

## Command

```bash
# Basic (use ./clup.sh or clup depending on installation)
./clup.sh --title "..." --description "..."

# With priority
./clup.sh --title "..." --description "..." --priority high
# Priority: urgent, high, normal, low (optional)

# With custom tags
./clup.sh --title "..." --description "..." --tags "bug,urgent,backend"
# Tags: comma-separated list (optional)
```

**Note:** If installed via symlink, use `clup` instead of `./clup.sh`

## Response

After success, show the user the ClickUp URL so they can click through.

## Notes

- Default tags are automatically added (configurable via `CLICKUP_DEFAULT_TAG`, comma-separated)
- Default status: "BACKLOG" (configurable via `CLICKUP_DEFAULT_STATUS`)
- Default list: Set via `CLICKUP_DEFAULT_LIST_ID`
- For help/options: `./clup.sh --help`


