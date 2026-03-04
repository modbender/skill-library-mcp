token-usage-tracker

Overview

This skill provides a set of example scripts to track per-call token usage, normalize timestamps, and compress large contexts before sending them to an LLM.

Installation (manual)

1. Review scripts in `scripts/` and adjust paths/config as needed.
2. Copy desired scripts into your active workspace or reference them from the skill folder.
3. Optionally set up systemd units found in `references/systemd/` (examples only).

Defaults

- Timezone: UTC
- Log folder: ./skills/logs (relative to OpenClaw workspace)

Notes

- The scripts are intentionally minimal and well-commented. They are safe to read and run but will not modify system services automatically.
- If you want, I can package this into a .skill file and run local tests. Say "package" to proceed.
