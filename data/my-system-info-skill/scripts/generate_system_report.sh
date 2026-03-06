#!/bin/bash

# 创建system-tool-results目录（如果不存在）
SYSTEM_TOOL_RESULTS_DIR="system-tool-results"
if [ ! -d "$SYSTEM_TOOL_RESULTS_DIR" ]; then
    mkdir -p "$SYSTEM_TOOL_RESULTS_DIR"
fi

# 获取当前日期时间作为文件名后缀
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_FILE="$SYSTEM_TOOL_RESULTS_DIR/system_report_$TIMESTAMP.md"

# 生成Markdown格式的系统报告
{
    echo "# 系统运维报告"
    echo "**生成时间：** $(date +"%Y-%m-%d %H:%M:%S")"
    echo ""
    
    echo "## 1. 系统基本信息"
    echo "**主机名：** $(hostname)"
    echo "**操作系统：** $(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d'"' -f2 || uname -a)"
    echo "**内核版本：** $(uname -r)"
    echo "**当前用户：** $(whoami)"
    echo "**系统运行时间：** $(uptime -p)"
    echo ""
    
    echo "## 2. CPU信息"
    echo "<details>"
    echo "<summary>🔍 点击查看详细CPU信息 (lscpu)</summary>"
    
    echo "| CPU属性 | 详情 |"
    echo "|---------|------|"
    lscpu | awk 'NR>1 {printf "| %s | %s |\n", $1, $2}'
    
    echo "</details>"
    echo ""
    
    echo "## 3. 内存信息"
    echo "<details>"
    echo "<summary>🔍 点击查看详细内存信息 (free -h)</summary>"
    free -h
    echo "</details>"
    echo ""
    
    echo "## 4. 磁盘信息"
    echo "### 4.1 块设备信息"
    echo "<details>"
    echo "<summary>🔍 点击查看块设备信息 (lsblk)</summary>"
    lsblk
    echo "</details>"
    echo ""
    echo "### 4.2 磁盘使用情况"
    echo "<details>"
    echo "<summary>🔍 点击查看磁盘使用情况 (df -h)</summary>"
    df -h
    echo "</details>"
    echo ""
    
    echo "## 5. 网络信息"
    echo "<details>"
    echo "<summary>🔍 点击查看网络接口信息 (ip addr)</summary>"
    ip addr
    echo "</details>"
    echo ""
    
    echo "## 6. 进程信息"
    echo "<details>"
    echo "<summary>🔍 点击查看进程信息 (top -bn1)</summary>"
    top -bn1 | head -20
    echo "</details>"
    echo ""
    
    echo "## 7. 服务状态"
    echo "<details>"
    echo "<summary>🔍 点击查看运行中的服务 (systemctl list-units --type=service --state=running)</summary>"
    systemctl list-units --type=service --state=running 2>/dev/null || echo "systemctl命令不可用"
    echo "</details>"
    
    echo "---"
    echo "*报告由系统自动生成*"
} > "$REPORT_FILE"

# 获取报告的绝对路径
ABSOLUTE_REPORT_PATH=$(realpath "$REPORT_FILE" 2>/dev/null || echo "$REPORT_FILE")

echo "Markdown格式的系统报告已生成："
echo "$ABSOLUTE_REPORT_PATH"
echo "您可以使用浏览器或Markdown查看器打开此文件查看格式化的报告。"
