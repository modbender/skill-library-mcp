---
name: whatsapp-common-groups
description: Find groups shared between contacts and check group membership
---

# WhatsApp Common Groups Skill

Discover groups two contacts share, or verify if a number belongs to a specific group.

## Usage

```
exec({ cmd: "node <skill_dir>/scripts/common.js COMMAND [ARGS]" })
```

## Commands

### Find Common Groups
```
exec({ cmd: "node <skill_dir>/scripts/common.js find \"5511999999999\"" })
```

### Check if Number is in Group
```
exec({ cmd: "node <skill_dir>/scripts/common.js check \"5511999999999\" \"groupId@g.us\"" })
```

### List All Known Members Across Groups
```
exec({ cmd: "node <skill_dir>/scripts/common.js all-members 50" })
```
