---
name: whatsapp-utils
description: Phone number formatting, cache inspection, contact export, and message ID generation
---

# WhatsApp Utils Skill

Miscellaneous utilities for WhatsApp automation.

## Usage

```
exec({ cmd: "node <skill_dir>/scripts/utils.js COMMAND [ARGS]" })
```

## Commands

### Format Phone Number
```
exec({ cmd: "node <skill_dir>/scripts/utils.js format \"(11) 99999-9999\"" })
```

### Clean Phone Number
```
exec({ cmd: "node <skill_dir>/scripts/utils.js clean \"+55 (11) 99999-9999\"" })
```

### Cache Info
```
exec({ cmd: "node <skill_dir>/scripts/utils.js cache-info" })
```

### Export Contacts
```
exec({ cmd: "node <skill_dir>/scripts/utils.js export-contacts" })
```

### Generate Message ID
```
exec({ cmd: "node <skill_dir>/scripts/utils.js gen-id" })
```
