#!/bin/bash
# SECURITY MANIFEST:
#   Environment variables accessed: NONE (except those used by clawhub CLI)
#   External endpoints called: ClawHub registry API (publish)
#   Local files read: skill directory, config files
#   Local files written: none
#
# Republish curated-search after remediation
# Run this after rate limit resets (wait ~1-2 hours)

cd /home/q/.openclaw/workspace/skills/curated-search

# Ensure version is 1.0.4 (increment from 1.0.3)
# Update package.json and CHANGELOG.md first if needed

clawhub publish . \
  --slug curated-search \
  --name "Curated Search" \
  --version 1.0.4 \
  --changelog "Security: removed unused search-api.js server component and related references. Cleaned .clawhubignore to exclude all internal audit files." \
  --no-input
