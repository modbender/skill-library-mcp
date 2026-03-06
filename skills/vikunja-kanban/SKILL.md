---
name: Vikunja Kanban Skill
description: Manage a Vikunja kanban board via API. Read status,
  create/move/complete tasks, and integrate with heartbeat and triage crons.
---

# Vikunja Kanban Skill

Manage a Vikunja kanban board via API. Read status, create/move/complete tasks, and integrate with heartbeat and triage crons.

## Config

Credentials stored in `secrets/vikunja.env`:
```
VIKUNJA_URL=https://your-vikunja-instance
VIKUNJA_TOKEN=${VIKUNJA_TOKEN}
VIKUNJA_PROJECT_ID=1
VIKUNJA_VIEW_ID=4
```

## Authentication

All scripts use a **long-lived API token** (expires 2030-01-01). No JWT login needed.
- Permissions: tasks (read_all, update, create, delete), projects (read_all, update, create)
- JWT login credentials kept in `secrets/vikunja.env` for reference only

## Bucket IDs

| ID | Name | Purpose |
|----|------|---------|
| 1 | 🔴 Urgent | Needs immediate attention |
| 2 | ⏳ Waiting On | Sent/requested, awaiting reply |
| 7 | ⚠️ System Issues | Infra/system problems |
| 8 | 🚧 Active Projects | In progress |
| 9 | 📅 Upcoming | Scheduled/future |
| 10 | 📥 Inbox | New items, untriaged |
| 3 | ✅ Done | Completed |

## Scripts

All scripts are in the skill's `scripts/` directory. Run from the skill root.

### Read the board
```bash
bash scripts/vikunja-status.sh              # All buckets
bash scripts/vikunja-status.sh "Urgent"     # Filter by bucket name
```

### Add a task
```bash
bash scripts/vikunja-add-task.sh "Title" "Description" BUCKET_ID [PRIORITY]
# Priority: 0=unset, 1=low, 2=medium, 3=high, 4=urgent
# Example: bash scripts/vikunja-add-task.sh "Fix DNS" "Check records" 1 4
```

### Move a task between buckets
```bash
bash scripts/vikunja-move-task.sh TASK_ID BUCKET_ID
# Example: bash scripts/vikunja-move-task.sh 15 3  # Move to Done
```

### Complete a task
```bash
bash scripts/vikunja-complete-task.sh TASK_ID
```

## Heartbeat Integration

The heartbeat cron reads from Vikunja:
```bash
bash scripts/vikunja-status.sh
```
- Check 🔴 Urgent for items aging >1h
- If Vikunja unreachable, fall back to `scripts/nc-status-board.sh read`

## Email Triage Integration

Email triage adds Action Required items to the Inbox bucket:
```bash
bash scripts/vikunja-add-task.sh "Email subject" "Brief description" 10 3
```

## API Reference

- **Base URL:** https://your-vikunja-instance/api/v1
- **Auth:** POST /login with username/password → JWT token (short-lived)
- **Tasks:** PUT /projects/{id}/tasks (create), POST /tasks/{id} (update)
- **Buckets:** POST /projects/{id}/views/{view}/buckets/{bucket}/tasks (move task)
- **Views:** GET /projects/{id}/views/{view}/tasks (list tasks by bucket)
- **Projects:** POST /projects/{id} (update title/settings), GET /projects (list all)
- **Sharing:** PUT /projects/{id}/users `{"username":"...", "right":N}` (add user)
- **Users:** GET /users?s=query (search), POST /user/password (self-service password change)

## Known API Bugs & Gotchas

### Sharing permissions ignored on creation
`PUT /projects/{id}/users` ignores the `right` field — always creates with permission=0 (read-only).
**Workaround:** Set permission directly in PostgreSQL:
```sql
UPDATE users_projects SET permission = 2 WHERE user_id = X AND project_id = Y;
```
Permission values: 0=read-only, 1=read+write, 2=admin

### Default Inbox project cannot be deleted
Every new user gets an auto-created "Inbox" project. `DELETE /projects/{id}` returns error 3012.
**Workaround:** Rename it: `POST /projects/{id}` with `{"title":"New Name"}`

### Password change is self-service only
No admin endpoint to change another user's password. Must login as the target user:
`POST /api/v1/user/password` with `{"old_password":"...", "new_password":"..."}`

### API token creation needs both tasks AND projects permissions
Tokens with only `tasks` permissions cannot read kanban views (returns 401).
Must include: `"permissions":{"tasks":["read_all","update","create","delete"],"projects":["read_all","update","create"]}`

### Token creation endpoint
`PUT /api/v1/tokens` to create, `GET /api/v1/tokens` to list, `DELETE /api/v1/tokens/{id}` to remove.
Required fields: `title`, `expires_at` (ISO-8601), `permissions` (object with permission groups).

## Notes

- **Long-lived API token** used (expires 2030) — no JWT login overhead
- Vikunja uses PUT for creation, POST for updates (unusual)
- Bucket IDs are specific to the Kanban view (view_id=4)
- Project name: "Kit Operations" (renamed from default "Inbox")
- Project shared: Kit (id:1, admin/owner), Alex (id:2, admin via DB fix)
- Token has tasks + projects permissions; covers all kanban operations
- Each user gets a default project that can't be deleted — rename to avoid confusion
