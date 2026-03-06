#!/usr/bin/env bash
# OpenClaw Security Audit
# Usage: security_audit.sh [--json] [--check docker|ssh|config|files|network]

set -uo pipefail

JSON_OUTPUT=false
CHECK_FILTER=""
SCORE=100
ISSUES=()
WARNINGS=()
PASSES=()

for arg in "$@"; do
    case "$arg" in
        --json) JSON_OUTPUT=true ;;
        --check) CHECK_FILTER="next" ;;
        --help|-h)
            echo "Usage: security_audit.sh [--json] [--check docker|ssh|config|files|network]"
            exit 0
            ;;
        *)
            if [ "$CHECK_FILTER" = "next" ]; then
                CHECK_FILTER="$arg"
            fi
            ;;
    esac
done

log() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo "$@"
    fi
}

pass() {
    local category="$1" msg="$2"
    PASSES+=("[$category] ✅ $msg")
    log "[$category] ✅ $msg"
}

warn() {
    local category="$1" msg="$2" deduct="${3:-5}"
    WARNINGS+=("[$category] ⚠️  $msg")
    SCORE=$((SCORE - deduct))
    log "[$category] ⚠️  $msg (-$deduct)"
}

fail() {
    local category="$1" msg="$2" deduct="${3:-10}"
    ISSUES+=("[$category] ❌ $msg")
    SCORE=$((SCORE - deduct))
    log "[$category] ❌ $msg (-$deduct)"
}

should_check() {
    [ -z "$CHECK_FILTER" ] || [ "$CHECK_FILTER" = "$1" ]
}

# ─── CONFIG CHECKS ───
check_config() {
    log ""
    log "── OpenClaw Config ──"

    # Find config file
    local config=""
    for path in /root/.openclaw/openclaw.json /home/node/.openclaw/openclaw.json ~/.openclaw/openclaw.json; do
        if [ -f "$path" ]; then
            config="$path"
            break
        fi
    done

    if [ -z "$config" ]; then
        warn "CONFIG" "openclaw.json not found — cannot audit config" 15
        return
    fi

    # allowInsecureAuth
    if grep -q '"allowInsecureAuth"[[:space:]]*:[[:space:]]*true' "$config" 2>/dev/null; then
        fail "CONFIG" "allowInsecureAuth is TRUE — critical security risk" 20
    else
        pass "CONFIG" "allowInsecureAuth: false"
    fi

    # dmPolicy
    if grep -q '"dmPolicy"[[:space:]]*:[[:space:]]*"open"' "$config" 2>/dev/null; then
        fail "CONFIG" "dmPolicy is 'open' — anyone can DM your agent" 15
    elif grep -q '"dmPolicy"[[:space:]]*:[[:space:]]*"allowlist"' "$config" 2>/dev/null; then
        pass "CONFIG" "dmPolicy: allowlist"
    else
        local policy=$(python3 -c "import json; d=json.load(open('$config')); print(d.get('dmPolicy','unknown'))" 2>/dev/null || echo "unknown")
        if [ "$policy" = "unknown" ]; then
            warn "CONFIG" "dmPolicy not set — defaults may be insecure" 5
        else
            pass "CONFIG" "dmPolicy: $policy"
        fi
    fi

    # Check for 0.0.0.0 bindings in config
    if grep -q '0\.0\.0\.0' "$config" 2>/dev/null; then
        fail "CONFIG" "Config contains 0.0.0.0 binding — should be 127.0.0.1" 10
    else
        pass "CONFIG" "No 0.0.0.0 bindings in config"
    fi

    # Check for hardcoded API keys
    if grep -qiE '(api[_-]?key|secret|token)[[:space:]]*:[[:space:]]*"[a-zA-Z0-9]{20,}"' "$config" 2>/dev/null; then
        warn "CONFIG" "Possible hardcoded API keys in config — use env vars" 5
    else
        pass "CONFIG" "No hardcoded API keys detected"
    fi
}

