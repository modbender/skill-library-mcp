#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${1:-$(pwd)}"
cd "$APP_ROOT"

echo "[doctor] app root: $APP_ROOT"

ok(){ echo "[ok] $*"; }
warn(){ echo "[warn] $*"; }
miss(){ echo "[missing] $*"; }

if [ -f package.json ]; then
  ok "package.json found"
else
  miss "package.json not found"
  exit 2
fi

if node -e "const p=require('./package.json'); process.exit((p.dependencies&&p.dependencies['react-native-update'])||(p.devDependencies&&p.devDependencies['react-native-update'])?0:1)"; then
  ok "react-native-update dependency present"
else
  miss "react-native-update dependency missing"
fi

if [ -f update.json ]; then
  ok "update.json found"
  if node -e "const u=require('./update.json'); const good=(u.ios&&u.ios.appKey)||(u.android&&u.android.appKey); process.exit(good?0:1)"; then
    ok "update.json includes platform appKey"
  else
    warn "update.json exists but appKey looks incomplete"
  fi
else
  miss "update.json missing (run pushy createApp/selectApp)"
fi

if [ -d ios ]; then
  if [ -f ios/Podfile ]; then
    ok "ios/Podfile found"
  else
    warn "ios exists but Podfile missing"
  fi
fi

if [ -d android ]; then
  ok "android project found"
fi

if grep -R --line-number --include='package.json' 'expo-updates' . >/dev/null 2>&1; then
  warn "expo-updates detected; may conflict depending on integration mode"
fi

echo "[doctor] done"
