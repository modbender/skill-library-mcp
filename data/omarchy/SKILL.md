---
name: omarchy
description: "Omarchy operating guardrails for day-to-day system work: assume the host is Omarchy by default, choose Omarchy-native workflows first, map user intent to the correct omarchy-* wrapper/script family, and avoid generic Linux commands that conflict with Omarchy behavior. Use whenever handling local system tasks on this host unless the user explicitly says it is not Omarchy; prioritize safe Omarchy commands, prevent non-Omarchy shortcuts (e.g., ad-hoc process killing/relaunch patterns), troubleshoot desktop behavior, and validate the right script before execution."
---

# Omarchy Skill

Treat this skill as an Omarchy operating mode, not just a command catalog. When working on an Omarchy system, prefer Omarchy-native wrappers and workflows over generic Linux one-liners that may bypass expected state handling. Use local script docs and names to choose the correct path. Each script has documentation at the top describing its purpose. DO NOT RUN A SCRIPT UNTIL YOU ARE SURE OF ITS PURPOSE.

## Operating rules

1. Start with command name matching and in-file comments under `/home/achals/.local/share/omarchy/bin`.
2. Prefer read-only/status commands first (`*list*`, `*status*`, `*current*`, `*available*`, `*version*`).
3. Ask before broad or high-impact actions (`*install*`, `*remove*`, `*reinstall*`, `*update*`, `*pkg*`, `*setup*`, `*set*`).
4. Avoid bulk discovery execution. Do static inspection first.
5. Never assume `omarchy-*` scripts support standard CLI flags or parameters (including `--help`). Treat each script as custom; inspect its file/header comments first.

## Worked examples (good vs bad)

Use these patterns whenever you operate on Omarchy. The goal is not "run an omarchy command at all costs"; the goal is to avoid bypassing Omarchy’s intended state-management flows.

### 1) Restarting Waybar

User intent: "Waybar is broken, restart it."

- Bad (generic shortcut):
  - `pkill waybar && waybar`
- Good (Omarchy-native):
  - `omarchy-restart-waybar`
- Why: Omarchy wrappers usually handle environment/session assumptions better than raw kill-and-relaunch one-liners.

### 2) Applying config/UI refresh after edits

User intent: "I changed config, apply it."

- Bad:
  - restarting random processes manually until things look fixed
- Good:
  - use targeted refresh script first, e.g. `omarchy-refresh-waybar`, `omarchy-refresh-hyprland`, `omarchy-refresh-config` (pick by component)
- Why: refresh scripts are explicit and reversible; manual shotgun restarts are noisy and risky.

### 3) Package management task

User intent: "Install/remove package X."

- Bad:
  - using raw `pacman`/`yay` first without checking Omarchy wrappers
- Good:
  - inspect and prefer `omarchy-pkg-*` flow (`...-present`, `...-missing`, then `...-install`/`...-remove`)
- Why: wrapper flow keeps behavior consistent with Omarchy expectations.

### 4) Theme change request

User intent: "Switch theme / sync theme to apps."

- Bad:
  - editing dotfiles manually first and restarting random apps
- Good:
  - `omarchy-theme-list` -> `omarchy-theme-set` -> app-specific follow-ups if needed (`omarchy-theme-set-vscode`, `...-browser`, `...-obsidian`)
- Why: Omarchy theme pipeline may include extra integration steps beyond plain config edits.

### 5) Audio/Bluetooth/Wi‑Fi issue

User intent: "Audio/Bluetooth/Wi‑Fi stopped behaving."

- Bad:
  - broad process killing (`killall pipewire`, random daemon restarts)
- Good:
  - use targeted wrapper restarts such as `omarchy-restart-pipewire`, `omarchy-restart-bluetooth`, `omarchy-restart-wifi`
- Why: targeted wrappers reduce collateral damage and match Omarchy’s service model.

### 6) "What command should I run?" discovery flow

User intent: ambiguous request like "fix my display stack".

- Bad:
  - execute many commands to discover options (`for c in omarchy-*; do $c --help; done`)
