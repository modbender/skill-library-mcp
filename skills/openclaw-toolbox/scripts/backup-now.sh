#!/bin/bash

# OpenClaw 立即备份脚本
# 使用方法: ./backup-now.sh ["自定义提交信息"]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 尝试寻找 OpenClaw 根目录 (~/.openclaw)
# 逻辑：从脚本目录向上查找，直到找到 openclaw.json 或 .env 文件
FIND_ROOT="$SCRIPT_DIR"
ROOT_DIR=""
while [ "$FIND_ROOT" != "/" ]; do
  if [ -f "$FIND_ROOT/openclaw.json" ] || [ -f "$FIND_ROOT/.env" ]; then
    ROOT_DIR="$FIND_ROOT"
    break
  fi
  FIND_ROOT="$(dirname "$FIND_ROOT")"
done

# 如果没找到，退回到预设的相对路径
if [ -z "$ROOT_DIR" ]; then
  ROOT_DIR="$(cd "$SCRIPT_DIR/../../../../" && pwd)"
fi

SKILLS_DIR="$ROOT_DIR/workspace/projects/openclaw-skills"

# 加载 .env 环境变量
if [ -f "$ROOT_DIR/.env" ]; then
  # 使用 grep 和 sed 处理 .env 文件，避免直接 source 可能带来的安全风险或语法错误
  export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
fi

BACKUP_TYPE="full"
BACKUP_DIR="$ROOT_DIR"
GIT_REMOTE="origin"

NO_PUSH=0
DRY_RUN=0
PULL_BEFORE=0
COMMIT_MSG=""

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

usage() {
  cat <<'USAGE'
Usage:
  backup-now.sh [message] [options]

Options:
  --full        备份整个 OpenClaw 仓库 (默认)
  --skills      备份 openclaw-skills 仓库
  --pull        备份前先 git pull --rebase（要求工作区干净）
  --no-push     只提交，不推送
  --dry-run     仅显示变更，不提交
  -m, --message 提交信息
  -h, --help    显示帮助

USAGE
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --full)
        BACKUP_TYPE="full"
        BACKUP_DIR="$ROOT_DIR"
        ;;
      --skills)
        BACKUP_TYPE="skills"
        BACKUP_DIR="$SKILLS_DIR"
        ;;
      --pull) PULL_BEFORE=1 ;;
      --no-push) NO_PUSH=1 ;;
      --dry-run) DRY_RUN=1 ;;
      -m|--message)
        shift
        COMMIT_MSG="$1"
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        if [ -z "$COMMIT_MSG" ]; then
          COMMIT_MSG="$1"
        else
          COMMIT_MSG="$COMMIT_MSG $1"
        fi
        ;;
    esac
    shift
  done
}

parse_args "$@"

echo -e "${BLUE}🔄 开始 ${BACKUP_TYPE} 备份...${NC}"

if [ ! -d "$BACKUP_DIR" ]; then
  if [ "$BACKUP_TYPE" == "skills" ] && [ -n "$OPENCLAW_SKILLS_GITHUB_URL" ]; then
    echo -e "${YELLOW}⚠️  Skills 目录不存在，尝试克隆...${NC}"
    mkdir -p "$(dirname "$SKILLS_DIR")"
    git clone "$OPENCLAW_SKILLS_GITHUB_URL" "$SKILLS_DIR"
  else
    echo -e "${RED}✗ 备份目录不存在: $BACKUP_DIR${NC}"
    exit 1
  fi
fi

cd "$BACKUP_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo -e "${RED}✗ 当前目录不是 Git 仓库: $BACKUP_DIR${NC}"
  exit 1
fi

if ! git remote get-url "$GIT_REMOTE" >/dev/null 2>&1; then
  GIT_REMOTE="$(git remote | head -n1)"
fi
if [ -z "$GIT_REMOTE" ]; then
  echo -e "${YELLOW}⚠️  未找到 Git 远端${NC}"
fi

REPO_URL=""
if [ -n "$GIT_REMOTE" ]; then
  REPO_URL="$(git remote get-url "$GIT_REMOTE" 2>/dev/null || true)"
fi
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"

echo -e "${BLUE}🔄 开始 ${BACKUP_TYPE} 备份...${NC}"

if [ "$PULL_BEFORE" -eq 1 ]; then
  if git diff --quiet && git diff --staged --quiet; then
    echo -e "${BLUE}⬇️  拉取最新代码...${NC}"
    git pull --rebase || echo -e "${YELLOW}⚠️  git pull 失败，请手动处理${NC}"
  else
    echo -e "${YELLOW}⚠️  工作区有未提交变更，跳过 git pull${NC}"
  fi
fi

# 检查是否有更改
if [ -z "$(git status --porcelain)" ]; then
  echo -e "${YELLOW}⚠️  没有需要备份的更改${NC}"
  exit 0
fi

if [ "$DRY_RUN" -eq 1 ]; then
  echo -e "${BLUE}📄 变更预览:${NC}"
  git status --short
  exit 0
fi

# 统计更改的文件
CHANGED_FILES=$(git status --short | wc -l | tr -d ' ')
echo -e "${BLUE}📁 发现 ${CHANGED_FILES} 个文件有更改${NC}"

# 默认提交信息
if [ -z "$COMMIT_MSG" ]; then
  case "$BACKUP_TYPE" in
    full)   DISPLAY_TYPE="Full" ;;
    skills) DISPLAY_TYPE="Skills" ;;
    *)      DISPLAY_TYPE="Manual" ;;
  esac
  COMMIT_MSG="$DISPLAY_TYPE backup: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 添加所有更改
echo -e "${BLUE}➕ 添加更改到暂存区...${NC}"
git add -A

# 提交
echo -e "${BLUE}💾 提交更改...${NC}"
git commit -m "$COMMIT_MSG"

# 推送到 GitHub
if [ "$NO_PUSH" -eq 0 ]; then
  echo -e "${BLUE}☁️  推送到 GitHub...${NC}"
  if [ -n "$GIT_REMOTE" ] && [ -n "$CURRENT_BRANCH" ]; then
    if ! git push "$GIT_REMOTE" "$CURRENT_BRANCH"; then
      echo -e "${RED}✗ 推送失败：可能需要先 git pull --rebase${NC}"
      exit 1
    fi
  else
    if ! git push; then
      echo -e "${RED}✗ 推送失败：请检查 Git 远端或设置上游分支${NC}"
      exit 1
    fi
  fi
else
  echo -e "${YELLOW}⚠️  跳过推送（--no-push）${NC}"
fi

echo -e "${GREEN}✅ 备份完成！${NC}"
echo -e "${BLUE}📦 仓库地址: ${REPO_URL:-N/A}${NC}"
if [ -n "$CURRENT_BRANCH" ]; then
  echo -e "${BLUE}🌿 分支: ${GIT_REMOTE:-?}/${CURRENT_BRANCH}${NC}"
fi
echo -e "${BLUE}📝 提交信息: ${COMMIT_MSG}${NC}"
echo ""
echo -e "${YELLOW}💡 提示: 可以设置定时自动备份${NC}"
