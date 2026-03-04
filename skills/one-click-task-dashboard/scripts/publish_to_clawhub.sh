#!/bin/zsh
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="one-click-task-dashboard"
VERSION="1.0.0"
NAME="One-Click Task Dashboard"
PRICE_CNY="100"
ORIGIN_FILE="${SKILL_DIR}/.clawhub/origin.json"
NPX_BIN="$(command -v npx || true)"
if [[ -z "${NPX_BIN}" ]]; then
  for one in \
    "/Users/${USER}/.nvm/versions/node/v24.13.0/bin/npx" \
    "${HOME}/.nvm/versions/node/v24.13.0/bin/npx" \
    "/opt/homebrew/bin/npx" \
    "/usr/local/bin/npx"
  do
    if [[ -x "${one}" ]]; then
      NPX_BIN="${one}"
      break
    fi
  done
fi
if [[ -z "${NPX_BIN}" ]]; then
  echo "npx not found" >&2
  exit 1
fi
export PATH="$(dirname "${NPX_BIN}"):/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"

if [[ -f "${ORIGIN_FILE}" ]] && rg -q "\"slug\"[[:space:]]*:[[:space:]]*\"${SLUG}\"" "${ORIGIN_FILE}"; then
  echo "Skill already published: ${SLUG}"
  exit 0
fi

echo "[1/3] 检查 ClawHub 登录态..."
"${NPX_BIN}" -y clawhub whoami --no-input

echo "[2/3] 发布 Skill..."
"${NPX_BIN}" -y clawhub publish "${SKILL_DIR}" \
  --slug "${SLUG}" \
  --name "${NAME}" \
  --version "${VERSION}" \
  --tags "latest" \
  --no-input

echo "[3/3] 售价设置..."
echo "CLI 当前不支持直接设置价格。请在 ClawHub 创作者后台将 ${SLUG} 价格设为 ¥${PRICE_CNY}。"
echo "建议入口: https://clawhub.ai"
echo "Skill slug: ${SLUG}"
