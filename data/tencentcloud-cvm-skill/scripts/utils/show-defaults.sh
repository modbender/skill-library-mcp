#!/bin/bash
# show-defaults.sh - 显示当前默认配置

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

show_help() {
    print_help_header "show-defaults.sh" "显示当前默认配置和环境变量"
    cat <<EOF
  -h, --help              显示帮助

配置优先级:
  1. 命令行参数
  2. 环境变量 TENCENT_CVM_DEFAULT_*
  3. 内置默认值

EOF
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help) show_help; exit 0 ;;
        *)         error "未知参数: $1"; exit 1 ;;
    esac
done

load_defaults

print_section "当前默认配置"
cat <<EOF
地域:       ${REGION:-未设置}  (TENCENT_CVM_DEFAULT_REGION)
可用区:     ${ZONE:-未设置}  (TENCENT_CVM_DEFAULT_ZONE)
实例规格:   ${INSTANCE_TYPE:-未设置}  (TENCENT_CVM_DEFAULT_INSTANCE_TYPE)
镜像 ID:    ${IMAGE_ID:-未设置}  (TENCENT_CVM_DEFAULT_IMAGE_ID)
系统盘:     ${DISK_SIZE}GB  (TENCENT_CVM_DEFAULT_DISK_SIZE)
数据盘:     ${DATA_DISK_SIZE:-不创建}  (TENCENT_CVM_DEFAULT_DATA_DISK_SIZE)
VPC:        ${VPC_ID:-未设置}  (TENCENT_CVM_DEFAULT_VPC_ID)
子网:       ${SUBNET_ID:-未设置}  (TENCENT_CVM_DEFAULT_SUBNET_ID)
安全组:     ${SG_ID:-未设置}  (TENCENT_CVM_DEFAULT_SG_ID)
计费类型:   ${CHARGE_TYPE}  (TENCENT_CVM_DEFAULT_CHARGE_TYPE)
EOF
echo "=================================="

print_section "密码存储"
echo "文件: $CVM_PASSWORD_FILE"
if [[ -f "$CVM_PASSWORD_FILE" ]]; then
    count=$(jq 'keys | length' "$CVM_PASSWORD_FILE")
    echo "已保存: $count 个实例"
else
    echo "已保存: 0 个实例"
fi
echo "=================================="
