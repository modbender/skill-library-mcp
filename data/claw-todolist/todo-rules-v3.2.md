Todo List Yatno V3.2 Methodology:
A custom task management style based on GTD and Eisenhower, designed specifically for chat interaction.

COMPLETE RULES:

ADDING A NEW TASK (ADD) / Alias 'a':
Format: ADD P<priority> @<context> [Task Text] [+ up to +++++] [DUE=<YYYY-MM-DD>]
• Context (@) is MANDATORY. If missing, the Agent will automatically insert @general and provide a notification.
• Weight (+) and Due Date (DUE) are optional.

MARKING AS DONE (DONE) / Alias 'x':
Format: DONE <ID>

EDITING A TASK (EDIT) / Alias 'e':
Format: EDIT <ID> [Changes]
Change Options:
PRIO=<New-P>,
CONTEXT=@<context>,
TEXT=[NewText],
WEIGHT=<+ or NONE>,
DUE=<YYYY-MM-DD>

FILTERING TODO (SHOW) / Alias 'ls':
• Context Filter: SHOW @<context>
• Due Filter: SHOW DUE <24h/48h/Week>
• Weight Filter: SHOW CRITICAL <+ up to +++++>
• Direct Context List: SHOW CONTEXTS (Displays all active contexts)
• Weekly Review: REVIEW (Runs automated structural analysis)

PRIORITY DEFINITIONS:

P1 (Urgent): IMPORTANT & Urgent. Execute immediately.

P2 (Schedule): IMPORTANT & Not Urgent. Schedule it.

P3 (Delegate/Quick): Not Important & Urgent. Delegate or complete quickly.

P4 (Defer): Not Important & Not Urgent. Postpone or eliminate.

Display: Text format. Weight appears as ⭐ icons after the task text.

Implementation:
Error handling for incorrect syntax (e.g., P5 or non-existent ID) will provide explicit corrective responses. Context is mandatory; if omitted, it will automatically be filled with @general.
