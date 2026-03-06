---
name: onedrive-integration
description: Copy large/long files to OneDrive for sharing when the user is on Telegram or WhatsApp and wants to view a full document or long file. Use to place files into OneDrive under an OpenClaw folder and provide the new filename/location.
---

# onedrive-integration

## Goal

When the user needs a *full* document / long file in Telegram/WhatsApp (where pasting is awkward), copy the file(s) into OneDrive so the user can open/share from there.

## Prerequisites

```bash
command -v python3
python3 --version
```

## Configuration (portable)

Machine-specific config lives alongside the skill:

- Example (do not edit): `~/.openclaw/skills/onedrive-integration/config.env.example`
- Real (machine-specific): `~/.openclaw/skills/onedrive-integration/config.env`

Keys:

- `ONEDRIVE_ROOT` (required) — e.g. `/mnt/c/Users/<windows_user>/OneDrive`
- `ONEDRIVE_SUBDIR` (optional) — default `openclaw`

If config is missing/unset, do **not** guess—ask Boss to confirm the correct OneDrive folder, then write `config.env`.

## Initialization / installation / onboarding

### Preferred (chat-first)

Because the primary interface is chat (Telegram), the preferred onboarding flow is:

1. Ask Boss to confirm the correct OneDrive root folder.
2. Write the real config file: `config.env`.
3. Run a smoke test by copying a small temp file.

### Optional (terminal)

If you are running in a real terminal, you can use the interactive onboarding script:

```bash
~/.openclaw/skills/onedrive-integration/scripts/onboard.sh
```

## How it works

Copy requested file(s) into:

- `${ONEDRIVE_ROOT}/${ONEDRIVE_SUBDIR}/` (defaults to `openclaw/`)

During copy, rename files to include their source path to avoid collisions.

### Rename rules

- Convert absolute path into a safe filename:
  - strip leading `/`
  - replace path separators (`/` and `\\`) with `-`
  - lowercase
  - replace any non `[a-z0-9._-]` with `-`
  - collapse multiple `-`

Examples:
- `/home/miles/folder1/file1.md` → `wsl-home-miles-folder1-file1.md`
- `/mnt/c/Users/<user>/folder1/file1.md` → `c-users-<user>-folder1-file1.md`

### Implementation

Canonical executable lives inside the skill folder:

- `~/.openclaw/skills/onedrive-integration/scripts/copy_to_onedrive.py`

Run:

```bash
~/.openclaw/skills/onedrive-integration/scripts/copy_to_onedrive.py <paths...>
```

(Reads `config.env` automatically.)

Optional overrides:

- `.../copy_to_onedrive.py --onedrive-root "..." --subdir "..." <paths...>`
- `.../copy_to_onedrive.py --config /path/to/config.env <paths...>`

The script:

- creates `${ONEDRIVE_ROOT}/${ONEDRIVE_SUBDIR}/` if missing
- copies files (preserve timestamps)
- prints the destination paths (no secrets)

## Notes

- If the request is a *browser-only* document (no local file), download it to a temp path first, then copy.
- If `ONEDRIVE_ROOT` is unset, do **not** guess—ask for confirmation.

## Executables / bin placement

- Keep the canonical script inside the skill folder.
- Optional: symlink into a common PATH dir (only if you want a short command):

```bash
mkdir -p ~/.local/bin
ln -sf ~/.openclaw/skills/onedrive-integration/scripts/copy_to_onedrive.py ~/.local/bin/copy-to-onedrive
```
