#!/usr/bin/env bash
set -euo pipefail

NAME=""
MODE="static"
IDEA=""
WORKDIR="${PWD}"
SKIP_DEPLOY="false"

usage() {
  echo "Usage: $0 --name <app-name> [--mode static|nextjs] [--idea <text>] [--workdir <path>] [--skip-deploy]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --idea) IDEA="$2"; shift 2 ;;
    --workdir) WORKDIR="$2"; shift 2 ;;
    --skip-deploy) SKIP_DEPLOY="true"; shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if [[ -z "$NAME" ]]; then
  usage
  exit 1
fi

if [[ "$MODE" != "static" && "$MODE" != "nextjs" ]]; then
  echo "--mode must be static or nextjs"
  exit 1
fi

if [[ "$SKIP_DEPLOY" != "true" ]]; then
  if ! command -v vercel >/dev/null 2>&1; then
    echo "Missing Vercel CLI. Install with: npm i -g vercel"
    exit 1
  fi
fi

TARGET_DIR="${WORKDIR%/}/${NAME}"
mkdir -p "$TARGET_DIR"

if [[ "$MODE" == "static" ]]; then
  cat > "${TARGET_DIR}/index.html" <<HTML
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>${NAME}</title>
  <style>
    :root { color-scheme: dark; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      background: radial-gradient(1000px 500px at 80% -10%, #3b82f6 0%, transparent 60%), #0b1020;
      color: #e8ecff;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
    }
    .card {
      width: min(900px, 100%);
      border: 1px solid #28345f;
      background: rgba(18, 26, 51, 0.85);
      border-radius: 18px;
      padding: 32px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.35);
    }
    h1 { margin: 0 0 8px; font-size: clamp(1.8rem, 4vw, 3rem); }
    p { margin: 0; color: #b8c2f0; line-height: 1.6; }
    .btn {
      display: inline-block;
      margin-top: 20px;
      background: #4f7cff;
      color: white;
      text-decoration: none;
      border-radius: 12px;
      padding: 10px 14px;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <main class="card">
    <h1>${NAME}</h1>
    <p>${IDEA:-A polished website scaffold deployed with Vercel.}</p>
    <a class="btn" href="#">Get Started</a>
  </main>
</body>
</html>
HTML
elif [[ "$MODE" == "nextjs" ]]; then
  if [[ -n "$(ls -A "$TARGET_DIR" 2>/dev/null)" ]]; then
    echo "Target directory is not empty: $TARGET_DIR"
    echo "Use a fresh --name or clean the directory first."
    exit 1
  fi
  npx create-next-app@latest "$TARGET_DIR" --ts --tailwind --eslint --app --use-npm --yes
fi

cd "$TARGET_DIR"

if [[ "$SKIP_DEPLOY" == "true" ]]; then
  echo "🧪 Scaffold complete (deploy skipped)"
  echo "📁 Folder: $TARGET_DIR"
  exit 0
fi

DEPLOY_URL="$(vercel deploy --prod --yes)"

echo "✅ Deployed: $DEPLOY_URL"
echo "📁 Folder: $TARGET_DIR"
