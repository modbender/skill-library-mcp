#!/bin/bash
#
# PC Healthcheck Script (Enhanced)
# Gathers comprehensive system information for health analysis
#
# Optimized with timeouts and quick mode support
#

# Don't exit on error - some commands may fail gracefully
set +e

# Timeout settings (seconds)
TIMEOUT_SMALL=5
TIMEOUT_MEDIUM=15
TIMEOUT_LARGE=30

# Run command with timeout
timeout_cmd() {
    local timeout=$1
    shift
    timeout "$timeout" "$@" 2>/dev/null || true
}

# Check for quick mode FIRST (before setting up output dir)
QUICK_MODE=0
if [ "$1" = "--quick" ]; then
    QUICK_MODE=1
    shift  # Remove --quick from args
fi

OUTPUT_DIR="${1:-/tmp/pc-healthcheck}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="${OUTPUT_DIR}/healthcheck_${TIMESTAMP}.txt"
JSON_FILE="${OUTPUT_DIR}/healthcheck_${TIMESTAMP}.json"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Log mode
if [ "$QUICK_MODE" = "1" ]; then
    log_info "Running in QUICK mode (fast, essential checks only)"
fi

log_info "Starting Enhanced PC Healthcheck..."
log_info "Output directory: $OUTPUT_DIR"

# Initialize report
cat > "$REPORT_FILE" << 'EOF'
================================================================================
                    🖥️ ENHANCED PC HEALTHCHECK REPORT
================================================================================

EOF

echo "Generated: $(date)" >> "$REPORT_FILE"
echo "Hostname: $(hostname)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# ============================================
# 1. SYSTEM INFORMATION
# ============================================
section() {
    echo "" >> "$REPORT_FILE"
    echo "================================================================================" >> "$REPORT_FILE"
    echo "  $1" >> "$REPORT_FILE"
    echo "================================================================================" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    log_info "Collecting: $1"
}

