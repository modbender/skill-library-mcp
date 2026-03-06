# Unitask Agent Use Cases (Public Beta)

Unitask is in **public beta**. Anyone can sign up at `https://unitask.app`, create a scoped token in `Dashboard -> Settings -> API`, and connect an AI agent.

## Day-to-Day Matrix (20)

| # | Use Case | Recommended Query/Tool | Support | Gap / Next Patch |
|---|---|---|---|---|
| 1 | What are my tasks for today including overdue? | `list_tasks(view=today,tz=<IANA>,status=todo,limit=100)` | Yes | None |
| 2 | What is coming up this week? | `list_tasks(view=upcoming,tz=<IANA>,window_days=7,status=todo)` | Yes | None |
| 3 | Tasks due in next 3 days | `list_tasks(due_from=<ISO>,due_to=<ISO>,status=todo)` | Yes | None |
| 4 | Tasks starting tomorrow | `list_tasks(start_from=<ISO>,start_to=<ISO>,status=todo)` | Yes | None |
| 5 | Today tasks sorted by priority | `list_tasks(view=today,sort_by=priority,sort_dir=desc)` | Yes | None |
| 6 | Parent tasks only | `list_tasks(parent_id=null,status=todo)` | Yes | None |
| 7 | Subtasks under a parent | `list_tasks(parent_id=<parent_id>,status=todo)` | Yes | None |
| 8 | Filter tasks by tag | `list_tasks(tag_id=<tag_id>,status=todo)` | Yes | None |
| 9 | Create a task | `create_task` | Yes | None |
| 10 | Create a subtask | `create_task(parent_id=<parent_id>)` | Yes | None |
| 11 | Update any task fields | `update_task` | Yes | None |
| 12 | Mark task done / reopen | `update_task_status` | Yes | None |
| 13 | Move subtask to another parent | `move_subtask(dry_run=true|false)` | Yes | None |
| 14 | Merge parent B into A | `merge_parent_tasks(dry_run=true|false)` | Yes | None |
| 15 | Create / rename / delete tags | `create_tag`, `update_tag`, `delete_tag` | Yes | None |
| 16 | Attach / remove tag on task | `add_task_tag`, `remove_task_tag` | Yes | None |
| 17 | Plan my day 9-5 with preview | `plan_day_timeblocks(apply=false)` | Yes | None |
| 18 | Apply approved timeblock plan | `plan_day_timeblocks(apply=true)` | Yes | None |
| 19 | Update onboarding/settings profile | `update_settings` | Yes | None |
| 20 | Mark many tasks done from one prompt | repeated `update_task_status` calls | Partial | Add `batch_update_task_status` tool |

## Quick Prompts

1. "What are my tasks for today including overdue?"
2. "Show what is upcoming in the next 7 days."
3. "List tasks tagged urgent and sort by priority."
4. "Move subtask <id> under parent <id>, preview first."
5. "Merge parent B into parent A, preview then apply."

## Safety Defaults

- Use least-privilege scopes (`read`, `write`, `delete`) for each workflow.
- Use dry-run first for `move_subtask` and `merge_parent_tasks`.
- Confirm destructive actions (`delete_task`, `delete_tag`) before apply.
