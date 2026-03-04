# Backup Inclusion/Exclusion Rules

To keep the Phylactery (soul backup) efficient and secure, the following rules apply:

## Included (The Essence)
- `MEMORY.md`: Long-term memory and distilled wisdom.
- `memory/*.md`: Daily logs and conversation context.
- `SOUL.md`: Personality, rules, and core identity.
- `USER.md`: Information about the human partner.
- `*.md`: Documentation and custom instructions in the workspace root.
- `skills/`: Installed skills and custom logic.

## Excluded (The Noise)
- `node_modules/`: Massive dependency folders (can be re-installed).
- `.git/`: Version history (redundant for a soul state backup).
- `temp/` & `tmp/`: Temporary files.
- `*.zip`, `*.skill`, `*.tar.gz`: Previous backup files or packages.
- `.env`: (Security) While identity is backed up, local environment secrets should be handled with care.
