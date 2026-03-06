---
name: whatsapp-forward
description: Generate VCards, parse invite links, and create forwarding templates
---

# WhatsApp Forward Skill

Utilities for contact sharing, message forwarding, and invite link parsing.

## Usage

```
exec({ cmd: "node <skill_dir>/scripts/forward.js COMMAND [ARGS]" })
```

## Commands

### Generate VCard
```
exec({ cmd: "node <skill_dir>/scripts/forward.js vcard \"John Doe\" \"5511999999999\"" })
```

### Generate Multiple VCards
```
exec({ cmd: "node <skill_dir>/scripts/forward.js multi-vcard '[{\"name\":\"John\",\"phone\":\"5511999999999\"}]'" })
```

### Parse Group Invite Link
```
exec({ cmd: "node <skill_dir>/scripts/forward.js parse-invite \"https://chat.whatsapp.com/ABC123\"" })
```

### Show Forwarding Templates
```
exec({ cmd: "node <skill_dir>/scripts/forward.js template" })
```
