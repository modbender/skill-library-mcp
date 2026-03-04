#!/bin/bash
# Runtime security checks - cross-platform
# Outputs JSON with success/failure indicators for each check
# Agent can fallback to environment-specific commands if checks fail

set -o pipefail

#############################################
# OS Detection
#############################################

OS="unknown"
OS_VARIANT=""
IN_WSL="false"
IN_DSM="false"

case "$(uname -s)" in
    Linux*)
        OS="linux"
        # Detect WSL
        if grep -qi microsoft /proc/version 2>/dev/null; then
            IN_WSL="true"
            OS_VARIANT="wsl"
        # Detect Synology DSM
        elif [ -f /etc/synoinfo.conf ]; then
            IN_DSM="true"
            OS_VARIANT="dsm"
        # Detect distro
        elif [ -f /etc/os-release ]; then
            OS_VARIANT=$(grep "^ID=" /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"')
        fi
        ;;
    Darwin*)
        OS="macos"
        OS_VARIANT=$(sw_vers -productVersion 2>/dev/null || echo "unknown")
        ;;
    CYGWIN*|MINGW*|MSYS*)
        OS="windows"
        OS_VARIANT="cygwin"
        ;;
    *)
        # Could be Windows native or unknown
        if [ -n "$WINDIR" ] || [ -n "$SystemRoot" ]; then
            OS="windows"
            OS_VARIANT="native"
        fi
        ;;
esac

# Track failed checks for agent fallback
declare -a failed_checks

echo "{"
echo '  "os": "'"$OS"'",'
echo '  "os_variant": "'"$OS_VARIANT"'",'
echo '  "in_wsl": '"$IN_WSL"','
echo '  "in_dsm": '"$IN_DSM"','

#############################################
# 1. Network Exposure Check
#############################################

echo '  "network": {'