# ─── DOCKER CHECKS ───
check_docker() {
    log ""
    log "── Docker Security ──"

    if ! command -v docker &>/dev/null; then
        warn "DOCKER" "Docker not available — skipping checks" 10
        return
    fi

    # Check port bindings
    local bad_ports=false
    while IFS= read -r line; do
        if echo "$line" | grep -q '0\.0\.0\.0:'; then
            local container=$(echo "$line" | awk '{print $NF}')
            local port=$(echo "$line" | grep -oP '0\.0\.0\.0:\d+' | head -1)
            fail "DOCKER" "Container '$container' exposes $port to all interfaces" 10
            bad_ports=true
        fi
    done < <(docker ps --format '{{.Ports}} {{.Names}}' 2>/dev/null || true)

    if [ "$bad_ports" = false ]; then
        pass "DOCKER" "All container ports bound to 127.0.0.1"
    fi

    # Check privileged containers
    while IFS= read -r container; do
        local priv=$(docker inspect --format '{{.HostConfig.Privileged}}' "$container" 2>/dev/null || echo "false")
        if [ "$priv" = "true" ]; then
            fail "DOCKER" "Container '$container' runs privileged" 10
        fi
    done < <(docker ps -q 2>/dev/null || true)

    # Check resource limits
    while IFS= read -r container; do
        local name=$(docker inspect --format '{{.Name}}' "$container" 2>/dev/null | sed 's/\///')
        local mem=$(docker inspect --format '{{.HostConfig.Memory}}' "$container" 2>/dev/null || echo "0")
        if [ "$mem" = "0" ]; then
            warn "DOCKER" "Container '$name' has no memory limit" 3
        fi
    done < <(docker ps -q 2>/dev/null || true)

    # Docker socket permissions
    if [ -S /var/run/docker.sock ]; then
        local sock_perms=$(stat -c '%a' /var/run/docker.sock 2>/dev/null || echo "unknown")
        if [ "$sock_perms" = "666" ]; then
            warn "DOCKER" "Docker socket is world-writable (666)" 5
        else
            pass "DOCKER" "Docker socket permissions: $sock_perms"
        fi
    fi
}

# ─── SSH CHECKS ───
check_ssh() {
    log ""
    log "── SSH Configuration ──"

    local sshd_config="/etc/ssh/sshd_config"
    if [ ! -f "$sshd_config" ]; then
        # Try to find it
        sshd_config=$(find /etc/ssh -name 'sshd_config' 2>/dev/null | head -1)
    fi

    if [ -z "$sshd_config" ] || [ ! -f "$sshd_config" ]; then
        log "[SSH] ℹ️  sshd_config not found (may be running in container)"
        return
    fi

    # Root login
    if grep -qiE '^[[:space:]]*PermitRootLogin[[:space:]]+(yes|without-password)' "$sshd_config" 2>/dev/null; then
        fail "SSH" "Root login is permitted" 10
    elif grep -qiE '^[[:space:]]*PermitRootLogin[[:space:]]+no' "$sshd_config" 2>/dev/null; then
        pass "SSH" "Root login disabled"
    else
        warn "SSH" "PermitRootLogin not explicitly set" 5
    fi

    # Password auth
    if grep -qiE '^[[:space:]]*PasswordAuthentication[[:space:]]+yes' "$sshd_config" 2>/dev/null; then
        fail "SSH" "Password authentication enabled" 10
    elif grep -qiE '^[[:space:]]*PasswordAuthentication[[:space:]]+no' "$sshd_config" 2>/dev/null; then
        pass "SSH" "Password authentication disabled"
    else
        warn "SSH" "PasswordAuthentication not explicitly set" 5
    fi

    # Check for non-standard port
    local port=$(grep -iE '^[[:space:]]*Port[[:space:]]+' "$sshd_config" 2>/dev/null | awk '{print $2}')
    if [ -n "$port" ] && [ "$port" != "22" ]; then
        pass "SSH" "Non-standard SSH port: $port (good)"
    fi
}

# ─── NETWORK CHECKS ───
check_network() {
    log ""
    log "── Network & Services ──"

    # Check firewall
    if command -v ufw &>/dev/null; then
        if ufw status 2>/dev/null | grep -q "Status: active"; then
            pass "NET" "UFW firewall active"
        else
            warn "NET" "UFW installed but not active" 10
        fi
    elif command -v iptables &>/dev/null; then
        local rules=$(iptables -L 2>/dev/null | wc -l || echo "0")
        if [ "$rules" -gt 10 ]; then
            pass "NET" "iptables has rules configured"
        else
            warn "NET" "iptables has minimal rules" 5
        fi
    else
        warn "NET" "No firewall detected" 10
    fi

    # Check listening services
    if command -v ss &>/dev/null; then
        local exposed=$(ss -tlnp 2>/dev/null | grep -c '0\.0\.0\.0' || echo "0")
        if [ "$exposed" -gt 0 ]; then
            warn "NET" "$exposed service(s) listening on 0.0.0.0" 5
            if [ "$JSON_OUTPUT" = false ]; then
                ss -tlnp 2>/dev/null | grep '0\.0\.0\.0' | while IFS= read -r line; do
                    log "        $line"
                done
            fi
        else
            pass "NET" "No services exposed on 0.0.0.0"
        fi
    elif command -v netstat &>/dev/null; then
        local exposed=$(netstat -tlnp 2>/dev/null | grep -c '0\.0\.0\.0' || echo "0")
        if [ "$exposed" -gt 0 ]; then
            warn "NET" "$exposed service(s) listening on 0.0.0.0" 5
        fi
    fi
}

