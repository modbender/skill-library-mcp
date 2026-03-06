---
name: whatsapp-validate
description: Check if phone numbers exist in the local Baileys session cache
---

# WhatsApp Validate Skill

Validate whether phone numbers have been seen by the connected WhatsApp account.

## Usage

```
exec({ cmd: "node <skill_dir>/scripts/validate.js COMMAND [ARGS]" })
```

## Commands

### Check Single Number
```
exec({ cmd: "node <skill_dir>/scripts/validate.js check \"5511999999999\"" })
```

### Batch Check
```
exec({ cmd: "node <skill_dir>/scripts/validate.js batch \"5511999999999,5511888888888\"" })
```

### List Known Numbers
```
exec({ cmd: "node <skill_dir>/scripts/validate.js list 50" })
```

## Note

This skill checks the local cache only. A number not found may still have WhatsApp — it simply hasn't interacted with the bot yet.