- Good:
  1. Statically inspect names in `/home/achals/.local/share/omarchy/bin`
  2. Read top-of-file script comments for likely candidates
  3. Start with read-only/status scripts
  4. Propose 1-3 likely commands and ask before high-impact actions
- Why: static inspection is safer, faster, and follows no-bulk-probing policy.

### 7) Update workflow

User intent: "Update system."

- Bad:
  - directly running full update steps without checking availability/state
- Good:
  - check first: `omarchy-update-available` (and related status)
  - then execute appropriate Omarchy update path with confirmation for impactful steps
- Why: staged update flow reduces surprise breakage.

## Decision template (apply every time)

For any Omarchy task, follow this mini-checklist:

1. Identify component (UI, package, theme, network, update, device, etc.)
2. Find matching `omarchy-*` family by name and script header comments
3. Prefer read-only/status command first
4. Use targeted `omarchy-refresh-*`/`omarchy-restart-*` over raw kill/relaunch
5. Ask before high-impact actions (`install/remove/reinstall/update/setup/set`)

## Omarchy command catalog (static, local)

Total commands: **161**

### battery (2)
- `omarchy-battery-monitor`
- `omarchy-battery-remaining`

### branch (1)
- `omarchy-branch-set`

### channel (1)
- `omarchy-channel-set`

### cmd (12)
- `omarchy-cmd-apple-display-brightness`
- `omarchy-cmd-audio-switch`
- `omarchy-cmd-first-run`
- `omarchy-cmd-missing`
- `omarchy-cmd-present`
- `omarchy-cmd-reboot`
- `omarchy-cmd-screenrecord`
- `omarchy-cmd-screensaver`
- `omarchy-cmd-screenshot`
- `omarchy-cmd-share`
- `omarchy-cmd-shutdown`
- `omarchy-cmd-terminal-cwd`

### debug (1)
- `omarchy-debug`

### dev (1)
- `omarchy-dev-add-migration`

### drive (3)
- `omarchy-drive-info`
- `omarchy-drive-select`
- `omarchy-drive-set-password`

### font (3)
- `omarchy-font-current`
- `omarchy-font-list`
- `omarchy-font-set`

### hibernation (3)
- `omarchy-hibernation-available`
- `omarchy-hibernation-remove`
- `omarchy-hibernation-setup`

### hook (1)
- `omarchy-hook`

### hyprland (3)
- `omarchy-hyprland-window-close-all`
- `omarchy-hyprland-window-pop`
- `omarchy-hyprland-workspace-toggle-gaps`

### install (9)
- `omarchy-install-chromium-google-account`
- `omarchy-install-dev-env`
- `omarchy-install-docker-dbs`
- `omarchy-install-dropbox`
- `omarchy-install-steam`
- `omarchy-install-tailscale`
- `omarchy-install-terminal`
- `omarchy-install-vscode`
- `omarchy-install-xbox-controllers`

### launch (14)
- `omarchy-launch-about`
- `omarchy-launch-audio`
- `omarchy-launch-bluetooth`
- `omarchy-launch-browser`
- `omarchy-launch-editor`
- `omarchy-launch-floating-terminal-with-presentation`
- `omarchy-launch-or-focus`
- `omarchy-launch-or-focus-tui`
- `omarchy-launch-or-focus-webapp`
- `omarchy-launch-screensaver`
- `omarchy-launch-tui`
- `omarchy-launch-walker`
- `omarchy-launch-webapp`
- `omarchy-launch-wifi`

### lock (1)
- `omarchy-lock-screen`

### menu (2)
- `omarchy-menu`
- `omarchy-menu-keybindings`

### migrate (1)
- `omarchy-migrate`

### notification (1)
- `omarchy-notification-dismiss`

### pkg (9)
- `omarchy-pkg-add`
- `omarchy-pkg-aur-accessible`
- `omarchy-pkg-aur-add`
- `omarchy-pkg-aur-install`
- `omarchy-pkg-drop`
- `omarchy-pkg-install`
- `omarchy-pkg-missing`
- `omarchy-pkg-present`
- `omarchy-pkg-remove`

