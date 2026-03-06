#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/YutaiGu/skill-briefing.git}"
INSTALL_DIR="${INSTALL_DIR:-$PWD/skill-briefing}"
BIN_DIR="${BIN_DIR:-/usr/local/bin}"
VENV_DIR="$INSTALL_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"
LAUNCHER_PATH=""

log() {
  printf "[briefing-install] %s\n" "$1"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1
}

ffmpeg_already_installed() {
  require_cmd ffmpeg
}

install_deps_linux() {
  local ffmpeg_needed=1
  if ffmpeg_already_installed; then
    ffmpeg_needed=0
    log "Detected existing ffmpeg, skip ffmpeg package install"
  fi

  if require_cmd apt-get; then
    sudo apt-get update
    if [ "$ffmpeg_needed" -eq 1 ]; then
      sudo apt-get install -y git curl python3.12 python3.12-venv ffmpeg
    else
      sudo apt-get install -y git curl python3.12 python3.12-venv
    fi
    if ! require_cmd "$PYTHON_BIN"; then
      echo "python3.12 not found after install. Please install Python 3.12 manually."
      exit 1
    fi
    return
  fi

  if require_cmd dnf; then
    if [ "$ffmpeg_needed" -eq 1 ]; then
      sudo dnf install -y git curl python3.12 ffmpeg
    else
      sudo dnf install -y git curl python3.12
    fi
    if ! require_cmd "$PYTHON_BIN"; then
      echo "python3.12 not found after install. Please install Python 3.12 manually."
      exit 1
    fi
    return
  fi

  if require_cmd yum; then
    if [ "$ffmpeg_needed" -eq 1 ]; then
      sudo yum install -y git curl python3.12 ffmpeg
    else
      sudo yum install -y git curl python3.12
    fi
    if ! require_cmd "$PYTHON_BIN"; then
      echo "python3.12 not found after install. Please install Python 3.12 manually."
      exit 1
    fi
    return
  fi

  echo "Unsupported Linux package manager. Install manually: git curl python3.12 python3.12-venv ffmpeg"
  exit 1
}

install_deps_macos() {
  if ! require_cmd brew; then
    echo "Homebrew is required on macOS. Install from https://brew.sh first."
    exit 1
  fi

  brew update
  if ffmpeg_already_installed; then
    log "Detected existing ffmpeg, skip ffmpeg package install"
    brew install git python@3.12
  else
    brew install git python@3.12 ffmpeg
  fi

  local brew_py
  brew_py="$(brew --prefix python@3.12)/bin/python3.12"
  if [ -x "$brew_py" ]; then
    PYTHON_BIN="$brew_py"
  fi
}

install_deps() {
  os="$(uname -s)"
  case "$os" in
    Linux*) install_deps_linux ;;
    Darwin*) install_deps_macos ;;
    *)
      echo "Unsupported OS: $os"
      exit 1
      ;;
  esac
}

sync_repo() {
  mkdir -p "$(dirname "$INSTALL_DIR")"
  if [ -d "$INSTALL_DIR/.git" ]; then
    log "Updating existing repo in $INSTALL_DIR"
    git -C "$INSTALL_DIR" pull
  else
    if [ -e "$INSTALL_DIR" ] && [ -n "$(ls -A "$INSTALL_DIR" 2>/dev/null || true)" ]; then
      echo "INSTALL_DIR exists and is not a git repo: $INSTALL_DIR"
      echo "Use an empty directory or pass INSTALL_DIR=/path/to/dir"
      exit 1
    fi
    log "Cloning repo to $INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR"
  fi
}

setup_python_env() {
  log "Creating virtual environment"
  "$PYTHON_BIN" -m venv "$VENV_DIR"

  log "Installing Python dependencies"
  "$VENV_DIR/bin/pip" install -U pip setuptools wheel
  "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
}

install_launcher() {
  local target_dir="$BIN_DIR"
  local target_path="$target_dir/briefing"
  local tmpfile

  tmpfile="$(mktemp)"
  cat > "$tmpfile" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/main.py" "\$@"
EOF
  chmod +x "$tmpfile"

  if [ -d "$target_dir" ] && [ -w "$target_dir" ]; then
    mv "$tmpfile" "$target_path"
    LAUNCHER_PATH="$target_path"
    return
  fi

  if require_cmd sudo; then
    sudo mkdir -p "$target_dir"
    sudo install -m 0755 "$tmpfile" "$target_path"
    rm -f "$tmpfile"
    LAUNCHER_PATH="$target_path"
    return
  fi

  rm -f "$tmpfile"
  target_dir="$HOME/.local/bin"
  target_path="$target_dir/briefing"
  mkdir -p "$target_dir"
  cat > "$target_path" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/main.py" "\$@"
EOF
  chmod +x "$target_path"
  LAUNCHER_PATH="$target_path"
}

ensure_path() {
  local launcher_dir
  launcher_dir="$(dirname "$LAUNCHER_PATH")"
  export PATH="$launcher_dir:$PATH"

  local line="export PATH=\"$launcher_dir:\$PATH\""
  local profiles=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile")

  for profile in "${profiles[@]}"; do
    if [ ! -f "$profile" ]; then
      continue
    fi
    if grep -Fq "$line" "$profile"; then
      return
    fi
  done

  local target="$HOME/.profile"
  if [ -n "${SHELL:-}" ] && [[ "$SHELL" == *"zsh"* ]]; then
    target="$HOME/.zshrc"
  elif [ -n "${SHELL:-}" ] && [[ "$SHELL" == *"bash"* ]]; then
    target="$HOME/.bashrc"
  fi

  touch "$target"
  printf "\n%s\n" "$line" >> "$target"
  log "Added PATH entry to $target"
}

verify_install() {
  "$VENV_DIR/bin/python" -c "import sys; sys.path.insert(0, '$INSTALL_DIR'); import main" >/dev/null
  if [ ! -x "$LAUNCHER_PATH" ]; then
    echo "Launcher was not created: $LAUNCHER_PATH"
    exit 1
  fi
}

print_done() {
  log "Installed successfully."
  echo
  echo "Launcher: $LAUNCHER_PATH"
  echo "Run: briefing"
}

main() {
  install_deps
  sync_repo
  setup_python_env
  install_launcher
  ensure_path
  verify_install
  print_done
}

main "$@"
