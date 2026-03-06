#!/bin/bash

# ==============================================================================
# Script: pl-init.sh
# Description: 创建规划文件
# Usage: ./pl-init.sh <plan-name>
# ==============================================================================

# 配置
PLANS_DIR="plans"
DATE=$(date +%Y%m%d)
TIME=$(date +%H%M%S)


# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 函数：打印帮助信息
show_help() {
    echo -e "${YELLOW}用法:${NC} ./pl-init.sh <plan-name>"
    echo -e "  名称：必须填写名称"
}

# 主逻辑
main() {
    # 1. 检查参数
    if [ -z "$1" ]; then
        show_help
        exit 1
    fi

    if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
        show_help
        exit 0
    fi

    local plan_name="$1"

    # 2. 确保目录存在
    if [ ! -d "$PLANS_DIR/${DATE}" ]; then
        mkdir -p "$PLANS_DIR/${DATE}"
    fi

    local file_path="${PLANS_DIR}/${DATE}/${TIME}-${plan_name}.md"

    # 3. 检查文件是否存在
    if [ -f "$file_path" ]; then
        echo -e "${RED}错误：文件 '$file_path' 已存在${NC}"
        exit 1
    fi

    # 4. 创建文件并写入头部信息
    local datetime=$(date +"%Y-%m-%d %H:%M:%S")
    cat > "$file_path" <<EOF
/plan: 与我共创此文件, 不要做任何实现, 共创文件, 每轮讨论你都要更新此文件, 现在处于规划设计阶段。严禁编写任何具体的代码。我们只讨论规划。如果我没明确说‘开始编码’，请不要输出具体实现逻辑。
---
**创建时间**: ${DATE}
**讨论记录**:
1. 已创建规划文件
---
# ${plan_name}

EOF
    echo -e "${GREEN}✓ 创建成功：$file_path${NC}"
}

main "$@"
