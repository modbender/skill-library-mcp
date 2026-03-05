---
name: linear-browser-automation
description: Automate Linear.app workflows in the OpenClaw-managed browser profile using browser tool actions (open, navigate, snapshot, act). Use when users want UI-based Linear automation such as triage, issue updates, comments, filtering, bulk state changes, and visual verification in the managed OpenClaw browser.
---

# Linear Browser Automation

Automate Linear workflows through UI interactions in the OpenClaw-managed browser.

## Execution mode

- Always use browser profile: `openclaw`
- Always run actions against host browser control
- Reuse an already-open, logged-in Linear tab in the managed browser whenever available.
- Do not open a new Linear tab if an existing authenticated Linear tab can be reused.
- Keep actions in one tab unless explicitly opening a new tab is required by user request.

## Standard workflow

1. Ensure managed browser is running (`profile="openclaw"`).
2. Check existing open tabs in managed browser and prefer a tab already on Linear.
3. If an existing Linear tab is found:
   - focus and reuse that tab
   - snapshot and detect auth state
4. If no Linear tab exists, open/navigate to `https://linear.app/`.
5. If on public landing page / unauthenticated state:
   - automatically navigate to `/login`
   - show a browser alert asking the user to log in to continue
   - wait for authenticated dashboard/workspace state
6. After login is complete and dashboard is visible, continue automatically from the same task context and same tab.
7. Resolve references from the snapshot.
8. Execute deterministic actions (click/type/select/press).
9. Re-snapshot and verify expected state before finishing.

## Required-input policy (hard rule)

For all Linear actions, always collect and confirm required details in chat before executing.

### 1) Create issue

Required fields:
1. Team (or project context that implies team)
2. Title

Optional fields (prompt if missing): description, priority, assignee, labels, due date.

Before submission, always present a summary block and ask:
- **`Proceed? (yes/no)`**

Only proceed on explicit **yes**.
Any other response (no/cancel/edit/silence) means do not submit.

### 2) Edit issue and comment on issue

Required fields:
1. Team name
2. Issue number/identifier (e.g., `POW-123`)

Hard rule:
- Do not run these automations when either team name or issue number is missing.
- If the user gives only title text or a partial reference, ask for the team name and issue number.
- Resolve and open the exact issue from the provided team + issue number before making changes.

### 3) Move issue state

Non-negotiable required fields:
1. Team name
2. Issue number/identifier (e.g., `POW-123`)
3. New state/status (e.g., `Todo`, `In Progress`, `Done`)
4. Comment text to add on the issue

Valid issue statuses (only these are accepted):
- `Backlog`
- `Todo`
- `In Progress`
- `Done`
- `Canceled`
- `Duplicate`

Hard rule:
- Do not run move-state automation when any one of these is missing.
- If state is not explicitly provided, ask for it and wait.
- If comment text is not explicitly provided, ask for it and wait.
- Reject any state value not in the valid-status list and ask user to pick one valid option.
- Do not infer or auto-pick a state unless user explicitly instructs you to choose one.
- Resolve the exact issue from team + issue number first, then apply the requested new state and add the comment.

### Priority validation rule

For any automation that sets or updates issue priority, only accept these values:
- `Urgent`
- `High`
- `Medium`
- `Low`

Hard rule:
- Reject any other priority value and ask for one valid option.

### Required-input conversation contract

When user requests a new issue:

1. Check whether required fields are already provided.
2. Ask only for missing required fields first.
3. Ask optional fields (or accept defaults).
4. Present final summary:
   - Team/Project
   - Title
   - Description
   - Priority
   - Assignee
   - Labels
   - Due date
5. Ask `Proceed? (yes/no)`.
6. Submit only after `yes`.

When user requests edit/comment:

1. Check for team name and issue number first.
2. Ask for whichever is missing.
3. Confirm target in one line (e.g., `Target issue: POW-123 (Powerhouse)`).
4. Execute only after target resolution is unambiguous.

When user requests move-state:

1. Check for team name, issue number, explicit new state, and comment text.
2. Ask for whichever is missing.
3. Confirm target, destination, and comment in one line (e.g., `Target issue: POW-123 (Powerhouse) → In Progress | Comment: <text>`).
4. Execute only after target resolution, new state, and comment are unambiguous.

## Safety + reliability rules

