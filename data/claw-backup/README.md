# ClawBackup
Version: 1.0.15

Backs up your OpenClaw customizations (memory, config, skills, workspace) to an `rclone` destination on a schedule (Google Drive by default). Works on macOS, Linux, and Windows (via Git Bash or WSL).

GitHub repository: https://github.com/vidarbrekke/ClawBackup

## What gets backed up

- **Clawd memory** — your project memory folder
- **OpenClaw config** — `openclaw.json`, skills, modules, workspace, cron jobs
- **Clawd scripts** — backup script, LaunchAgent plist (macOS)
- **CursorApps/clawd** — includes active skills and related files (excluding `node_modules`)

## Prerequisites

- **Node.js** — [Download](https://nodejs.org/) (for running setup)
- **rclone** — [Download](https://rclone.org/install/) and configured for Google Drive (**only required in `rclone` upload mode**)
- **Bash** — included on macOS/Linux; use Git Bash on Windows. **If you use WSL**, run setup inside your WSL terminal (e.g. `node setup.js` from WSL), not from Windows PowerShell, so paths are generated for Linux.

## Install (recommended)

### Safer path (recommended)

Review the repository code before running setup:

```bash
git clone https://github.com/vidarbrekke/ClawBackup.git
cd ClawBackup
# optional: checkout a tag or pinned commit before running
node setup.js
```

### Quick path (advanced users)

This downloads and executes setup immediately. Use only if you trust the source:

```bash
curl -fsSL https://raw.githubusercontent.com/vidarbrekke/ClawBackup/main/setup.js | node
```

## Run setup

1. Run the setup (using Option A or B above).
2. Answer the prompts. Press Enter to accept the default in brackets. All paths use your system’s home directory and what you type — nothing is hardcoded to a specific username.
3. The setup writes a customized `backup_enhanced.sh` into your project’s `scripts/` folder (paths are resolved to absolute so cron/launchd work from any working directory).
4. Choose upload mode:
   - `rclone` (default): upload archives to your remote destination.
   - `local-only`: keep backups locally, skip cloud transfer.
5. If you chose `launchd` (macOS) or `cron` (Linux), follow the printed commands to enable scheduled backups. Setup now prompts for schedule hour/minute.

To regenerate the backup script and plist with default paths only (no prompts), run `node setup.js --defaults`.

## Before first backup

1. **Configure rclone for Google Drive:**
   ```bash
   rclone config
   ```
   Create a remote (e.g. `googleDrive`) and complete the OAuth flow.

2. **Test a backup:**
   ```bash
   ~/clawd/scripts/backup_enhanced.sh
   ```
   (Use the path the setup printed for your system.)

## Security notes (important)

- Backups can contain sensitive data from `~/.openclaw`, project config, memory, and skills.
- Setup and scheduling modify your local environment (LaunchAgent/cron/Task Scheduler) and create recurring jobs.
- In `rclone` mode, cloud credentials are provided by your existing `rclone config`; no new env vars are required by this repo.
- Prefer encrypted storage:
  - use an encrypted destination (e.g. `rclone crypt`), or
  - encrypt archives locally before offsite storage (e.g. age/gpg workflow).
- Each backup now writes a checksum file (`.sha256`) next to the archive for integrity verification.

## Disable / uninstall scheduler

- **macOS:** `launchctl unload ~/Library/LaunchAgents/com.openclaw.backup.plist`
- **Linux:** remove the backup line from `crontab -e`
- **Windows:** remove/disable the Task Scheduler task you created

## Restore notes (skills and user data)

Each archive includes a `RESTORE_NOTES.txt` file with the exact restore targets
based on your configured paths. In general:

- `openclaw_config/skills` → `~/.openclaw/skills`
- `cursorapps_clawd/skills` → `~/Dev/CursorApps/clawd/skills` (or your chosen path)
- `openclaw_config/*` → `~/.openclaw/`
- `clawd_scripts/*` → `~/clawd/scripts/`
- `root_md_files/*` → project root

## Schedule (optional)

- **macOS:** The setup generates a LaunchAgent plist. Install with the printed commands (copy to `~/Library/LaunchAgents/` and `launchctl load` — no sudo for the agent). Or run the universal installer: `./install-launchagent.sh` (it searches common locations; if your project is elsewhere, pass the plist path: `./install-launchagent.sh /path/to/com.openclaw.backup.plist`). If you had an old system-wide daemon, the installer may ask for your password once to remove it. Backup runs at the hour/minute configured during setup.
- **Linux:** Add the printed cron line to `crontab -e`.
- **Windows:** Use Task Scheduler to run the backup script daily via Git Bash or WSL.

## Troubleshooting

- **Backup fails or rclone “remote not found”:** Run `rclone config` and ensure the remote name matches what you entered at setup (e.g. `googleDrive`). On macOS, use the LaunchAgent (not LaunchDaemon) so the job runs as your user and sees `~/.config/rclone`.
- **Paths wrong after moving home/project:** Run `node setup.js` again with the new paths, then reinstall the scheduler (e.g. `./install-launchagent.sh` on macOS).
- **Check logs:** Local backup log: `$LOCAL_BACKUP_DIR/backup.log`; launchd stdout/stderr: `$LOCAL_BACKUP_DIR/launchd.log` and `launchd.err` (paths from your setup).

## Roadmap

### Now

- Add workspace include modes (`full|minimal|off`) so users can tune backup size and sensitivity for `~/.openclaw/workspace*`.

### Next

- Add optional remote verification mode (presence/size/checksum validation after upload).
- Add stricter remote retention safety checks (safe destination prefix by default, explicit override when needed).
- Enrich `manifest.json` with ClawBackup git commit hash and top-level staged sections.
- Add launchd polish options (`RunAtLoad`, `WorkingDirectory`) while keeping current defaults stable.
- Add destination examples/presets in setup/docs for common `rclone` remotes (Dropbox, OneDrive, Box, S3).

### Later

- Add a `restore.sh` helper (dry-run by default) to make restores safer and easier.
- Introduce a storage-provider abstraction (keep `rclone` as default, allow provider-skill adapters later).

## Test suite

Critical behavior tests are included for setup/runtime generation logic.

Run:

```bash
node --test tests/*.test.js
```

## For maintainers / AI-assisted edits

To reduce oversights when editing this repo (e.g. destructive ops, path edge cases), this repo includes a Cursor rule: [.cursor/rules/safety-destructive-ops.mdc](.cursor/rules/safety-destructive-ops.mdc). You can copy that file into your OpenClaw or clawd project’s `.cursor/rules/` so the same checks apply there.

## Versioning (auto-updated on commit)

This repo includes a `VERSION` file and an update script. To auto-update the
version on every commit, enable the local git hook:

```bash
git config core.hooksPath .githooks
```

This runs `scripts/update-version.sh --next` before each commit and updates
`VERSION`, `README.md`, and `SKILL.md`.

## License

MIT