# Get external IP (cross-platform)
external_ip=$(curl -s --max-time 5 https://ifconfig.me 2>/dev/null || curl -s --max-time 5 https://api.ipify.org 2>/dev/null || echo "")
if [ -z "$external_ip" ]; then
    external_ip="unknown"
    failed_checks+=("external_ip")
fi
echo '    "external_ip": "'"$external_ip"'",'

# Get local IPs (OS-specific)
local_ips=""
if [ "$OS" = "macos" ]; then
    local_ips=$(ifconfig 2>/dev/null | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | tr '\n' ',' | sed 's/,$//')
elif [ "$OS" = "linux" ]; then
    local_ips=$(hostname -I 2>/dev/null | tr ' ' ',' | sed 's/,$//')
    if [ -z "$local_ips" ]; then
        # Fallback for minimal systems
        local_ips=$(ip -4 addr show 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1 | tr '\n' ',' | sed 's/,$//')
    fi
fi
if [ -z "$local_ips" ]; then
    local_ips="unknown"
    failed_checks+=("local_ips")
fi
echo '    "local_ips": "'"$local_ips"'",'

# Gateway port and binding
gateway_port=$(grep -oE '"port":\s*[0-9]+' ~/.openclaw/openclaw.json 2>/dev/null | grep -oE '[0-9]+' | head -1)
[ -z "$gateway_port" ] && gateway_port="18789"

# Check gateway binding (OS-specific)
gateway_bind=""
if [ "$OS" = "macos" ]; then
    gateway_bind=$(lsof -iTCP:"$gateway_port" -sTCP:LISTEN -n -P 2>/dev/null | tail -1 | awk '{print $9}')
elif [ "$OS" = "linux" ]; then
    gateway_bind=$(ss -tlnp 2>/dev/null | grep ":$gateway_port " | awk '{print $4}')
    if [ -z "$gateway_bind" ]; then
        # Fallback to netstat
        gateway_bind=$(netstat -tlnp 2>/dev/null | grep ":$gateway_port " | awk '{print $4}')
    fi
fi
if [ -z "$gateway_bind" ]; then
    gateway_bind="unknown"
    failed_checks+=("gateway_bind")
fi

exposed="false"
if echo "$gateway_bind" | grep -qE "^\*:|^0\.0\.0\.0:|^\[::\]:"; then
    exposed="true"
fi
echo '    "gateway_port": '"$gateway_port"','
echo '    "gateway_bind": "'"$gateway_bind"'",'
echo '    "potentially_exposed": '"$exposed"','

# NAT detection
nat_detected="true"
if [ "$local_ips" != "unknown" ] && [ "$external_ip" != "unknown" ]; then
    for ip in $(echo "$local_ips" | tr ',' ' '); do
        if [ "$ip" = "$external_ip" ]; then
            nat_detected="false"
            break
        fi
    done
fi
echo '    "behind_nat": '"$nat_detected"','

# VPN detection (cross-platform)
vpn_type="none"
if [ "$OS" = "macos" ]; then
    if ifconfig 2>/dev/null | grep -q "utun"; then
        if command -v tailscale &>/dev/null && tailscale status &>/dev/null 2>&1; then
            vpn_type="tailscale"
        else
            vpn_type="vpn"
        fi
    fi
elif [ "$OS" = "linux" ]; then
    if ip link 2>/dev/null | grep -qE "wg[0-9]"; then
        vpn_type="wireguard"
    elif ip link 2>/dev/null | grep -q "tailscale"; then
        vpn_type="tailscale"
    elif command -v tailscale &>/dev/null && tailscale status &>/dev/null 2>&1; then
        vpn_type="tailscale"
    elif ip link 2>/dev/null | grep -qE "tun[0-9]"; then
        vpn_type="openvpn"
    fi
fi
echo '    "vpn_type": "'"$vpn_type"'"'

echo '  },'

#############################################
# 2. Container/Isolation Detection
#############################################

echo '  "isolation": {'

in_container="false"
container_type="none"

if [ "$OS" = "linux" ]; then
    if [ -f /.dockerenv ]; then
        in_container="true"
        container_type="docker"
    elif grep -qE "docker|lxc|kubepods|containerd" /proc/1/cgroup 2>/dev/null; then
        in_container="true"
        container_type="container"
    elif [ -f /run/.containerenv ]; then
        in_container="true"
        container_type="podman"
    fi
elif [ "$OS" = "macos" ]; then
    # macOS: check for Lima/Colima/Orbstack
    if [ -f /.dockerenv ] || [ -n "$LIMA_INSTANCE" ]; then
        in_container="true"
        container_type="lima"
    fi
fi

echo '    "in_container": '"$in_container"','
echo '    "container_type": "'"$container_type"'"'

echo '  },'

#############################################
# 3. Process Privileges
#############################################

echo '  "privileges": {'

current_user=$(whoami 2>/dev/null || echo "unknown")
echo '    "current_user": "'"$current_user"'",'

is_root="false"
if [ "$(id -u 2>/dev/null)" = "0" ]; then
    is_root="true"
fi
echo '    "running_as_root": '"$is_root"','

# Sudo check (cross-platform)
can_sudo="false"
if command -v sudo &>/dev/null; then
    if groups 2>/dev/null | grep -qE "sudo|wheel|admin"; then
        can_sudo="true"
    fi
    # Check if we can actually sudo without password
    if sudo -n true 2>/dev/null; then
        can_sudo="true"
    fi
fi
echo '    "can_sudo": '"$can_sudo"','

# OpenClaw process
openclaw_pid=$(pgrep -f "openclaw" 2>/dev/null | head -1)
if [ -n "$openclaw_pid" ]; then
    openclaw_user=$(ps -o user= -p "$openclaw_pid" 2>/dev/null | tr -d ' ')
    echo '    "openclaw_pid": '"$openclaw_pid"','
    echo '    "openclaw_user": "'"${openclaw_user:-unknown}"'"'
else
    echo '    "openclaw_pid": null,'
    echo '    "openclaw_user": null'
fi

echo '  },'

#############################################
# 4. File System Security
#############################################

echo '  "filesystem": {'

openclaw_dir="$HOME/.openclaw"
if [ -d "$openclaw_dir" ]; then
    # Get permissions (cross-platform)
    if [ "$OS" = "macos" ]; then
        dir_perms=$(stat -f %Lp "$openclaw_dir" 2>/dev/null || echo "unknown")
        config_perms=$(stat -f %Lp "$openclaw_dir/openclaw.json" 2>/dev/null || echo "missing")
        creds_perms=$(stat -f %Lp "$openclaw_dir/credentials" 2>/dev/null || echo "missing")
    else
        dir_perms=$(stat -c %a "$openclaw_dir" 2>/dev/null || echo "unknown")
        config_perms=$(stat -c %a "$openclaw_dir/openclaw.json" 2>/dev/null || echo "missing")
        creds_perms=$(stat -c %a "$openclaw_dir/credentials" 2>/dev/null || echo "missing")
    fi
    echo '    "openclaw_dir_perms": "'"$dir_perms"'",'
    echo '    "config_perms": "'"$config_perms"'",'
    echo '    "credentials_dir_perms": "'"$creds_perms"'"'
else
    echo '    "openclaw_dir_perms": "missing",'
    echo '    "config_perms": "missing",'
    echo '    "credentials_dir_perms": "missing"'
fi

echo '  },'

#############################################
# 5. Failed Checks (for agent fallback)
#############################################

echo '  "failed_checks": ['
first=true
for check in "${failed_checks[@]}"; do
    [ "$first" = true ] && first=false || echo -n ","
    echo -n '"'"$check"'"'
done
echo ''
echo '  ]'

echo "}"
