#!/usr/bin/env bash
# install.sh — Set up Task-Specialist skill
# Creates SQLite database and optional PATH symlinks.
# No eval(), no external APIs, no crypto.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB="${TASK_DB:-$SCRIPT_DIR/tasks.db}"
BIN_DIR="${HOME}/.local/bin"

ok()  { printf '\033[1;32m✓\033[0m %s\n' "$1"; }
die() { printf '\033[1;31mError:\033[0m %s\n' "$1" >&2; exit 1; }
info(){ printf '\033[1;34mℹ\033[0m %s\n' "$1"; }

CREATE_SYMLINKS=false
if [ "${1:-}" = "--symlink" ]; then
  CREATE_SYMLINKS=true
fi

# ── 1. Check sqlite3 ────────────────────────────────────────────────────────

if ! command -v sqlite3 &>/dev/null; then
  die "sqlite3 is required but not found. Install it:
    Debian/Ubuntu: sudo apt install sqlite3
    Arch:          sudo pacman -S sqlite
    macOS:         brew install sqlite"
fi

ok "sqlite3 found: $(sqlite3 --version | head -1)"

# ── 2. Create database with schema ──────────────────────────────────────────

if [ -f "$DB" ]; then
  info "Database already exists at $DB — skipping creation."
else
  sqlite3 "$DB" <<'SQL'
CREATE TABLE IF NOT EXISTS tasks (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  request_text TEXT    NOT NULL,
  project      TEXT,
  status       TEXT    NOT NULL DEFAULT 'pending'
                       CHECK(status IN ('pending','in_progress','blocked','done')),
  priority     INTEGER NOT NULL DEFAULT 5
                       CHECK(priority BETWEEN 1 AND 10),
  parent_id    INTEGER REFERENCES tasks(id),
  created_at   TEXT    NOT NULL,
  started_at   TEXT,
  completed_at TEXT,
  last_updated TEXT    NOT NULL,
  notes        TEXT
);

CREATE TABLE IF NOT EXISTS dependencies (
  task_id           INTEGER NOT NULL REFERENCES tasks(id),
  depends_on_task_id INTEGER NOT NULL REFERENCES tasks(id),
  PRIMARY KEY (task_id, depends_on_task_id),
  CHECK(task_id != depends_on_task_id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_id);
CREATE INDEX IF NOT EXISTS idx_deps_task    ON dependencies(task_id);
CREATE INDEX IF NOT EXISTS idx_deps_dep     ON dependencies(depends_on_task_id);
SQL

  ok "Database created at $DB"
fi

# ── 3. Make scripts executable ───────────────────────────────────────────────

chmod +x "$SCRIPT_DIR/scripts/task.sh"
chmod +x "$SCRIPT_DIR/scripts/task-heartbeat.sh"
ok "Scripts marked executable"

# ── 4. Symlink to ~/.local/bin (optional) ────────────────────────────────────

if [ "$CREATE_SYMLINKS" = true ]; then
  mkdir -p "$BIN_DIR"
  ln -sf "$SCRIPT_DIR/scripts/task.sh" "$BIN_DIR/task"
  ln -sf "$SCRIPT_DIR/scripts/task-heartbeat.sh" "$BIN_DIR/task-heartbeat"
  ok "Symlinks created in $BIN_DIR"

  # Check if ~/.local/bin is in PATH
  if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    info "Add $BIN_DIR to your PATH if not already present:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
  fi
else
  info "Skipped symlinking to $BIN_DIR (run 'bash install.sh --symlink' to create them automatically)."
  info "You can use the commands directly:"
  echo "  $SCRIPT_DIR/scripts/task.sh"
  echo "  $SCRIPT_DIR/scripts/task-heartbeat.sh"
fi

# ── Done ─────────────────────────────────────────────────────────────────────

echo ""
ok "Task-Specialist installed successfully!"
echo ""
echo "Quick start:"
if [ "$CREATE_SYMLINKS" = true ]; then
  echo "  task create \"My first task\" --priority=8"
  echo "  task list"
  echo "  task start 1"
  echo "  task-heartbeat 1"
else
  echo "  $SCRIPT_DIR/scripts/task.sh create \"My first task\" --priority=8"
  echo "  $SCRIPT_DIR/scripts/task.sh list"
  echo "  $SCRIPT_DIR/scripts/task.sh start 1"
fi
