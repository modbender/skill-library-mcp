#!/bin/bash
set -e

# Get absolute path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(pwd)"
BACKUP_DIR="$WORKSPACE_ROOT/.tricore_backup/$(date +%Y%m%d%H%M%S)"

echo "[TriCore] Initializing TriCore Architecture / 正在初始化 TriCore 架构..."

# ==========================================
# 兜底回滚机制 (Fallback Rollback Mechanism)
# ==========================================
function cleanup_on_error {
    echo ""
    echo "[!] ❌ Installation failed! Initiating rollback... / 安装失败！触发回滚机制..."
    
    if [ -f "$BACKUP_DIR/POLICY.md" ]; then
        cp "$BACKUP_DIR/POLICY.md" "$WORKSPACE_ROOT/POLICY.md"
        echo "  - Restored / 已恢复: POLICY.md"
    fi
    
    if [ -f "$BACKUP_DIR/MEMORY.md" ]; then
        cp "$BACKUP_DIR/MEMORY.md" "$WORKSPACE_ROOT/MEMORY.md"
        echo "  - Restored / 已恢复: MEMORY.md"
    fi
    
    if [ -f "$BACKUP_DIR/memctl.py" ]; then
        cp "$BACKUP_DIR/memctl.py" "$WORKSPACE_ROOT/tools/memctl.py"
    elif [ -f "$WORKSPACE_ROOT/tools/memctl.py" ]; then
        # 如果原来没有 memctl.py，我们就把它删掉
        rm -f "$WORKSPACE_ROOT/tools/memctl.py"
    fi
    
    echo "[!] Rollback completed. System restored to pre-install state. / 回滚完成，系统已恢复至安装前状态。"
    exit 1
}

# 绑定 ERR 信号，脚本中途报错则执行回滚
trap cleanup_on_error ERR

# 创建预检备份
echo "[TriCore] Creating pre-install backups / 创建安装前备份..."
mkdir -p "$BACKUP_DIR"
[ -f "$WORKSPACE_ROOT/POLICY.md" ] && cp "$WORKSPACE_ROOT/POLICY.md" "$BACKUP_DIR/POLICY.md"
[ -f "$WORKSPACE_ROOT/MEMORY.md" ] && cp "$WORKSPACE_ROOT/MEMORY.md" "$BACKUP_DIR/MEMORY.md"
[ -f "$WORKSPACE_ROOT/tools/memctl.py" ] && cp "$WORKSPACE_ROOT/tools/memctl.py" "$BACKUP_DIR/memctl.py"

# ==========================================
# 核心安装逻辑 (Core Installation Logic)
# ==========================================

# 1. Dependency Check
echo "[TriCore] Checking system environment / 检查系统环境..."
if ! command -v python3 &> /dev/null; then
    echo "[!] FATAL: Python 3 is not installed."
    exit 1
fi

if ! command -v agent-browser &> /dev/null; then
    echo "[!] WARNING: agent-browser not detected. (Recommended for self-evolution)"
fi

# 2. Ensure core directories exist
echo "[TriCore] Creating state and memory directory tree / 创建状态与记忆目录树..."
mkdir -p "$WORKSPACE_ROOT/tools"
mkdir -p "$WORKSPACE_ROOT/memory/state"
mkdir -p "$WORKSPACE_ROOT/memory/daily"
mkdir -p "$WORKSPACE_ROOT/memory/sessions"
mkdir -p "$WORKSPACE_ROOT/memory/kb"
mkdir -p "$WORKSPACE_ROOT/memory/archive"

# 3. Deploy Engine & Skills
echo "[TriCore] Deploying memctl engine and cognitive skills / 部署 memctl 引擎与认知技能..."
cp "$SCRIPT_DIR/tools/memctl.py" "$WORKSPACE_ROOT/tools/memctl.py"

