---
name: whatsapp-contacts
description: List, search, and lookup WhatsApp contacts from the Baileys session cache
---

# WhatsApp Contacts Skill

Read and search contacts stored in the local Baileys WhatsApp session.

## Usage

```
exec({ cmd: "node <skill_dir>/scripts/contacts.js COMMAND [ARGS]" })
```

## Commands

### List Contacts
```
exec({ cmd: "node <skill_dir>/scripts/contacts.js list 50" })
```

### Search by Name or Phone
```
exec({ cmd: "node <skill_dir>/scripts/contacts.js search \"John\"" })
```

### Get Contact Info
```
exec({ cmd: "node <skill_dir>/scripts/contacts.js get 5511999999999" })
```

## Note

This skill reads contacts from the local Baileys session cache. Only contacts that have previously interacted with the connected account will be available.
