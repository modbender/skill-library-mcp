---
name: mac-cleanup
description: Cleans up system caches, trash, and old downloads on macOS.
author: tempguest
version: 0.1.0
license: MIT
---

# Mac Cleanup Skill

This skill helps you reclaim disk space on your MacBook Pro by cleaning up:
- **System Caches**: Clears the user cache directory (`~/Library/Caches`).
- **Trash**: Empties the Trash (`~/.Trash`).
- **Old Downloads**: Deletes files in `~/Downloads` that are older than 30 days.

## Commands

- `cleanup`: standardized command to run the cleanup script.