for skill in planning-with-files react-agent self-evolution; do
    if [ -f "$SCRIPT_DIR/cognitive-skills/${skill}.md" ]; then
        mkdir -p "$WORKSPACE_ROOT/skills/${skill}"
        # Copy English default
        cp "$SCRIPT_DIR/cognitive-skills/${skill}.md" "$WORKSPACE_ROOT/skills/${skill}/SKILL.md"
        # Copy Chinese if exists
        if [ -f "$SCRIPT_DIR/cognitive-skills/${skill}_zh.md" ]; then
            cp "$SCRIPT_DIR/cognitive-skills/${skill}_zh.md" "$WORKSPACE_ROOT/skills/${skill}/SKILL_zh.md"
        fi
        echo "  - Deployed cognitive skill / 部署了认知技能: ${skill}"
    fi
done

# 4. Legacy MEMORY.md Check
echo "[TriCore] Checking and migrating legacy MEMORY.md / 正在检查和迁移遗留的 MEMORY.md..."
python3 "$WORKSPACE_ROOT/tools/memctl.py" migrate_legacy

# 5. Ensure Base Files
python3 "$WORKSPACE_ROOT/tools/memctl.py" ensure

# 6. Deploy Linter to POLICY.md
POLICY_FILE="$WORKSPACE_ROOT/POLICY.md"
if [ ! -f "$POLICY_FILE" ]; then
    echo "# POLICY.md - Core Security Rules" > "$POLICY_FILE"
fi

if ! grep -q "TriCore Compliance" "$POLICY_FILE"; then
    echo "" >> "$POLICY_FILE"
    echo "### Memory Management (TriCore Compliance)" >> "$POLICY_FILE"
    echo "- **[CRITICAL: TriCore Compliance]** The entire system adopts the 'TriCore' architecture. It is strictly forbidden to use stray markdown files (like task_plan.md, findings.md, memory/daily-learning/) in the root directory or unauthorized places to manage states!" >> "$POLICY_FILE"
    echo "- **Hard Constraint 1**: Any state persistence or knowledge accumulation **MUST** use python3 tools/memctl.py (capture|kb_append|work_upsert). Modifying markdown directly via shell (>>) is forbidden." >> "$POLICY_FILE"
    echo "- **Hard Constraint 2**: Before adding/modifying cron jobs or creating/editing any skill's SKILL.md, you **MUST run** 'python3 tools/memctl.py lint <cmd/path>' to review compliance. LINT ERROR means you must refactor." >> "$POLICY_FILE"
    echo "- **MEMORY.md** (Main memory file) must remain extremely short (summary + pointers). Dumping long documents here is prohibited." >> "$POLICY_FILE"
    echo "[TriCore] Injected Linter and architectural constraints into POLICY.md."
else
    echo "[TriCore] POLICY.md already contains compliance constraints."
fi

# 7. Configure Pre-compaction Override
echo "[TriCore] Configuring OpenClaw Pre-compaction Memory Flush prompt / 配置系统 Token 压缩的记忆刷写提示词..."
openclaw config set agents.defaults.compaction.memoryFlush.prompt "[TriCore 架构约束] Tokens 快超出上限，系统即将执行上下文清理 (Compaction)。请将此会话中尚未归档的长期事实、工作流经验和重要状态提取出来。【TriCore 强制写入规范】：绝对禁止使用 edit 或 bash 追加 md 日志！事实提取使用 python3 tools/memctl.py kb_append facts '...'，经验提取使用 python3 tools/memctl.py kb_append playbooks '...'，如果没有需要持久化的记忆，请只回复：NO_REPLY" > /dev/null

# 解除错误陷阱，因为已经成功
trap - ERR

echo "=================================================="
echo "[TriCore] Initialization Complete! / 初始化完成！"
echo "Run 'python3 tools/memctl.py --help' to see supported commands."
echo "If you wish to uninstall, run 'bash uninstall.sh' from this skill directory."
echo "=================================================="