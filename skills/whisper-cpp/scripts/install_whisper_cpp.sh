#!/usr/bin/env bash
set -euo pipefail

# Builds whisper.cpp and installs whisper-cli into ~/.local/bin,
# and installs the required shared libraries into ~/.local/lib.

PREFIX="$HOME/.local/share/whisper.cpp"
REPO="$PREFIX/repo"
BUILD="$REPO/build"

mkdir -p "$PREFIX" "$HOME/.local/bin" "$HOME/.local/lib"

if [ ! -d "$REPO/.git" ]; then
  git clone https://github.com/ggerganov/whisper.cpp "$REPO"
else
  git -C "$REPO" pull --ff-only
fi

cmake -S "$REPO" -B "$BUILD" -DCMAKE_BUILD_TYPE=Release
cmake --build "$BUILD" -j"$(nproc)"

# install whisper-cli
if [ -x "$BUILD/bin/whisper-cli" ]; then
  install -m 755 "$BUILD/bin/whisper-cli" "$HOME/.local/bin/whisper-cli"
elif [ -x "$BUILD/whisper-cli" ]; then
  install -m 755 "$BUILD/whisper-cli" "$HOME/.local/bin/whisper-cli"
else
  echo "Could not find whisper-cli under: $BUILD" >&2
  exit 1
fi

# install shared libs so whisper-cli keeps working after you delete the build dir/repo
find "$BUILD" -maxdepth 4 -type f \( -name 'libwhisper.so*' -o -name 'libggml*.so*' \) \
  -exec install -m 755 -t "$HOME/.local/lib" {} +

cd "$HOME/.local/lib"
# create symlinks expected by the loader (best-effort)
ls -1 libwhisper.so.1.* >/dev/null 2>&1 && [ -e libwhisper.so.1 ] || ln -sf "$(ls -1 libwhisper.so.1.* | head -n1)" libwhisper.so.1
ls -1 libggml.so.0.* >/dev/null 2>&1 && [ -e libggml.so.0 ] || ln -sf "$(ls -1 libggml.so.0.* | head -n1)" libggml.so.0
ls -1 libggml-base.so.0.* >/dev/null 2>&1 && [ -e libggml-base.so.0 ] || ln -sf "$(ls -1 libggml-base.so.0.* | head -n1)" libggml-base.so.0
ls -1 libggml-cpu.so.0.* >/dev/null 2>&1 && [ -e libggml-cpu.so.0 ] || ln -sf "$(ls -1 libggml-cpu.so.0.* | head -n1)" libggml-cpu.so.0

LD_LIBRARY_PATH="$HOME/.local/lib" "$HOME/.local/bin/whisper-cli" -h >/dev/null

echo "[OK] whisper-cli installed to ~/.local/bin and libs installed to ~/.local/lib"
