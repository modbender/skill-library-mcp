---
name: whatsapp-chats
description: List, search, and analyze WhatsApp conversations
---

# WhatsApp Chats Skill

Browse and search WhatsApp conversations from the local Baileys session cache.

## Usage

```
exec({ cmd: "node <skill_dir>/scripts/chats.js COMMAND [ARGS]" })
```

## Commands

### List Chats
```
exec({ cmd: "node <skill_dir>/scripts/chats.js list 30" })
```

### Search Chats
```
exec({ cmd: "node <skill_dir>/scripts/chats.js search \"John\"" })
```

### Chat Statistics
```
exec({ cmd: "node <skill_dir>/scripts/chats.js stats" })
```
