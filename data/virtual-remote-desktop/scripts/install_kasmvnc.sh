#!/usr/bin/env bash
set -euo pipefail

need_bin() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "[ERR] missing command: $1" >&2
    exit 1
  }
}

need_bin python3
need_bin wget
need_bin sudo

if command -v vncserver >/dev/null 2>&1 && vncserver -help 2>&1 | grep -qi kasmvnc; then
  echo "[OK] KasmVNC already installed"
  exit 0
fi

CODENAME="$(lsb_release -cs 2>/dev/null || echo noble)"
ARCH_RAW="$(uname -m)"
case "${ARCH_RAW}" in
  x86_64|amd64) ARCH=amd64 ;;
  aarch64|arm64) ARCH=arm64 ;;
  *) echo "[ERR] unsupported arch: ${ARCH_RAW}" >&2; exit 1 ;;
esac

ASSET_URL="$(python3 - <<PY
import requests,sys
codename='${CODENAME}'
arch='${ARCH}'
release=requests.get('https://api.github.com/repos/kasmtech/KasmVNC/releases/latest',timeout=20).json()
assets=release.get('assets',[])
preferred=[f'kasmvncserver_{codename}_', 'kasmvncserver_noble_', 'kasmvncserver_jammy_', 'kasmvncserver_focal_', 'kasmvncserver_bookworm_']
for prefix in preferred:
    for a in assets:
        n=a.get('name','')
        if n.startswith(prefix) and n.endswith(f'_{arch}.deb'):
            print(a['browser_download_url'])
            sys.exit(0)
print('')
PY
)"

if [[ -z "${ASSET_URL}" ]]; then
  echo "[ERR] could not resolve KasmVNC package for codename=${CODENAME}, arch=${ARCH}" >&2
  exit 1
fi

TMP_DEB="/tmp/$(basename "${ASSET_URL}")"
echo "[INFO] downloading ${ASSET_URL}"
wget -qO "${TMP_DEB}" "${ASSET_URL}"

echo "[INFO] installing ${TMP_DEB}"
sudo apt-get update -qq
# core runtime deps for AI action scripts + lightweight desktop
sudo apt-get install -y "${TMP_DEB}" fluxbox xdotool scrot xauth

if ! id -nG "$USER" | tr ' ' '\n' | grep -qx 'ssl-cert'; then
  echo "[INFO] adding ${USER} to ssl-cert group"
  sudo usermod -a -G ssl-cert "$USER"
fi

echo "[OK] KasmVNC installed"
echo "[NOTE] if current shell still lacks ssl-cert group, scripts will use 'sg ssl-cert -c ...' automatically"