- Prefer stable selectors/refs from fresh snapshot before acting.
- Re-snapshot after major UI transitions.
- If unauthenticated state appears, auto-navigate to login and trigger an in-browser alert instructing the user to log in.
- After user login completes and dashboard is detected, resume the task automatically.
- For destructive actions (delete/archive), require explicit confirmation.
- If team/project context is ambiguous, ask before acting.

## Supported automations

- Open Linear and verify dashboard loaded
- Search/filter issues (team, assignee, state, label)
- Create new issue (with required-input policy)
- Edit issue fields (title, description, priority, due date, labels)
- Move issue state (Backlog/In Progress/Done)
- Add comments
- Bulk triage (limited batch with confirmation)
- Visual verification (post-action snapshot checks)

## Example test prompts (one per supported automation)

Use these prompts verbatim (or with your own team/issue values) to test each supported automation.

### 1) Open Linear and verify dashboard loaded

"Using the linear-browser-automation skill in the OpenClaw-managed browser, open Linear and verify the workspace dashboard is loaded for team `<team_name>`. Return the current page URL, visible workspace/team name, and whether auth is active."

### 2) Search/filter issues

"Using the linear-browser-automation skill in the OpenClaw-managed browser, list issues for team `<team_name>` filtered by assignee `<assignee_name>`, state `<state_name>`, and label `<label_name>`. Return issue identifier, title, state, assignee, labels, due date, and URL. If no issues match, say `No matching issues found`."

### 3) Create new issue

"Using the linear-browser-automation skill in the OpenClaw-managed browser, create a new issue in team `<team_name>` with title `<issue_title>`. Set priority `<priority_name>`, assignee `<assignee_name>`, label `<label_name>`, and due date `<due_date_yyyy-mm-dd>`. Show a summary and ask `Proceed? (yes/no)` before submitting."

### 4) Edit issue fields

"Using the linear-browser-automation skill in the OpenClaw-managed browser, edit issue `<issue_number>` in team `<team_name>`. Update title to `<updated_issue_title>`, set priority to `<priority_name>`, set due date to `<due_date_yyyy-mm-dd>`, and ensure label `<label_name>` is applied. Return issue identifier, updated title, state, priority, assignee, labels, due date, and URL."

### 5) Move issue state

"Using the linear-browser-automation skill in the OpenClaw-managed browser, move issue `<issue_number>` in team `<team_name>` to state `<new_state>` and add this comment: `<comment_text>`. Return issue identifier, title, previous state, new state, assignee, labels, due date, comment posted, and URL."

### 6) Add comments

"Using the linear-browser-automation skill in the OpenClaw-managed browser, add this comment to issue `<issue_number>` in team `<team_name>`: `<comment_text>`. Return issue identifier, title, assignee, current state, comment text posted, and URL."

### 7) Bulk triage

"Using the linear-browser-automation skill in the OpenClaw-managed browser, triage up to `<max_items>` issues in team `<team_name>` where state is `<source_state>` and assignee is empty. For each selected issue, set priority to `<priority_name>` and add label `<label_name>`. Show the candidate list first, ask for confirmation, then apply updates and return the changed issues with before/after fields."

### 8) Visual verification

"Using the linear-browser-automation skill in the OpenClaw-managed browser, open issue `<issue_number>` in team `<team_name>` and perform visual verification only (no edits). Return what is visible for title, state, priority, assignee, labels, due date, and URL, and explicitly state whether each verification check passed or failed."

## Suggested command patterns (agent-side)

### Open Linear in managed profile

- start browser (`profile="openclaw"`)
- open `https://linear.app/`

### Reuse existing tab

- navigate current `targetId` to target URL

### Interaction cycle

- snapshot (refs=aria preferred)
- act (click/type/select/press)
- snapshot and verify

## Failure handling

- Missing element/ref:
  - refresh snapshot
  - retry once with updated refs
- Navigation/login interruption:
  - pause and ask user to complete auth/MFA
- Ambiguous target:
  - ask for disambiguation (team/project/issue)
- Missing required issue fields:
  - keep prompting until provided or user cancels
- No explicit yes on submit confirmation:
  - do not submit

## Completion report format

Return:

- actions performed
- items changed (issue IDs/titles if visible)
- verification checks passed/failed
- any manual follow-up needed
