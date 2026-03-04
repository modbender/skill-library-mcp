#!/bin/bash
# remote-exec.sh - 远程执行命令（仅支持预定义安全命令集）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common.sh"

#=============================================================================
# 安全命令白名单
#=============================================================================

# 允许的命令前缀列表（只读命令）
SAFE_COMMAND_PREFIXES=(
    # 系统信息
    "uptime"
    "uname"
    "hostname"
    "cat /etc/os-release"
    "date"
    "timedatectl"
    # CPU
    "cat /proc/loadavg"
    "top -bn1"
    "mpstat"
    "nproc"
    "lscpu"
    # 内存
    "free"
    "cat /proc/meminfo"
    "vmstat"
    # 磁盘
    "df"
    "lsblk"
    "fdisk -l"
    "du -sh"
    "du -h"
    # 进程
    "ps aux"
    "ps -ef"
    "pgrep"
    "pidof"
    # 网络
    "ip addr"
    "ip route"
    "ifconfig"
    "netstat"
    "ss -"
    "ping -c"
    "curl -I"
    "curl -s"
    "dig"
    "nslookup"
    "traceroute"
    "tracepath"
    # 服务
    "systemctl status"
    "systemctl is-active"
    "systemctl is-enabled"
    "systemctl list-units"
    "service"
    # 日志（只读）
    "tail -n"
    "tail -f"
    "head -n"
    "journalctl"
    "dmesg"
    "cat /var/log"
    # 安全审计
    "who"
    "w"
    "last"
    "lastlog"
    "cat /etc/passwd"
    "cat /etc/group"
    "id"
    "groups"
    # 其他只读
    "env"
    "printenv"
    "crontab -l"
    "docker ps"
    "docker images"
    "docker stats --no-stream"
    "nginx -t"
    "nginx -T"
    "php -v"
    "node -v"
    "python --version"
    "python3 --version"
    "java -version"
    "mysql --version"
    "redis-cli info"
    "redis-cli ping"
)

# 危险命令黑名单（即使匹配白名单前缀也禁止）
DANGEROUS_PATTERNS=(
    "rm "
    "rm -"
    "rmdir"
    "dd "
    "mkfs"
    "fdisk -"
    "> "
    ">> "
    "wget "
    "curl -o"
    "curl -O"
    "chmod "
    "chown "
    "chgrp "
    "useradd"
    "userdel"
    "usermod"
    "passwd"
    "sudo "
    "su "
    "shutdown"
    "reboot"
    "halt"
    "poweroff"
    "init "
    "systemctl start"
    "systemctl stop"
    "systemctl restart"
    "systemctl enable"
    "systemctl disable"
    "kill "
    "killall"
    "pkill"
    "mv "
    "cp "
    "; "
    "&&"
    "||"
    "|"
    "\`"
    "\$("
    "eval "
    "exec "
    "source "
    ". "
)

# 校验命令是否安全
validate_command() {
    local cmd="$1"
    
    # 去除首尾空格
    cmd=$(echo "$cmd" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    
    # 检查危险模式
    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
        if [[ "$cmd" == *"$pattern"* ]]; then
            error "命令包含危险操作: $pattern"
            echo "出于安全考虑，此命令被禁止执行" >&2
            return 1
        fi
    done
    
    # 检查是否匹配安全命令前缀
    for safe_prefix in "${SAFE_COMMAND_PREFIXES[@]}"; do
        if [[ "$cmd" == "$safe_prefix" ]] || [[ "$cmd" == "$safe_prefix "* ]]; then
            return 0
        fi
    done
    
    error "不支持的命令: $cmd"
    echo "" >&2
    echo "仅支持预定义的安全命令集，包括：" >&2
    echo "  - 系统信息: uptime, uname, hostname, date" >&2
    echo "  - 资源监控: top, free, df, ps" >&2
    echo "  - 网络检查: ip addr, netstat, ping, curl -I" >&2
    echo "  - 服务状态: systemctl status" >&2
    echo "  - 日志查看: tail, head, journalctl" >&2
    echo "" >&2
    echo "详细列表请参阅 SKILL.md" >&2
    return 1
}

#=============================================================================
# 主逻辑
#=============================================================================

show_help() {
    print_help_header "remote-exec.sh" "在远程服务器执行安全命令"
    cat <<EOF
  --instance-id <id>      实例 ID（自动获取密码和 IP）
  --host <ip>             IP 地址
  --user <user>           用户名，默认 root
  --password <pwd>        密码
  --cmd <command>         要执行的命令（必需，仅支持安全命令集）
  --list-commands         列出支持的安全命令
  -h, --help              显示帮助

安全限制:
  仅支持预定义的只读命令，禁止执行写操作和危险命令。
  详细的安全命令列表请参阅 SKILL.md

示例:
  $0 --instance-id ins-xxx --cmd "df -h"
  $0 --instance-id ins-xxx --cmd "systemctl status nginx"
  $0 --instance-id ins-xxx --cmd "top -bn1"
  $0 --list-commands

EOF
}

list_safe_commands() {
    echo ""
    echo "========== 支持的安全命令 =========="
    echo ""
    echo "系统信息:"
    echo "  uptime, uname, hostname, cat /etc/os-release, date, timedatectl"
    echo ""
    echo "CPU:"
    echo "  cat /proc/loadavg, top -bn1, mpstat, nproc, lscpu"
    echo ""
    echo "内存:"
    echo "  free, cat /proc/meminfo, vmstat"
    echo ""
    echo "磁盘:"
    echo "  df, lsblk, fdisk -l, du -sh <path>"
    echo ""
    echo "进程:"
    echo "  ps aux, ps -ef, pgrep <name>, pidof <name>"
    echo ""
    echo "网络:"
    echo "  ip addr, ip route, netstat, ss, ping -c <n> <host>"
    echo "  curl -I <url>, dig <domain>, traceroute <host>"
    echo ""
    echo "服务:"
    echo "  systemctl status <service>, systemctl is-active <service>"
    echo "  systemctl list-units"
    echo ""
    echo "日志:"
    echo "  tail -n <n> <file>, head -n <n> <file>"
    echo "  journalctl -u <service>, dmesg"
    echo ""
    echo "安全:"
    echo "  who, w, last, cat /etc/passwd, cat /etc/group"
    echo ""
    echo "其他:"
    echo "  env, crontab -l, docker ps, docker images"
    echo ""
    echo "===================================="
}

check_ssh_prerequisites

INSTANCE_ID="" HOST="" USER="root" PORT=22 PASSWORD="" CMD=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --instance-id)    INSTANCE_ID="$2"; shift 2 ;;
        --host)           HOST="$2"; shift 2 ;;
        --user)           USER="$2"; shift 2 ;;
        --password)       PASSWORD="$2"; shift 2 ;;
        --cmd)            CMD="$2"; shift 2 ;;
        --list-commands)  list_safe_commands; exit 0 ;;
        -h|--help)        show_help; exit 0 ;;
        *)                error "未知参数: $1"; exit 1 ;;
    esac
done

[[ -z "$CMD" ]] && { error "缺少必需参数: --cmd"; exit 1; }

# 安全校验
validate_command "$CMD" || exit 1

resolve_ops_connection "$INSTANCE_ID" "$HOST" "$PASSWORD" || exit 1
HOST="$OPS_HOST"
PASSWORD="$OPS_PASSWORD"

info "在 $HOST 执行命令: $CMD"
echo ""
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USER@$HOST" "$CMD"
echo ""
success "命令执行完成"
