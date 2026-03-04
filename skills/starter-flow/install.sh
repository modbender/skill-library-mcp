#!/bin/bash

# 🚀 Starter Flow - 启动流
# 交互式安装脚本（Phase 1）
# 版本：v1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 技能列表
declare -a SKILLS=(
    "token-estimator:Token 预估:预估 Token 消耗，避免超支"
    "smart-router:智能压缩:自动压缩内容，节省 60-80% Token"
    "command-flow:命令全览:说中文就懂，不用记英文"
    "skill-dashboard:技能管理:像管手机 APP 一样简单"
    "token-water-meter:用量监控:实时查看 Token 使用情况"
)

# 用户选择（默认全选）
declare -a SELECTED=(true true true true true)

# 清屏
clear

# 显示标题
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  🚀 Starter Flow - 启动流                              ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}  5 个核心技能，3 分钟快速上手 OpenClaw                   ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 安全声明
echo -e "${GREEN}✅ 安全声明：${NC}"
echo "   • 所有技能本地运行，无云端依赖"
echo "   • 用户自主选择，无强制安装"
echo "   • 可随时卸载，无残留"
echo ""

# 主循环
while true; do
    echo -e "${YELLOW}请选择要安装的技能（输入数字切换，A 全选，N 全不选，I 安装）：${NC}"
    echo ""
    
    # 显示技能列表
    for i in "${!SKILLS[@]}"; do
        IFS=':' read -r name cn desc <<< "${SKILLS[$i]}"
        if [ "${SELECTED[$i]}" = true ]; then
            echo -e "   ${GREEN}[✓]${NC} $((i+1)). $cn ($name)"
        else
            echo -e "   [ ] $((i+1)). $cn ($name)"
        fi
        echo -e "       ${BLUE}→${NC} $desc"
    done
    
    echo ""
    echo -e "${YELLOW}语言/Language:${NC} [1] 中文  [2] English"
    echo ""
    read -p "输入选项 (1-5/A/N/I/1-2): " choice
    
    case $choice in
        1|2|3|4|5)
            idx=$((choice-1))
            if [ "${SELECTED[$idx]}" = true ]; then
                SELECTED[$idx]=false
            else
                SELECTED[$idx]=true
            fi
            clear
            ;;
        a|A)
            SELECTED=(true true true true true)
            clear
            ;;
        n|N)
            SELECTED=(false false false false false)
            clear
            ;;
        i|I)
            break
            ;;
        1)
            # 中文已默认，此处可扩展英文支持
            clear
            ;;
        2)
            # 英文支持（Phase 2）
            echo "English support coming in Phase 2..."
            sleep 2
            clear
            ;;
        *)
            echo -e "${RED}无效选项，请重新输入${NC}"
            sleep 1
            clear
            ;;
    esac
done

# 统计选择
count=0
for i in "${!SELECTED[@]}"; do
    if [ "${SELECTED[$i]}" = true ]; then
        ((count++))
    fi
done

# 确认安装
if [ $count -eq 0 ]; then
    echo -e "${RED}✗ 未选择任何技能，退出安装${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}将安装 $count 个技能：${NC}"
for i in "${!SKILLS[@]}"; do
    if [ "${SELECTED[$i]}" = true ]; then
        IFS=':' read -r name cn desc <<< "${SKILLS[$i]}"
        echo -e "   ${GREEN}✓${NC} $cn ($name)"
    fi
done
echo ""

read -p "确定要安装吗？(y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}取消安装${NC}"
    exit 0
fi

# 执行安装
echo ""
echo -e "${BLUE}开始安装...${NC}"
echo ""

for i in "${!SKILLS[@]}"; do
    if [ "${SELECTED[$i]}" = true ]; then
        IFS=':' read -r name cn desc <<< "${SKILLS[$i]}"
        echo -e "${GREEN}→${NC} 安装 $cn ($name)..."
        
        if clawhub install "$name"; then
            echo -e "   ${GREEN}✓${NC} 安装成功"
        else
            echo -e "   ${RED}✗${NC} 安装失败，跳过"
        fi
        echo ""
    fi
done

# 安装完成引导
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  ✅ Starter Flow 安装完成！                             ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}现在你可以：${NC}"
echo ""
echo "   1️⃣  说\"斜杠命令\"查看所有命令"
echo "   2️⃣  说\"技能控制台\"管理已安装技能"
echo "   3️⃣  说\"Token 用量\"查看当前消耗"
echo ""
echo -e "${BLUE}💡 提示：${NC}可随时卸载不需要的技能"
echo ""
echo -e "${GREEN}🎉 开始使用吧！${NC}"
echo ""
