---
name: PocketBase
description: Build backends with PocketBase collections, auth, and realtime.
metadata: {"clawdbot":{"emoji":"📦","requires":{"bins":["pocketbase"]},"os":["linux","darwin","win32"]}}
---

## SDK Basics
- Import from `pocketbase` not `pocketbase/dist` — the dist path is internal and breaks on updates
- Always check `pb.authStore.isValid` before using `pb.authStore.model` — expired tokens return stale data without error
- After login, token is auto-attached to requests — no need to manually set Authorization headers

## Fetching Records
- Use `expand` parameter to load relations: `pb.collection('posts').getList(1, 20, { expand: 'author,comments' })`
- Expanded records appear in `record.expand.fieldName` — not directly on the record object
- Filter syntax is SQL-like but uses single quotes: `filter: "status = 'active' && created >= '2024-01-01'"`
- Combine conditions with `&&` and `||`, not `AND`/`OR` — SQL keywords don't work

## Authentication
- Users collection is `users` (lowercase) — `_users` or `Users` returns empty results
- `authWithPassword(email, password)` returns the full user record plus token
- OAuth flow: `authWithOAuth2({ provider: 'google' })` opens popup automatically in browser
- Logout requires both `pb.authStore.clear()` and invalidating server-side if using tokens elsewhere

## Realtime
- Subscribe with `pb.collection('posts').subscribe('*', callback)` — the `'*'` means all record changes
- Callback receives `{ action: 'create'|'update'|'delete', record }` — check action before processing
- Always unsubscribe on cleanup: `pb.collection('posts').unsubscribe()` — orphan subscriptions leak memory

## File Uploads
- Files require FormData, not JSON: `formData.append('document', file)` then pass to `create()`
- Get file URL with `pb.files.getURL(record, record.filename)` — don't construct URLs manually
- Multiple files to same field: append with same key multiple times

## Collection Rules
- Empty rule = blocked for everyone, `""` (empty string) rule = open to everyone — counterintuitive
- Use `@request.auth.id` to reference logged-in user, `@request.data` for submitted data
- Example restrict to owner: `@request.auth.id = user.id` in View/Update/Delete rules

## Hooks (pb_hooks/)
- JavaScript hooks go in `pb_hooks/*.pb.js` — the `.pb.js` extension is required
- Hooks run synchronously and block the request — keep them fast or use routines
- Access app with `$app`, event data with `e` — common: `e.record`, `e.httpContext`

## Admin API
- Admin endpoints need superuser auth, not regular user tokens
- Create admin token: `pb.admins.authWithPassword(email, password)`
- Admin operations use `pb.admins` or `pb.collections`, not `pb.collection()`
