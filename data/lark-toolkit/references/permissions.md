# Lark API Permissions Reference

## Messaging (IM)

| Permission | Description |
|-----------|-------------|
| `im:message` | Send and receive messages in chats |
| `im:message:send_as_bot` | Send messages as bot |
| `im:message.p2p_msg:readonly` | Read direct messages to bot |
| `im:message.group_msg:readonly` | Read group messages mentioning bot |
| `im:message.group_at_msg:readonly` | Read all group messages |
| `im:chat` | Read and update group info |
| `im:chat:readonly` | Read group info |
| `im:chat.members:write_only` | Manage group members |
| `im:resource` | Access message resources (images, files) |

## Contacts

| Permission | Description |
|-----------|-------------|
| `contact:user.base:readonly` | Read basic user info (name, avatar) |
| `contact:user.employee_id:readonly` | Read employee IDs |
| `contact:user.email:readonly` | Read user emails |
| `contact:user.phone:readonly` | Read user phone numbers |
| `contact:department.base:readonly` | Read department info |

## Calendar

| Permission | Description |
|-----------|-------------|
| `calendar:calendar` | Read and write calendars |
| `calendar:calendar:readonly` | Read calendars |
| `calendar:calendar.event:write` | Create/update calendar events |

## Docs & Drive

| Permission | Description |
|-----------|-------------|
| `docs:doc` | Read and write documents |
| `docs:doc:readonly` | Read documents |
| `drive:drive` | Read and write Drive files |
| `drive:drive:readonly` | Read Drive files |
| `wiki:wiki` | Read and write Wiki |
| `wiki:wiki:readonly` | Read Wiki |

## Bitable

| Permission | Description |
|-----------|-------------|
| `bitable:app` | Read and write Base apps |
| `bitable:app:readonly` | Read Base apps |

## Task

| Permission | Description |
|-----------|-------------|
| `task:task` | Read and write tasks |
| `task:task:readonly` | Read tasks |

## OKR

| Permission | Description |
|-----------|-------------|
| `okr:okr:readonly` | Read OKR data |
| `okr:progress:write` | Write OKR progress |

## Notes

- After adding/removing permissions, **publish a new app version** for changes to take effect
- Use minimum required permissions for security
- `tenant_access_token` inherits all granted app permissions
- `user_access_token` (OAuth) is limited to what the user can access