### powerprofiles (1)
- `omarchy-powerprofiles-list`

### refresh (14)
- `omarchy-refresh-applications`
- `omarchy-refresh-chromium`
- `omarchy-refresh-config`
- `omarchy-refresh-fastfetch`
- `omarchy-refresh-hypridle`
- `omarchy-refresh-hyprland`
- `omarchy-refresh-hyprlock`
- `omarchy-refresh-hyprsunset`
- `omarchy-refresh-limine`
- `omarchy-refresh-pacman`
- `omarchy-refresh-plymouth`
- `omarchy-refresh-swayosd`
- `omarchy-refresh-walker`
- `omarchy-refresh-waybar`

### reinstall (4)
- `omarchy-reinstall`
- `omarchy-reinstall-configs`
- `omarchy-reinstall-git`
- `omarchy-reinstall-pkgs`

### remove (1)
- `omarchy-remove-dev-env`

### reset (1)
- `omarchy-reset-sudo`

### restart (15)
- `omarchy-restart-app`
- `omarchy-restart-bluetooth`
- `omarchy-restart-btop`
- `omarchy-restart-hyprctl`
- `omarchy-restart-hypridle`
- `omarchy-restart-hyprsunset`
- `omarchy-restart-mako`
- `omarchy-restart-opencode`
- `omarchy-restart-pipewire`
- `omarchy-restart-swayosd`
- `omarchy-restart-terminal`
- `omarchy-restart-walker`
- `omarchy-restart-waybar`
- `omarchy-restart-wifi`
- `omarchy-restart-xcompose`

### setup (3)
- `omarchy-setup-dns`
- `omarchy-setup-fido2`
- `omarchy-setup-fingerprint`

### show (2)
- `omarchy-show-done`
- `omarchy-show-logo`

### snapshot (1)
- `omarchy-snapshot`

### state (1)
- `omarchy-state`

### theme (13)
- `omarchy-theme-bg-install`
- `omarchy-theme-bg-next`
- `omarchy-theme-current`
- `omarchy-theme-install`
- `omarchy-theme-list`
- `omarchy-theme-remove`
- `omarchy-theme-set`
- `omarchy-theme-set-browser`
- `omarchy-theme-set-gnome`
- `omarchy-theme-set-obsidian`
- `omarchy-theme-set-templates`
- `omarchy-theme-set-vscode`
- `omarchy-theme-update`

### toggle (5)
- `omarchy-toggle-idle`
- `omarchy-toggle-nightlight`
- `omarchy-toggle-screensaver`
- `omarchy-toggle-suspend`
- `omarchy-toggle-waybar`

### tui (2)
- `omarchy-tui-install`
- `omarchy-tui-remove`

### tz (1)
- `omarchy-tz-select`

### update (14)
- `omarchy-update`
- `omarchy-update-analyze-logs`
- `omarchy-update-available`
- `omarchy-update-available-reset`
- `omarchy-update-branch`
- `omarchy-update-confirm`
- `omarchy-update-firmware`
- `omarchy-update-git`
- `omarchy-update-keyring`
- `omarchy-update-perform`
- `omarchy-update-restart`
- `omarchy-update-system-pkgs`
- `omarchy-update-time`
- `omarchy-update-without-idle`

### upload (1)
- `omarchy-upload-log`

### version (4)
- `omarchy-version`
- `omarchy-version-branch`
- `omarchy-version-channel`
- `omarchy-version-pkgs`

### voxtype (5)
- `omarchy-voxtype-config`
- `omarchy-voxtype-install`
- `omarchy-voxtype-model`
- `omarchy-voxtype-remove`
- `omarchy-voxtype-status`

### webapp (4)
- `omarchy-webapp-handler-hey`
- `omarchy-webapp-handler-zoom`
- `omarchy-webapp-install`
- `omarchy-webapp-remove`

### windows (1)
- `omarchy-windows-vm`