subsection() {
    echo "" >> "$REPORT_FILE"
    echo "--- $1 ---" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

# 1.1 Basic System Info
section "1. SYSTEM OVERVIEW"

subsection "1.1 OS Details"
{
    echo "=== Operating System ==="
    if command -v uname &> /dev/null; then
        uname -a
    fi
    echo ""
    if [ -f /etc/os-release ]; then
        cat /etc/os-release
    elif [ -f /etc/lsb-release ]; then
        cat /etc/lsb-release
    fi
    echo ""
    echo "=== System Uptime ==="
    uptime -p 2>/dev/null || uptime
    echo ""
    echo "=== Current User & Shell ==="
    echo "User: $(whoami)"
    echo "Shell: $SHELL"
    echo "Home: $HOME"
} >> "$REPORT_FILE"

# 1.2 Kernel & Hardware
subsection "1.2 Kernel & Module Information"
{
    echo "=== Kernel Version ==="
    uname -r
    echo ""
    echo "=== Loaded Kernel Modules (top 30) ==="
    if command -v lsmod &> /dev/null; then
        lsmod | head -35
    fi
} >> "$REPORT_FILE"

subsection "1.3 CPU Information"
{
    echo "=== CPU Details ==="
    if [ -f /proc/cpuinfo ]; then
        grep -E "model name|processor|cpu MHz|cache size|cpu cores|flags|bogomips" /proc/cpuinfo | head -30
    elif command -v sysctl &> /dev/null; then
        sysctl -n machdep.cpu.brand_string 2>/dev/null || sysctl -n hw.model
    fi
    echo ""
    echo "=== CPU Usage (live) ==="
    top -bn1 | head -15
} >> "$REPORT_FILE"

subsection "1.4 Memory Information"
{
    echo "=== Memory Details ==="
    if [ -f /proc/meminfo ]; then
        cat /proc/meminfo
    elif command -v vm_stat &> /dev/null; then
        vm_stat
    fi
    echo ""
    echo "=== Memory Usage ==="
    free -h
    echo ""
    echo "=== Top Memory Consumers ==="
    ps aux --sort=-%mem | head -10
} >> "$REPORT_FILE"

# ============================================
# 2. WINDOWS-SPECIFIC (via WSL) - Skip in quick mode
# ============================================
if [ "$QUICK_MODE" = "1" ]; then
    # Quick mode: skip Windows section entirely (slow due to WSL filesystem)
    log_info "Skipping Windows section (quick mode)"
else
section "2. WINDOWS ENVIRONMENT (WSL)"

subsection "2.1 Windows Version"
{
    if [ -f /proc/version ]; then
        grep -i microsoft /proc/version
    fi
    echo ""
    echo "=== Windows Mounts ==="
    mount | grep -E "^C:|^/mnt/c|/mnt/c/Users" | head -20
} >> "$REPORT_FILE"

subsection "2.2 Windows System Info"
{
    echo "=== WSL Version ==="
    wsl.exe -l -v 2>/dev/null || echo "WSL command not available"
    echo ""
    echo "=== Windows Users Directory ==="
    ls -la /mnt/c/Users/ 2>/dev/null | head -20
} >> "$REPORT_FILE"

subsection "2.3 Windows Installed Programs"
{
    echo "=== Program Files (64-bit) ==="
    timeout_cmd $TIMEOUT_SMALL ls /mnt/c/Program\ Files/ 2>/dev/null | head -15
    echo ""
    echo "=== Program Files (32-bit) ==="
    timeout_cmd $TIMEOUT_SMALL ls /mnt/c/Program\ Files\ \(x86\)/ 2>/dev/null | head -15
} >> "$REPORT_FILE"
fi  # End of quick mode skip for Windows section

# ============================================
# 3. STORAGE & DISK
# ============================================
section "3. STORAGE & DISK"

subsection "3.1 Disk Usage"
df -h 2>/dev/null | grep -v "tmpfs\|devtmpfs\|loop" >> "$REPORT_FILE"

subsection "3.2 Inode Usage"
df -i 2>/dev/null | grep -v "tmpfs\|devtmpfs\|loop" >> "$REPORT_FILE"

subsection "3.3 Disk Partitions"
{
    echo "=== Block Devices ==="
    lsblk -o NAME,TYPE,SIZE,MOUNTPOINT,FSTYPE 2>/dev/null
    echo ""
    echo "=== Mount Points ==="
    mount | grep -v "proc\|sys\|dev\|run" | head -30
} >> "$REPORT_FILE"

subsection "3.4 Disk I/O Stats"
if command -v iostat &> /dev/null; then
    iostat -x 1 1 2>/dev/null | tail -20 >> "$REPORT_FILE"
fi

subsection "3.5 SMART Health (if available)"
if command -v smartctl &> /dev/null; then
    for disk in /dev/sd? /dev/nvme?; do
        [ -b "$disk" ] && smartctl -H "$disk" 2>/dev/null >> "$REPORT_FILE"
    done
fi

# ============================================
# 4. NETWORK
# ============================================
section "4. NETWORK"

subsection "4.1 Network Interfaces"
ip addr show 2>/dev/null >> "$REPORT_FILE" || ifconfig -a 2>/dev/null >> "$REPORT_FILE"

subsection "4.2 Routing Table"
ip route show 2>/dev/null >> "$REPORT_FILE" || netstat -rn 2>/dev/null >> "$REPORT_FILE"

subsection "4.3 DNS Configuration"
{
    echo "=== /etc/resolv.conf ==="
    cat /etc/resolv.conf 2>/dev/null
    echo ""
    echo "=== DNS Resolvers ==="
    if command -v resolvectl &> /dev/null; then
        resolvectl status 2>/dev/null | head -30
    fi
} >> "$REPORT_FILE"

subsection "4.4 Listening Ports (TCP)"
{
    echo "=== Listening TCP Ports ==="
    if command -v ss &> /dev/null; then
        ss -tlnp 2>/dev/null
    else
        netstat -tlnp 2>/dev/null
    fi
} >> "$REPORT_FILE"

subsection "4.5 Listening Ports (UDP)"
{
    echo "=== Listening UDP Ports ==="
    if command -v ss &> /dev/null; then
        ss -ulnp 2>/dev/null
    else
        netstat -ulnp 2>/dev/null
    fi
} >> "$REPORT_FILE"

subsection "4.6 Active Connections"
{
    echo "=== Established Connections ==="
    if command -v ss &> /dev/null; then
        ss -tn | grep ESTAB | head -30
    else
        netstat -tn | grep ESTAB | head -30
    fi
} >> "$REPORT_FILE"

subsection "4.7 Firewall Status"
{
    echo "=== iptables (summary) ==="
    if command -v iptables &> /dev/null; then
        iptables -L -n -v 2>/dev/null | head -30
    fi
    echo ""
    echo "=== ufw Status ==="
    if command -v ufw &> /dev/null; then
        ufw status verbose 2>/dev/null
    fi
} >> "$REPORT_FILE"

# ============================================
# 5. PROCESSES & SERVICES
# ============================================
section "5. PROCESSES & SERVICES"

subsection "5.1 Top CPU Processes"
ps aux --sort=-%cpu | head -15 >> "$REPORT_FILE"

subsection "5.2 Top Memory Processes"
ps aux --sort=-%mem | head -15 >> "$REPORT_FILE"

subsection "5.3 Zombie Processes"
ps aux | awk '$8 ~ /Z/ {print}' >> "$REPORT_FILE" || echo "No zombie processes found" >> "$REPORT_FILE"

subsection "5.4 Running Services"
{
    echo "=== Running System Services ==="
    if command -v systemctl &> /dev/null; then
        systemctl --type=running --no-pager 2>/dev/null | head -40
    fi
} >> "$REPORT_FILE"

subsection "5.5 Failed Services"
{
    echo "=== Failed Services ==="
    if command -v systemctl &> /dev/null; then
        systemctl --failed --no-pager 2>/dev/null
    fi
} >> "$REPORT_FILE"

# ============================================
# 6. USERS & SECURITY
# ============================================
section "6. USERS & SECURITY"

subsection "6.1 Logged In Users"
who -a 2>/dev/null >> "$REPORT_FILE"

subsection "6.2 Last Logins"
last -20 2>/dev/null >> "$REPORT_FILE"

subsection "6.3 User Accounts"
{
    echo "=== System Users ==="
    getent passwd | grep -v "/nologin\|/false" | head -20
    echo ""
    echo "=== User Groups ==="
    getent group | head -20
} >> "$REPORT_FILE"

subsection "6.4 SSH Keys & Access"
{
    echo "=== SSH Authorized Keys ==="
    if [ -d ~/.ssh ]; then
        for keyfile in ~/.ssh/authorized_keys ~/.ssh/authorized_keys2; do
            [ -f "$keyfile" ] && echo "$keyfile:" && cat "$keyfile" | head -5
        done
    fi
    echo ""
    echo "=== SSH Known Hosts ==="
    if [ -f ~/.ssh/known_hosts ]; then
        head -10 ~/.ssh/known_hosts
    fi
} >> "$REPORT_FILE"

subsection "6.5 Failed Login Attempts"
{
    echo "=== Recent Failed Logins ==="
    if [ -f /var/log/auth.log ]; then
        grep -i "failed\|invalid" /var/log/auth.log 2>/dev/null | tail -20
    fi
} >> "$REPORT_FILE"

# ============================================
# 7. PACKAGES & SOFTWARE
# ============================================
section "7. PACKAGES & SOFTWARE"

subsection "7.1 Package Manager (apt/dpkg)"
{
    echo "=== Recently Installed Packages ==="
    if command -v dpkg &> /dev/null; then
        dpkg -l | grep "^ii" | tail -30
    fi
} >> "$REPORT_FILE"

subsection "7.2 Snap Packages"
if command -v snap &> /dev/null; then
    echo "=== Snap Packages ==="
    snap list >> "$REPORT_FILE"
fi

subsection "7.3 Python Packages"
{
    echo "=== Python Versions ==="
    python3 --version 2>/dev/null
    python --version 2>/dev/null
    echo ""
    echo "=== pip Packages (user) ==="
    pip3 list 2>/dev/null | head -20
} >> "$REPORT_FILE"

subsection "7.4 Node.js & npm"
{
    echo "=== Node.js Version ==="
    node --version 2>/dev/null
    echo ""
    echo "=== npm Global Packages ==="
    npm list -g --depth=0 2>/dev/null | head -20
} >> "$REPORT_FILE"

subsection "7.5 Ruby & Gems"
{
    echo "=== Ruby Version ==="
    ruby --version 2>/dev/null
    echo ""
    echo "=== Gem List ==="
    gem list 2>/dev/null | head -20
} >> "$REPORT_FILE"

subsection "7.6 Cargo (Rust)"
{
    echo "=== Rust/Cargo ==="
    cargo --version 2>/dev/null
    echo ""
    echo "=== Cargo Binaries ==="
    ls ~/.cargo/bin 2>/dev/null | head -20
} >> "$REPORT_FILE"

# ============================================
# 8. ENVIRONMENT & PATHS
# ============================================
section "8. ENVIRONMENT & CONFIG"

subsection "8.1 Environment Variables"
{
    echo "=== Key Environment Variables ==="
    echo "PATH: $PATH" | head -5
    echo ""
    echo "=== All Environment Variables ==="
    env | sort | head -40
} >> "$REPORT_FILE"

subsection "8.2 Shell Configuration"
{
    echo "=== Shell History (last 20) ==="
    if [ -f ~/.bash_history ]; then
        tail -20 ~/.bash_history
    fi
    echo ""
    echo "=== Aliases ==="
    alias 2>/dev/null | head -20
} >> "$REPORT_FILE"

# ============================================
# 9. CONTAINERS & VIRTUALIZATION
# ============================================
section "9. CONTAINERS & VIRTUALIZATION"

subsection "9.1 Docker"
if command -v docker &> /dev/null; then
    echo "=== Docker Version ===" >> "$REPORT_FILE"
    timeout_cmd $TIMEOUT_SMALL docker --version 2>/dev/null >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "=== Docker Containers ===" >> "$REPORT_FILE"
    timeout_cmd $TIMEOUT_SMALL docker ps -a 2>/dev/null >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "=== Docker Images ===" >> "$REPORT_FILE"
    timeout_cmd $TIMEOUT_SMALL docker images 2>/dev/null >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "=== Docker System Info ===" >> "$REPORT_FILE"
    timeout_cmd $TIMEOUT_SMALL docker system df 2>/dev/null >> "$REPORT_FILE"
fi

subsection "9.2 Podman"
if command -v podman &> /dev/null; then
    echo "=== Podman Containers ==="
    podman ps -a 2>/dev/null >> "$REPORT_FILE"
fi

subsection "9.3 Virtual Machines"
if command -v virsh &> /dev/null; then
    echo "=== Libvirt VMs ==="
    virsh list --all 2>/dev/null >> "$REPORT_FILE"
fi

# ============================================
# 10. HARDWARE INFO
# ============================================
section "10. HARDWARE"

subsection "10.1 GPU Information"
{
    echo "=== lspci GPU ==="
    lspci 2>/dev/null | grep -i "vga\|graphics\|display" | head -10
    echo ""
    echo "=== nvidia-smi (if available) ==="
    nvidia-smi 2>/dev/null | head -30
} >> "$REPORT_FILE"

subsection "10.2 USB Devices"
{
    echo "=== USB Devices ==="
    lsusb 2>/dev/null | head -20
} >> "$REPORT_FILE"

subsection "10.3 PCI Devices"
{
    echo "=== PCI Devices (summary) ==="
    lspci 2>/dev/null | head -30
} >> "$REPORT_FILE"

subsection "10.4 Temperature & Power"
{
    echo "=== Thermal Zones ==="
    if [ -d /sys/class/thermal ]; then
        for zone in /sys/class/thermal/thermal_zone*; do
            [ -f "$zone/temp" ] && echo "$zone: $(cat $zone/temp 2>/dev/null | cut -c1,2).$(( $(cat $zone/temp 2>/dev/null | cut -c3) * 10 ))°C"
        done
    fi
    echo ""
    echo "=== sensors output ==="
    sensors 2>/dev/null | head -20
} >> "$REPORT_FILE"

subsection "10.5 Battery Status (if laptop)"
if command -v upower &> /dev/null; then
    upower -i /org/freedesktop/UPower/devices/battery_BAT0 2>/dev/null >> "$REPORT_FILE"
fi

# ============================================
# 11. FILESYSTEM & LOGS
# ============================================
section "11. FILESYSTEM & LOGS"

subsection "11.1 Large Directories"
{
    echo "=== Top Disk Consumers in /home (limited) ==="
    timeout_cmd $TIMEOUT_MEDIUM du -sh ~/* 2>/dev/null | sort -rh | head -10
} >> "$REPORT_FILE"

subsection "11.2 System Logs"
{
    echo "=== Recent System Errors ==="
    # Use journalctl if available (faster than reading logs directly)
    if command -v journalctl &> /dev/null; then
        timeout_cmd $TIMEOUT_SMALL journalctl -p err --no-pager -n 20 2>/dev/null
    elif [ -f /var/log/syslog ]; then
        timeout_cmd $TIMEOUT_SMALL grep -i "error\|fail\|critical" /var/log/syslog 2>/dev/null | tail -20
    fi
    echo ""
    echo "=== Kernel Ring Buffer (dmesg) ==="
    timeout_cmd $TIMEOUT_SMALL dmesg 2>/dev/null | tail -20
} >> "$REPORT_FILE"

# ============================================
# 12. CRON & SCHEDULED TASKS
# ============================================
section "12. CRON & SCHEDULED TASKS"

subsection "12.1 User Crontab"
crontab -l 2>/dev/null >> "$REPORT_FILE" || echo "No user crontabs" >> "$REPORT_FILE"

subsection "12.2 System Cron"
{
    echo "=== /etc/crontab ==="
    cat /etc/crontab 2>/dev/null
    echo ""
    echo "=== Cron.d files ==="
    ls -la /etc/cron.d/ 2>/dev/null
} >> "$REPORT_FILE"

subsection "12.3 Anacron"
if [ -f /etc/anacrontab ]; then
    echo "=== /etc/anacrontab ==="
    cat /etc/anacrontab >> "$REPORT_FILE"
fi

# ============================================
# 13. OPENCLAW STATUS
# ============================================
section "13. OPENCLAW STATUS"

subsection "13.1 OpenClaw Version & Status"
{
    echo "=== OpenClaw Version ==="
    openclaw --version 2>/dev/null
    echo ""
    echo "=== OpenClaw Status ==="
    openclaw status 2>/dev/null
    echo ""
    echo "=== OpenClaw Skills ==="
    openclaw skills list 2>/dev/null | head -20
} >> "$REPORT_FILE"

# ============================================
# 14. BROWSER INFO (if accessible)
# ============================================
section "14. BROWSER INFORMATION"

subsection "14.1 Installed Browsers"
{
    echo "=== Browser Binaries ==="
    which firefox chrome chromium google-chrome microsoft-edge edge 2>/dev/null
    echo ""
    echo "=== Browser Versions (if available) ==="
    firefox --version 2>/dev/null
    google-chrome --version 2>/dev/null
    chromium --version 2>/dev/null
} >> "$REPORT_FILE"

# ============================================
# SUMMARY & RECOMMENDATIONS
# ============================================
section "SUMMARY & RECOMMENDATIONS"

{
    echo "=== Quick Health Score ==="
    echo ""
    
    # Calculate health score
    SCORE=100
    WARNINGS=0
    
    echo "📊 System Metrics:"
    echo ""
    
    # Disk check
    DISK_FULL=$(df -h 2>/dev/null | grep -v "tmpfs\|devtmpfs\|loop" | awk -F'[\t %]+' '{if($5+0 > 80) print $6":"$5}')
    if [ -n "$DISK_FULL" ]; then
        echo "  ⚠️  High disk usage: $DISK_FULL"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  ✅ Disk usage: OK"
    fi
    
    # Memory check
    MEM_PCT=$(free | awk '/^Mem:/{print int($3/$2*100)}')
    if [ "$MEM_PCT" -gt 80 ]; then
        echo "  ⚠️  High memory usage: ${MEM_PCT}%"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  ✅ Memory usage: ${MEM_PCT}% (OK)"
    fi
    
    # Failed services
    FAILED=$(systemctl --failed --no-pager 2>/dev/null | grep -c "●" 2>/dev/null || echo 0)
    FAILED=${FAILED:-0}
    if [ "$FAILED" -gt 0 ] 2>/dev/null; then
        echo "  ⚠️  Failed services: $FAILED"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  ✅ No failed services"
    fi
    
    # Failed logins
    FAILED_LOGINS=$(grep -c "Failed password" /var/log/auth.log 2>/dev/null | tail -1 | grep -oE '[0-9]+' || echo 0)
    FAILED_LOGINS=${FAILED_LOGINS:-0}
    if [ "$FAILED_LOGINS" -gt 10 ] 2>/dev/null; then
        echo "  ⚠️  Failed login attempts: $FAILED_LOGINS (high)"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  ✅ Login attempts: OK"
    fi
    
    echo ""
    echo "Overall Health: $((100 - WARNINGS * 15))%"
    echo ""
    
    echo "=== Recommendations ==="
    echo ""
    
    # Storage recommendations
    if df -h /mnt/c 2>/dev/null | awk 'NR==2 {print $5}' | tr -d '%' | grep -qE '[8-9][0-9]|100'; then
        echo "💾 STORAGE (Windows C: drive is running low):"
        echo "   • Empty Recycle Bin (right-click → Empty Recycle Bin)"
        echo "   • Clear Downloads folder: %USERPROFILE%\\Downloads"
        echo "   • Delete temp files: Type 'temp' in File Explorer → Select all → Delete"
        echo "   • Run Disk Cleanup: Right-click C: → Properties → Disk Cleanup"
        echo "   • Press Win+R → type 'cleanmgr' → select C: drive"
        echo "   • In Docker Desktop: Settings → Resources → Disk → Clean up"
        echo ""
    fi
    
    # WSL/Docker recommendations
    if df -h /usr/lib/wsl/drivers 2>/dev/null | awk 'NR==2 {print $5}' | tr -d '%' | grep -qE '[8-9][0-9]|100'; then
        echo "🐳 WSL/DOCKER (Disk space running low):"
        echo "   • Run: docker system prune -a"
        echo "   • Run: docker volume prune"
        echo "   • Run: wsl --shutdown (then restart WSL)"
        echo "   • In Docker Desktop: Settings → Resources → Disk → Clean up"
        echo ""
    fi
    
    # Memory recommendations
    MEM_PCT=$(free | awk '/^Mem:/{print int($3/$2*100)}')
    if [ "$MEM_PCT" -gt 80 ]; then
        echo "🧠 MEMORY (High memory usage):"
        echo "   • Close unused browser tabs"
        echo "   • Close heavy applications (Chrome, VS Code, etc.)"
        echo "   • Restart your computer"
        echo ""
    fi
    
    # General recommendations
    echo "📝 GENERAL MAINTENANCE:"
    echo "   • Run periodic healthchecks to track changes"
    echo "   • Keep system packages updated (run: sudo apt update)"
    echo "   • Monitor disk space trends"
    echo "   • Review security logs regularly"
} >> "$REPORT_FILE"

# Create JSON summary
{
    echo "{"
    echo "  \"timestamp\": \"$(date -Iseconds)\","
    echo "  \"hostname\": \"$(hostname)\","
    echo "  \"os\": \"$(uname -s)\","
    echo "  \"kernel\": \"$(uname -r)\","
    echo "  \"uptime\": \"$(uptime -p 2>/dev/null || uptime)\","
    
    # Memory
    echo "  \"memory_total_gb\": $(free -g 2>/dev/null | awk '/^Mem:/{print $2}'),"
    echo "  \"memory_used_gb\": $(free -g 2>/dev/null | awk '/^Mem:/{print $3}'),"
    echo "  \"memory_percent\": $(free | awk '/^Mem:/{print int($3/$2*100)}'),"
    
    # CPU
    echo "  \"cpu_cores\": $(nproc),"
    echo "  \"cpu_model\": \"$(grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2 | xargs)\","
    
    # Disk
    echo "  \"disk_usage\": ["
    df -h 2>/dev/null | grep -v "tmpfs\|devtmpfs\|loop" | awk -F'[\t %]+' '{if(NR>1 && $5+0 > 0) printf "    {\"mount\": \"%s\", \"used\": \"%s\", \"percent\": %d},\n", $6, $5, $5+0}' | sed 's/,$//'
    echo "  ],"
    
    # Failed services
    echo "  \"failed_services\": $(systemctl --failed --no-pager 2>/dev/null | grep -c "●" 2>/dev/null || echo 0),"
    
    # Network
    echo "  \"listening_ports_tcp\": $(ss -tln 2>/dev/null | wc -l),"
    echo "  \"listening_ports_udp\": $(ss -uln 2>/dev/null | wc -l),"
    
    # OpenClaw
    echo "  \"openclaw_running\": $(pgrep -f openclaw-gateway >/dev/null && echo "true" || echo "false"),"
    
    echo "  \"report_file\": \"$REPORT_FILE\""
    echo "}"
} > "$JSON_FILE"

log_success "Enhanced Healthcheck complete!"
log_info "Report saved to: $REPORT_FILE"
log_info "JSON summary: $JSON_FILE"

# Display summary
echo ""
log_info "=== Quick Summary ==="
echo ""
df -h 2>/dev/null | grep -v "tmpfs\|devtmpfs\|loop" | awk '{if($5 ~ /^[0-9]+/ && $5+0 > 80) print "⚠️  WARNING: "$1" is "$5" full"}'
free -h 2>/dev/null | awk '/Mem:/ {if($3/$2 > 0.8) print "⚠️  WARNING: Memory usage above 80%"}'

if command -v systemctl &> /dev/null; then
    FAILED=$(systemctl --failed --no-pager 2>/dev/null | grep -c "●" 2>/dev/null || echo 0)
    FAILED=${FAILED:-0}
    if [ "$FAILED" -gt 0 ] 2>/dev/null; then
        echo "⚠️  WARNING: $FAILED failed services"
    fi
fi

echo ""
log_success "Done!"

# Output file paths
echo "$REPORT_FILE"
echo "$JSON_FILE"