# Examples

## Add task with project and due date
User: “Add ‘Call plumber’ to project house due Friday, high priority.”
Command: `task add project:house due:friday priority:H "Call plumber"`

## List due this week
User: “What’s due this week?”
Command: `task due.before:eow list`

## Modify metadata
User: “Add tag email to task 7 and move it to project work.”
Command: `task 7 modify +email project:work`

## Complete
User: “Mark task 12 done.”
Command: `task 12 done`
