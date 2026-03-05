#!/bin/bash

# NightPatch Skill Cron集成脚本
# 设置定时自动运行夜间修补

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 技能目录
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_SCRIPT="$SKILL_DIR/run-nightly.sh"
CRON_JOB="0 3 * * * cd $SKILL_DIR && ./run-nightly.sh >> $SKILL_DIR/logs/cron.log 2>&1"

echo -e "${GREEN}NightPatch Skill Cron集成设置${NC}"
echo "=" * 50

# 创建运行脚本
cat > "$CRON_SCRIPT" << 'EOF'
#!/bin/bash
# NightPatch 夜间自动运行脚本

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SKILL_DIR/logs/nightly-run-$(date +%Y%m%d).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "========================================" >> "$LOG_FILE"
echo "NightPatch 夜间运行 - $TIMESTAMP" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 检查是否应该运行（避免生产环境）
if [ "$NODE_ENV" = "production" ]; then
    echo "⚠️  生产环境，跳过夜间修补" >> "$LOG_FILE"
    exit 0
fi

# 运行夜间修补
cd "$SKILL_DIR"
echo "开始运行夜间修补..." >> "$LOG_FILE"

# 使用手动模式运行
if ./start.sh run >> "$LOG_FILE" 2>&1; then
    echo "✅ 夜间修补完成" >> "$LOG_FILE"
else
    echo "❌ 夜间修补失败" >> "$LOG_FILE"
    # 发送错误通知（可以扩展）
    echo "错误详情请查看日志: $LOG_FILE" >> "$LOG_FILE"
fi

echo "运行完成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
EOF

chmod +x "$CRON_SCRIPT"
echo -e "${GREEN}✅ 创建运行脚本: $CRON_SCRIPT${NC}"

# 创建日志目录
mkdir -p "$SKILL_DIR/logs"
echo -e "${GREEN}✅ 创建日志目录${NC}"

# 显示cron配置
echo ""
echo -e "${YELLOW}📅 Cron配置示例:${NC}"
echo "$CRON_JOB"
echo ""
echo -e "${YELLOW}📝 添加cron作业的方法:${NC}"
echo "1. 运行 crontab -e"
echo "2. 添加以下行:"
echo "   $CRON_JOB"
echo "3. 保存并退出"
echo ""
echo -e "${YELLOW}🔧 手动测试运行:${NC}"
echo "cd $SKILL_DIR && ./run-nightly.sh"
echo ""
echo -e "${YELLOW}📊 查看日志:${NC}"
echo "tail -f $SKILL_DIR/logs/cron.log"
echo "tail -f $SKILL_DIR/logs/nightly-run-*.log"
echo ""
echo -e "${GREEN}🎉 Cron集成设置完成！${NC}"
echo ""
echo -e "${YELLOW}⚠️  注意:${NC}"
echo "- 默认运行时间: 每天凌晨3点"
echo "- 生产环境会自动跳过"
echo "- 所有操作都有详细日志"
echo "- 确保Node.js和依赖已安装"

# 测试运行脚本（仅打印命令，不实际执行）
echo ""
echo -e "${YELLOW}⚠️  安全提示：${NC}"
echo -e "${YELLOW}   脚本安装完成，但不会自动运行。${NC}"
echo -e "${YELLOW}   建议先手动测试：${NC}"
echo ""
echo -e "${CYAN}   cd \"$SKILL_DIR\" && ./start.sh dry-run${NC}"
echo ""
echo -e "${YELLOW}   确认无误后，可手动运行：${NC}"
echo -e "${CYAN}   cd \"$SKILL_DIR\" && ./start.sh run${NC}"
echo ""
echo -e "${YELLOW}   或等待cron定时执行。${NC}"