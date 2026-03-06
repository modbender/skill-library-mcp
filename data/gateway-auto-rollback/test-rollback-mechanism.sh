#!/bin/bash
# 测试回滚机制的完整性

set -e

CONFIG_FILE="$HOME/.openclaw/openclaw.json"
BACKUP_DIR="$HOME/.openclaw/backup"
TEST_DIR="/tmp/rollback-test"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}✅ PASS${NC} $1"
}

log_fail() {
    echo -e "${RED}❌ FAIL${NC} $1"
    exit 1
}

echo "======================================"
echo "回滚机制完整性测试"
echo "======================================"

# 测试 1: 检查备份目录
log_test "检查备份目录..."
if [ -d "$BACKUP_DIR" ]; then
    log_pass "备份目录存在"
else
    log_fail "备份目录不存在"
fi

# 测试 2: 检查配置文件
log_test "检查配置文件..."
if [ -f "$CONFIG_FILE" ]; then
    log_pass "配置文件存在"
else
    log_fail "配置文件不存在"
fi

# 测试 3: JSON 验证
log_test "验证 JSON 语法..."
if python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
    log_pass "JSON 语法有效"
else
    log_fail "JSON 语法无效"
fi

# 测试 4: 哈希计算
log_test "测试哈希计算..."
HASH=$(python3 -c "
import hashlib
with open('$CONFIG_FILE', 'rb') as f:
    print(hashlib.sha256(f.read()).hexdigest()[:8])
")
if [ ${#HASH} -eq 8 ]; then
    log_pass "哈希计算成功: $HASH"
else
    log_fail "哈希计算失败"
fi

# 测试 5: Gateway 健康检查
log_test "检查 Gateway 健康状态..."
if timeout 3 curl -s http://127.0.0.1:18789/api/health > /dev/null 2>&1; then
    log_pass "Gateway 健康"
else
    echo -e "${YELLOW}⚠️ WARNING${NC} Gateway 可能不运行，测试跳过"
fi

# 测试 6: 备份创建测试
log_test "测试备份创建..."
mkdir -p "$TEST_DIR"
cp "$CONFIG_FILE" "$TEST_DIR/test-config.json"

# 计算测试文件哈希
TEST_HASH=$(python3 -c "
import hashlib
with open('$TEST_DIR/test-config.json', 'rb') as f:
    print(hashlib.sha256(f.read()).hexdigest()[:8])
")

# 模拟备份命名
TEST_BACKUP="$TEST_DIR/test-config.json.20260301_053612.$TEST_HASH.bak"
cp "$TEST_DIR/test-config.json" "$TEST_BACKUP"

if [ -f "$TEST_BACKUP" ]; then
    log_pass "备份创建成功: $(basename $TEST_BACKUP)"
else
    log_fail "备份创建失败"
fi

# 测试 7: 回滚操作
log_test "测试回滚操作..."
cp "$TEST_BACKUP" "$TEST_DIR/test-restore.json"

# 验证恢复文件
if python3 -c "import json; json.load(open('$TEST_DIR/test-restore.json'))" 2>/dev/null; then
    log_pass "回滚文件验证通过"
else
    log_fail "回滚文件验证失败"
fi

# 测试 8: 监视进程检查
log_test "检查监视守护进程..."
if pgrep -f "gateway-auto-rollback.py.*--watch" > /dev/null 2>&1; then
    PID=$(pgrep -f "gateway-auto-rollback.py.*--watch")
    log_pass "监视进程运行中 (PID: $PID)"
elif pgrep -f "config-modification-hook.py.*--watch" > /dev/null 2>&1; then
    PID=$(pgrep -f "config-modification-hook.py.*--watch")
    log_pass "监视进程运行中 (PID: $PID)"
else
    echo -e "${YELLOW}⚠️ WARNING${NC} 监视进程未运行"
fi

# 测试 9: 日志文件检查
log_test "检查日志文件..."
LOG_FILE="$HOME/.openclaw/logs/config-modification.log"
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE")
    log_pass "日志文件存在 (大小: $LOG_SIZE 字节)"
else
    echo -e "${YELLOW}⚠️ WARNING${NC} 日志文件不存在（首次运行是正常的）"
fi

# 测试 10: 脚本权限检查
log_test "检查脚本权限..."
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_FILE="$SKILL_DIR/gateway-auto-rollback.py"
if [ -x "$SCRIPT_FILE" ]; then
    log_pass "脚本可执行: $SCRIPT_FILE"
else
    # Fallback to legacy path
    SCRIPT_FILE="$HOME/.openclaw/workspace/.lib/config-modification-hook.py"
    if [ -x "$SCRIPT_FILE" ]; then
        log_pass "脚本可执行 (legacy path)"
    else
        log_fail "脚本不可执行"
    fi
fi

# 清理测试文件
log_test "清理测试文件..."
rm -rf "$TEST_DIR"
log_pass "清理完成"

# 总结
echo ""
echo "======================================"
echo -e "${GREEN}✅ 所有测试完成${NC}"
echo "======================================"
echo ""
echo "📝 建议："
echo "1. 监视守护进程应 24/7 运行"
echo "2. 定期检查 ~/.openclaw/backup/ 目录大小"
echo "3. 配置 cron 任务进行自动备份和清理"
echo "4. 每月审查一次日志文件"
echo ""
