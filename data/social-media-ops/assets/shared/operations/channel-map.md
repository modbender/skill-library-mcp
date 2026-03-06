# Channel Map

_Platform channel routing for this instance. Updated by instance-setup and brand-manager skills._

## Current Setup

- **Platform:** _(set during instance-setup)_
- **Mode:** _(set during instance-setup)_

## System Channels

| Channel | Thread ID | Purpose |
|---------|-----------|---------|
| General | _(none)_ | Cross-brand chat, catch-all |
| Operations | _(set during setup)_ | Schedules, reminders, system notifications |

## Brand Channels

_Brand channels are managed by brand-manager. See `shared/brand-registry.md` for the full brand list._

| Brand ID | Display Name | Thread ID |
|----------|-------------|-----------|

## Routing Rules

- **Brand content** → brand's channel/topic
- **Brand research** → brand's channel/topic
- **Cross-brand** → General
- **Scheduling / cron notifications** → Operations
- **Ambiguous messages** → General

## Mode Reference

| Mode | Description | Brand Isolation |
|------|-------------|----------------|
| DM+Topics | Private chat with forum mode | Per-brand topic in DM |
| Group+Topics | Supergroup with forum mode | Per-brand topic in group |
| DM-simple | Private chat, no topics | Context-based |
| Group-simple | Group chat, no topics | Context-based |

_Format for addressing: `chatId:threadId` (e.g., `-100XXXXXXXXXX:3`)_
