#!/usr/bin/env bash
set -euo pipefail

# Install a Chromium/Chrome extension via direct CRX download (no Web Store UI).
# Default target extension: DataHive.
#
# Usage:
#   BROWSER=chrome|chromium ./install_extension_crx.sh [extension-id]
#
# Env:
#   BROWSER=chrome|chromium (default: chrome)
#   PROD_VERSION=<browser version used for CRX update URL>
#   WORK_DIR=/tmp/datahive-crx

EXT_ID="${1:-bonfdkhbkkdoipfojcnimjagphdnfedb}"
BROWSER="${BROWSER:-chrome}"
PROD_VERSION="${PROD_VERSION:-145.0.7632.109}"
WORK_DIR="${WORK_DIR:-/tmp/datahive-crx}"
CRX_PATH="$WORK_DIR/${EXT_ID}.crx"
ZIP_PATH="$WORK_DIR/${EXT_ID}.zip"
UNPACK_DIR="$WORK_DIR/${EXT_ID}-unpacked"

# System-wide external extension location differs by browser packaging.
case "$BROWSER" in
  chrome)
    EXT_BASE_DIR="/opt/google/chrome/extensions"
    ;;
  chromium)
    # Snap Chromium reads from this path in this environment.
    EXT_BASE_DIR="/var/snap/chromium/current/chromium-browser/Extensions"
    ;;
  *)
    echo "ERROR: unsupported BROWSER='$BROWSER' (use chrome|chromium)" >&2
    exit 2
    ;;
esac

EXTERNAL_JSON_PATH="$EXT_BASE_DIR/${EXT_ID}.json"
EXTERNAL_CRX_PATH="$EXT_BASE_DIR/${EXT_ID}.crx"

mkdir -p "$WORK_DIR"

CRX_URL="https://clients2.google.com/service/update2/crx?response=redirect&prodversion=${PROD_VERSION}&acceptformat=crx2,crx3&x=id%3D${EXT_ID}%26uc"

echo "[1/6] Downloading CRX for extension: $EXT_ID"
curl -fL "$CRX_URL" -o "$CRX_PATH"

if [[ ! -s "$CRX_PATH" ]]; then
  echo "ERROR: CRX download failed or returned empty file." >&2
  exit 1
fi

echo "[2/6] Decoding CRX container"
python3 - "$CRX_PATH" "$ZIP_PATH" <<'PY'
import pathlib, struct, sys
crx_path = pathlib.Path(sys.argv[1])
zip_path = pathlib.Path(sys.argv[2])
data = crx_path.read_bytes()
if data[:4] != b"Cr24":
    raise SystemExit("Not a CRX file")
ver = struct.unpack("<I", data[4:8])[0]
if ver == 2:
    pub_len, sig_len = struct.unpack("<II", data[8:16])
    off = 16 + pub_len + sig_len
elif ver == 3:
    header_len = struct.unpack("<I", data[8:12])[0]
    off = 12 + header_len
else:
    raise SystemExit(f"Unsupported CRX version: {ver}")
zip_path.write_bytes(data[off:])
print(f"CRX_VERSION={ver}")
PY

echo "[3/6] Unpacking extension files"
rm -rf "$UNPACK_DIR"
mkdir -p "$UNPACK_DIR"
python3 - "$ZIP_PATH" "$UNPACK_DIR" <<'PY'
import json, pathlib, zipfile, sys
zip_path = pathlib.Path(sys.argv[1])
out_dir = pathlib.Path(sys.argv[2])
with zipfile.ZipFile(zip_path) as z:
    z.extractall(out_dir)
manifest = json.loads((out_dir / "manifest.json").read_text())
print(f"EXT_VERSION={manifest.get('version','unknown')}")
print(f"UNPACK_DIR={out_dir}")
PY

echo "[4/6] Installing external extension files ($BROWSER)"
sudo mkdir -p "$EXT_BASE_DIR"
sudo cp "$CRX_PATH" "$EXTERNAL_CRX_PATH"

EXT_VERSION="$(python3 - <<PY
import json
from pathlib import Path
m = json.loads(Path('$UNPACK_DIR/manifest.json').read_text())
print(m.get('version','0.0.0'))
PY
)"

printf '{"external_crx":"%s","external_version":"%s"}\n' "$EXTERNAL_CRX_PATH" "$EXT_VERSION" | sudo tee "$EXTERNAL_JSON_PATH" >/dev/null

echo "[5/6] Verifying installed files"
test -s "$CRX_PATH"
test -f "$UNPACK_DIR/manifest.json"
sudo test -s "$EXTERNAL_CRX_PATH"
sudo test -s "$EXTERNAL_JSON_PATH"

echo "[6/6] Done"
echo "BROWSER=$BROWSER"
echo "EXT_ID=$EXT_ID"
echo "EXT_VERSION=$EXT_VERSION"
echo "CRX_PATH=$CRX_PATH"
echo "UNPACK_DIR=$UNPACK_DIR"
echo "EXTERNAL_CRX_PATH=$EXTERNAL_CRX_PATH"
echo "EXTERNAL_JSON_PATH=$EXTERNAL_JSON_PATH"
