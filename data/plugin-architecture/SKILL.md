---
name: Plugin Architecture Skill
description: "name: plugin-architecture version: 1.1.0 author: Charles Sears
  description: Adds UI plugin registration support to OpenClaw - allows plugins
  to register custom tabs in the Control UI."
---

# Plugin Architecture Skill

name: plugin-architecture
version: 1.1.0
author: Charles Sears
description: Adds UI plugin registration support to OpenClaw - allows plugins to register custom tabs in the Control UI.

## Overview

This skill adds the ability for OpenClaw plugins to register custom UI views/tabs that appear in the Control dashboard sidebar.

## Installation

**This skill requires manual installation by your OpenClaw agent.**

After extracting this skill to your skills folder, give your agent this prompt:

```
Please install the plugin-architecture skill. Read the INSTALL_INSTRUCTIONS.md file in the skill folder and follow it step by step. The skill is at: ~/clawd/skills/plugin-architecture/
```

## What It Does

Once installed, plugins can register UI tabs like this:

```typescript
// In your plugin's register() function:
if (typeof api.registerView === "function") {
  api.registerView({
    id: "my-view",
    label: "My View",
    subtitle: "Description here",
    icon: "database",  // Icon name from the icon set
    group: "Agent",    // Which nav group (Chat, Control, Agent, Settings)
    position: 5,       // Order within the group
  });
}
```

## Files Included

- `SKILL.md` - This file
- `INSTALL_INSTRUCTIONS.md` - Step-by-step instructions for the agent
- `reference/` - Reference code files showing what to add
