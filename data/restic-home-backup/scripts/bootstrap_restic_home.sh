#!/usr/bin/env bash
set -euo pipefail

# Safer bootstrap for restic home backup.
# Default mode is PLAN-ONLY (no system changes). Use --apply for changes.
#
# Usage (plan only):
#   bash bootstrap_restic_home.sh --user pi --repo /mnt/backup/restic-home
#
# Apply changes:
#   sudo bash bootstrap_restic_home.sh --user pi --repo /mnt/backup/restic-home --apply
#
# Optional:
#   --password-file /etc/restic-home/password
#   --timezone Europe/Berlin
#   --enable-timers          (off by default)
#   --init-repo              (off by default)
#   --run-initial-backup     (off by default)

USER_NAME=""
REPO=""
PASS_FILE="/etc/restic-home/password"
TIMEZONE="Europe/Berlin"
APPLY="no"
ENABLE_TIMERS="no"
INIT_REPO="no"
RUN_INITIAL_BACKUP="no"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) USER_NAME="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --password-file) PASS_FILE="$2"; shift 2 ;;
    --timezone) TIMEZONE="$2"; shift 2 ;;
    --apply) APPLY="yes"; shift 1 ;;
    --enable-timers) ENABLE_TIMERS="yes"; shift 1 ;;
    --init-repo) INIT_REPO="yes"; shift 1 ;;
    --run-initial-backup) RUN_INITIAL_BACKUP="yes"; shift 1 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$USER_NAME" || -z "$REPO" ]]; then
  echo "Missing required args. Need --user and --repo" >&2
  exit 2
fi

HOME_DIR="/home/${USER_NAME}"
if [[ ! -d "$HOME_DIR" ]]; then
  echo "Home dir not found: $HOME_DIR" >&2
  exit 2
fi

if [[ "$APPLY" != "yes" ]]; then
  cat <<EOF
PLAN ONLY (no changes applied).
Would configure restic backup with:
- user: ${USER_NAME}
- source: ${HOME_DIR}
- repository: ${REPO}
- password file: ${PASS_FILE}
- timezone: ${TIMEZONE}
- enable timers: ${ENABLE_TIMERS}
- init repository: ${INIT_REPO}
- run initial backup: ${RUN_INITIAL_BACKUP}

To apply, rerun with: --apply
EOF
  exit 0
fi

if ! command -v restic >/dev/null 2>&1; then
  echo "restic is not installed. Install first: sudo apt install -y restic" >&2
  exit 2
fi

mkdir -p /etc/restic-home

# Generate random password on first setup (if file missing or empty).
if [[ ! -s "$PASS_FILE" ]]; then
  mkdir -p "$(dirname "$PASS_FILE")"
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -base64 48 > "$PASS_FILE"
  else
    tr -dc 'A-Za-z0-9!@#$%^&*()-_=+[]{}:,.?' </dev/urandom | head -c 64 > "$PASS_FILE"
    echo >> "$PASS_FILE"
  fi
  chmod 600 "$PASS_FILE"
  echo "Generated initial random restic password at: $PASS_FILE"
else
  chmod 600 "$PASS_FILE"
fi

cat >/etc/restic-home/excludes.txt <<'EOF'
**/.cache
**/node_modules
**/.venv
**/.local/share/Trash
EOF

cat >/etc/restic-home.env <<EOF
RESTIC_REPOSITORY=${REPO}
RESTIC_PASSWORD_FILE=${PASS_FILE}
BACKUP_SOURCE=${HOME_DIR}
EXCLUDES_FILE=/etc/restic-home/excludes.txt
EOF
chmod 600 /etc/restic-home.env

cat >/usr/local/bin/restic-home-backup.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
source /etc/restic-home.env
exec /usr/bin/restic backup "$BACKUP_SOURCE" --exclude-file "$EXCLUDES_FILE"
EOF
chmod 755 /usr/local/bin/restic-home-backup.sh

cat >/usr/local/bin/restic-home-prune.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
source /etc/restic-home.env
exec /usr/bin/restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune
EOF
chmod 755 /usr/local/bin/restic-home-prune.sh

cat >/usr/local/bin/restic-home-check.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
source /etc/restic-home.env
exec /usr/bin/restic check
EOF
chmod 755 /usr/local/bin/restic-home-check.sh

cat >/etc/systemd/system/restic-home-backup.service <<'EOF'
[Unit]
Description=Restic backup of home directory
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
EnvironmentFile=/etc/restic-home.env
ExecStart=/usr/local/bin/restic-home-backup.sh
EOF

cat >/etc/systemd/system/restic-home-backup.timer <<EOF
[Unit]
Description=Daily home backup (02:30 ${TIMEZONE})

[Timer]
OnCalendar=*-*-* 02:30:00 ${TIMEZONE}
Persistent=true
AccuracySec=1m
Unit=restic-home-backup.service

[Install]
WantedBy=timers.target
EOF

cat >/etc/systemd/system/restic-home-prune.service <<'EOF'
[Unit]
Description=Restic retention prune

[Service]
Type=oneshot
EnvironmentFile=/etc/restic-home.env
ExecStart=/usr/local/bin/restic-home-prune.sh
EOF

cat >/etc/systemd/system/restic-home-prune.timer <<EOF
[Unit]
Description=Weekly prune (Sunday 03:15 ${TIMEZONE})

[Timer]
OnCalendar=Sun *-*-* 03:15:00 ${TIMEZONE}
Persistent=true
AccuracySec=1m
Unit=restic-home-prune.service

[Install]
WantedBy=timers.target
EOF

cat >/etc/systemd/system/restic-home-check.service <<'EOF'
[Unit]
Description=Restic repository integrity check

[Service]
Type=oneshot
EnvironmentFile=/etc/restic-home.env
ExecStart=/usr/local/bin/restic-home-check.sh
EOF

cat >/etc/systemd/system/restic-home-check.timer <<EOF
[Unit]
Description=Monthly restic integrity check (day 1 at 04:00 ${TIMEZONE})

[Timer]
OnCalendar=*-*-01 04:00:00 ${TIMEZONE}
Persistent=true
AccuracySec=5m
Unit=restic-home-check.service

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload

if [[ "$ENABLE_TIMERS" == "yes" ]]; then
  systemctl enable --now restic-home-backup.timer restic-home-prune.timer restic-home-check.timer
fi

if [[ "$INIT_REPO" == "yes" ]]; then
  source /etc/restic-home.env
  if ! /usr/bin/restic snapshots >/dev/null 2>&1; then
    /usr/bin/restic init
  fi
fi

if [[ "$RUN_INITIAL_BACKUP" == "yes" ]]; then
  systemctl start restic-home-backup.service
fi

echo "Apply complete."
echo "- Config/scripts/units written"
echo "- Timers enabled: ${ENABLE_TIMERS}"
echo "- Repo initialized: ${INIT_REPO}"
echo "- Initial backup run: ${RUN_INITIAL_BACKUP}"
echo "Next validation: source /etc/restic-home.env && restic snapshots"