# ─── FILE PERMISSION CHECKS ───
check_files() {
    log ""
    log "── File Permissions ──"

    # Check config files
    for cfg in /root/.openclaw/openclaw.json /home/node/.openclaw/openclaw.json ~/.openclaw/openclaw.json; do
        if [ -f "$cfg" ]; then
            local perms=$(stat -c '%a' "$cfg" 2>/dev/null || echo "unknown")
            if [ "$perms" = "644" ] || [ "$perms" = "600" ] || [ "$perms" = "640" ]; then
                pass "FILES" "Config permissions OK ($perms): $cfg"
            elif [ "$perms" = "666" ] || [ "$perms" = "777" ]; then
                fail "FILES" "Config world-readable ($perms): $cfg" 10
            else
                pass "FILES" "Config permissions: $perms ($cfg)"
            fi
            break
        fi
    done

    # SSH key permissions
    for key_dir in /root/.ssh /home/node/.ssh ~/.ssh; do
        if [ -d "$key_dir" ]; then
            local dir_perms=$(stat -c '%a' "$key_dir" 2>/dev/null || echo "unknown")
            if [ "$dir_perms" != "700" ] && [ "$dir_perms" != "750" ]; then
                warn "FILES" "SSH dir permissions too open ($dir_perms): $key_dir" 5
            fi
            for key in "$key_dir"/id_*; do
                if [ -f "$key" ] && ! echo "$key" | grep -q '\.pub$'; then
                    local kperms=$(stat -c '%a' "$key" 2>/dev/null || echo "unknown")
                    if [ "$kperms" != "600" ] && [ "$kperms" != "400" ]; then
                        fail "FILES" "SSH private key too open ($kperms): $key" 10
                    else
                        pass "FILES" "SSH key permissions OK ($kperms): $(basename "$key")"
                    fi
                fi
            done
            break
        fi
    done

    # .env files
    for env_file in /root/.openclaw/.env /home/node/.openclaw/.env .env; do
        if [ -f "$env_file" ]; then
            local eperms=$(stat -c '%a' "$env_file" 2>/dev/null || echo "unknown")
            if [ "$eperms" = "666" ] || [ "$eperms" = "777" ] || [ "$eperms" = "644" ]; then
                warn "FILES" ".env file too open ($eperms): $env_file" 5
            else
                pass "FILES" ".env permissions OK ($eperms): $env_file"
            fi
        fi
    done

    # Sensitive files in /tmp
    local tmp_sensitive=$(find /tmp -maxdepth 2 -name '*.key' -o -name '*.pem' -o -name '*.env' -o -name '*secret*' 2>/dev/null | head -5)
    if [ -n "$tmp_sensitive" ]; then
        warn "FILES" "Sensitive files found in /tmp" 5
    else
        pass "FILES" "No sensitive files in /tmp"
    fi
}

# ─── RUN CHECKS ───
log ""
log "═══ OpenClaw Security Audit ═══"
log "Date: $(date '+%Y-%m-%d %H:%M:%S')"

should_check "config" && check_config
should_check "docker" && check_docker
should_check "ssh" && check_ssh
should_check "network" && check_network
should_check "files" && check_files

# Clamp score
[ "$SCORE" -lt 0 ] && SCORE=0

# Rating
if [ "$SCORE" -ge 90 ]; then
    RATING="🟢 Excellent"
elif [ "$SCORE" -ge 70 ]; then
    RATING="🟡 Good"
elif [ "$SCORE" -ge 50 ]; then
    RATING="🟠 Fair"
else
    RATING="🔴 Critical"
fi

# Output
if [ "$JSON_OUTPUT" = true ]; then
    # Build JSON
    python3 -c "
import json
data = {
    'score': $SCORE,
    'rating': '$(echo "$RATING" | sed "s/'/\\\\'/g")',
    'issues': $(printf '%s\n' "${ISSUES[@]+"${ISSUES[@]}"}" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))" 2>/dev/null || echo '[]'),
    'warnings': $(printf '%s\n' "${WARNINGS[@]+"${WARNINGS[@]}"}" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))" 2>/dev/null || echo '[]'),
    'passes': $(printf '%s\n' "${PASSES[@]+"${PASSES[@]}"}" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))" 2>/dev/null || echo '[]'),
    'total_checks': $((${#PASSES[@]} + ${#WARNINGS[@]} + ${#ISSUES[@]})),
}
print(json.dumps(data, indent=2))
"
else
    log ""
    log "═══════════════════════════════"
    log "Score: $SCORE/100 — $RATING"
    log "Checks: ${#PASSES[@]} passed, ${#WARNINGS[@]} warnings, ${#ISSUES[@]} critical"

    if [ ${#ISSUES[@]} -gt 0 ]; then
        log ""
        log "Critical Issues:"
        for issue in "${ISSUES[@]}"; do
            log "  $issue"
        done
    fi

    if [ ${#WARNINGS[@]} -gt 0 ]; then
        log ""
        log "Warnings:"
        for warning in "${WARNINGS[@]}"; do
            log "  $warning"
        done
    fi
    log "═══════════════════════════════"
fi
