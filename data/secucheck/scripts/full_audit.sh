#!/bin/bash
# Full security audit - outputs pre-analyzed findings in English
# Agent localizes final output to user's language

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Gather all data (use bash explicitly - ClawHub may strip exec permissions)
runtime=$(bash "$SCRIPT_DIR/runtime_check.sh" 2>/dev/null)
config=$(bash "$SCRIPT_DIR/gather_config.sh" 2>/dev/null)
skills=$(bash "$SCRIPT_DIR/gather_skills.sh" 2>/dev/null)
agents=$(bash "$SCRIPT_DIR/gather_agents.sh" 2>/dev/null)

# Run OpenClaw's built-in security audit (--deep for live gateway probe)
cli_audit=$(openclaw security audit --deep --json 2>&1 | sed -n '/^{/,/^}/p')

# Initialize findings arrays
declare -a critical_findings
declare -a high_findings
declare -a medium_findings
declare -a low_findings
declare -a info_findings

#############################################
# Analyze Runtime
#############################################

running_as_root=$(echo "$runtime" | jq -r '.privileges.running_as_root')
can_sudo=$(echo "$runtime" | jq -r '.privileges.can_sudo')
potentially_exposed=$(echo "$runtime" | jq -r '.network.potentially_exposed')
behind_nat=$(echo "$runtime" | jq -r '.network.behind_nat')
vpn_type=$(echo "$runtime" | jq -r '.network.vpn_type')
in_container=$(echo "$runtime" | jq -r '.isolation.in_container')
dir_perms=$(echo "$runtime" | jq -r '.filesystem.openclaw_dir_perms')

# Check: Running as root
if [ "$running_as_root" = "true" ]; then
    critical_findings+=("RUNTIME|root_process|OpenClaw is running as root. Command execution has full system access.|Run openclaw as a regular user.")
fi

# Check: Direct exposure without protection
if [ "$potentially_exposed" = "true" ] && [ "$vpn_type" = "none" ] && [ "$behind_nat" = "false" ]; then
    critical_findings+=("RUNTIME|direct_exposure|Gateway is directly exposed to the internet without protection.|Configure VPN or firewall.")
elif [ "$potentially_exposed" = "true" ] && [ "$vpn_type" = "none" ]; then
    high_findings+=("RUNTIME|lan_exposure|Gateway is exposed on LAN without VPN.|Consider using VPN.")
fi

# Check: Bare metal + sudo
if [ "$in_container" = "false" ] && [ "$can_sudo" = "true" ]; then
    medium_findings+=("RUNTIME|bare_metal_sudo|Running on bare metal with sudo privileges available.|Consider Docker isolation or restrict sudo.")
fi

# Check: File permissions
if [ "$dir_perms" != "700" ] && [ "$dir_perms" != "missing" ] && [ "$dir_perms" != "unknown" ]; then
    medium_findings+=("RUNTIME|weak_perms|~/.openclaw directory has $dir_perms permissions. 700 recommended.|chmod 700 ~/.openclaw")
fi

# Info: VPN detected
if [ "$vpn_type" != "none" ]; then
    info_findings+=("RUNTIME|vpn_active|$vpn_type VPN is active.|Additional protection layer.")
fi

# Info: Container detected
if [ "$in_container" = "true" ]; then
    info_findings+=("RUNTIME|containerized|Running inside a container.|Isolated from host system.")
fi

#############################################
# Analyze Channels
#############################################

# Check groupPolicy
group_policy=$(echo "$config" | jq -r '.channels.slack.groupPolicy // "unknown"')
if [ "$group_policy" = "open" ]; then
    high_findings+=("CHANNEL|open_groups|Slack groupPolicy is 'open'. Bot responds in any channel.|Change to allowlist.")
fi

# Check for allowBots in open context
allow_bots=$(echo "$config" | jq -r '.channels.slack.allowBots // false')
if [ "$allow_bots" = "true" ] && [ "$group_policy" = "open" ]; then
    medium_findings+=("CHANNEL|bots_in_open|allowBots is true with open groupPolicy.|Bot-to-bot injection possible.")
fi

#############################################
# Analyze Agents
#############################################

# Check for dangerous tools on non-main agents
while IFS= read -r agent; do
    [ -z "$agent" ] && continue
    
    agent_id=$(echo "$agent" | jq -r '.id')
    also_allow=$(echo "$agent" | jq -r '.tools.alsoAllow // []')
    deny=$(echo "$agent" | jq -r '.tools.deny // []')
    
    # Skip main agent (higher trust)
    if [ "$agent_id" = "main" ]; then
        continue
    fi
    
    # Check for exec without gateway deny
    has_exec=$(echo "$also_allow" | jq 'contains(["exec"])')
    denies_gateway=$(echo "$deny" | jq 'contains(["gateway"])')
    
    if [ "$has_exec" = "true" ] && [ "$denies_gateway" = "false" ]; then
        high_findings+=("AGENT|exec_no_deny|Agent '$agent_id' has exec permission but doesn't deny gateway.|Add gateway to deny list.")
    elif [ "$has_exec" = "true" ]; then
        low_findings+=("AGENT|exec_with_deny|Agent '$agent_id' has exec but critical tools are denied.|Properly restricted.")
    fi
done <<< "$(echo "$agents" | jq -c '.config_agents.list[]' 2>/dev/null)"

# Check agent directory permissions
open_agent_dirs=0
while IFS= read -r agent_dir; do
    [ -z "$agent_dir" ] && continue
    perms=$(echo "$agent_dir" | jq -r '.permissions')
    if [ "$perms" != "700" ] && [ "$perms" != "unknown" ]; then
        open_agent_dirs=$((open_agent_dirs + 1))
    fi
done <<< "$(echo "$agents" | jq -c '.agent_directories[]' 2>/dev/null)"

if [ "$open_agent_dirs" -gt 0 ]; then
    low_findings+=("AGENT|open_agent_dirs|$open_agent_dirs agent directory(s) have permissions more open than 700.|chmod 700 ~/.openclaw/agents/*")
fi

# Check SOUL security scan
risky_souls=$(echo "$agents" | jq -r '.soul_security_scan.risky_patterns_found // 0')
if [ "$risky_souls" -gt 0 ] 2>/dev/null; then
    high_findings+=("AGENT|risky_soul|$risky_souls SOUL file(s) contain risky patterns (ignore safety, bypass, override).|Review SOUL.md files for dangerous instructions.")
fi

# Check AGENTS.md patterns
agents_md_patterns=$(echo "$agents" | jq -r '.workspace.agents_md_patterns // ""')
if echo "$agents_md_patterns" | grep -q "sudo"; then
    medium_findings+=("WORKSPACE|sudo_in_agents_md|AGENTS.md mentions sudo commands.|Review if sudo is necessary.")
fi

#############################################
# Analyze Skills
#############################################

# Check for skills with dangerous patterns
scripts_with_network=$(echo "$skills" | jq '[.user_skills[] | select(.scripts_with_network > 0)] | length' 2>/dev/null || echo 0)
scripts_with_encoding=$(echo "$skills" | jq '[.user_skills[] | select(.scripts_with_encoding > 0)] | length' 2>/dev/null || echo 0)
scripts_accessing_sensitive=$(echo "$skills" | jq '[.user_skills[] | select(.scripts_accessing_sensitive > 0)] | length' 2>/dev/null || echo 0)

if [ "$scripts_accessing_sensitive" -gt 0 ] 2>/dev/null; then
    medium_findings+=("SKILL|sensitive_access|$scripts_accessing_sensitive skill(s) access sensitive paths (~/.ssh, ~/.aws, etc.).|Review these skills.")
fi

if [ "$scripts_with_encoding" -gt 0 ] 2>/dev/null; then
    medium_findings+=("SKILL|encoding_detected|$scripts_with_encoding skill(s) use base64/encoding.|Check for obfuscation.")
fi

#############################################
# Merge OpenClaw CLI Audit Results (Context-Aware)
#############################################

if [ -n "$cli_audit" ] && echo "$cli_audit" | jq -e '.findings' >/dev/null 2>&1; then
    # Parse CLI audit findings with context-aware severity adjustment
    while IFS= read -r finding; do
        [ -z "$finding" ] && continue
        
        severity=$(echo "$finding" | jq -r '.severity')
        check_id=$(echo "$finding" | jq -r '.checkId')
        title=$(echo "$finding" | jq -r '.title')
        detail=$(echo "$finding" | jq -r '.detail // ""' | tr '\n' ' ')
        remediation=$(echo "$finding" | jq -r '.remediation // "Review and fix."')
        
        # Skip attack_surface summary (just info noise)
        if [ "$check_id" = "summary.attack_surface" ]; then
            continue
        fi
        
        # Context-aware severity adjustment
        adjusted_severity="$severity"
        context_note=""
        
        case "$check_id" in
            "gateway.control_ui.insecure_auth")
                # allowInsecureAuth behind VPN is acceptable
                if [ "$vpn_type" != "none" ]; then
                    adjusted_severity="info"
                    context_note="[VPN 보호됨 - 실제 위험 낮음]"
                elif [ "$behind_nat" = "true" ] && [ "$potentially_exposed" = "false" ]; then
                    adjusted_severity="warn"
                    context_note="[NAT 뒤 - 외부 직접 노출 없음]"
                else
                    context_note="[⚠️ 외부 노출 시 실제 위험]"
                fi
                ;;
            "config.secrets.gateway_password_in_config")
                # Password in config is fine for single-user home setup
                if [ "$vpn_type" != "none" ] || [ "$behind_nat" = "true" ]; then
                    adjusted_severity="info"
                    context_note="[1인 사용 환경 - 허용 가능]"
                else
                    context_note="[공유 서버라면 환경변수 권장]"
                fi
                ;;
            "plugins.extensions_no_allowlist")
                # Check if there are actually untrusted plugins
                ext_count=$(echo "$detail" | grep -oP '\d+(?= extension)')
                if [ "$ext_count" = "1" ] || [ -z "$ext_count" ]; then
                    adjusted_severity="info"
                    context_note="[소수 확장만 있음 - 낮은 위험]"
                fi
                ;;
        esac
        
        # Build full title with context
        full_title="$title"
        if [ -n "$context_note" ]; then
            full_title="$title $context_note"
        fi
        if [ -n "$detail" ] && [ "$detail" != "null" ]; then
            full_title="$full_title ($detail)"
        fi
        
        case "$adjusted_severity" in
            critical)
                critical_findings+=("CONFIG|$check_id|$full_title|$remediation")
                ;;
            warn)
                high_findings+=("CONFIG|$check_id|$full_title|$remediation")
                ;;
            info)
                info_findings+=("CONFIG|$check_id|$full_title|$remediation")
                ;;
        esac
    done <<< "$(echo "$cli_audit" | jq -c '.findings[]' 2>/dev/null)"
fi

#############################################
# Output Results
#############################################

echo "{"
echo '  "scan_time": "'"$(date -Iseconds)"'",'
echo '  "hostname": "'"$(hostname)"'",'
echo '  "os": "'"$(echo "$runtime" | jq -r '.os')"'",'

# Counts
echo '  "counts": {'
echo '    "critical": '"${#critical_findings[@]}"','
echo '    "high": '"${#high_findings[@]}"','
echo '    "medium": '"${#medium_findings[@]}"','
echo '    "low": '"${#low_findings[@]}"','
echo '    "info": '"${#info_findings[@]}"
echo '  },'

# Findings
echo '  "findings": {'

echo '    "critical": ['
first=true
for f in "${critical_findings[@]}"; do
    IFS='|' read -r category id title action <<< "$f"
    [ "$first" = true ] && first=false || echo ","
    echo -n '      {"category": "'"$category"'", "id": "'"$id"'", "title": "'"$title"'", "action": "'"$action"'"}'
done
echo ""
echo '    ],'

echo '    "high": ['
first=true
for f in "${high_findings[@]}"; do
    IFS='|' read -r category id title action <<< "$f"
    [ "$first" = true ] && first=false || echo ","
    echo -n '      {"category": "'"$category"'", "id": "'"$id"'", "title": "'"$title"'", "action": "'"$action"'"}'
done
echo ""
echo '    ],'

echo '    "medium": ['
first=true
for f in "${medium_findings[@]}"; do
    IFS='|' read -r category id title action <<< "$f"
    [ "$first" = true ] && first=false || echo ","
    echo -n '      {"category": "'"$category"'", "id": "'"$id"'", "title": "'"$title"'", "action": "'"$action"'"}'
done
echo ""
echo '    ],'

echo '    "low": ['
first=true
for f in "${low_findings[@]}"; do
    IFS='|' read -r category id title action <<< "$f"
    [ "$first" = true ] && first=false || echo ","
    echo -n '      {"category": "'"$category"'", "id": "'"$id"'", "title": "'"$title"'", "action": "'"$action"'"}'
done
echo ""
echo '    ],'

echo '    "info": ['
first=true
for f in "${info_findings[@]}"; do
    IFS='|' read -r category id title action <<< "$f"
    [ "$first" = true ] && first=false || echo ","
    echo -n '      {"category": "'"$category"'", "id": "'"$id"'", "title": "'"$title"'", "action": "'"$action"'"}'
done
echo ""
echo '    ]'

echo '  },'

# Runtime summary for agent reference
echo '  "runtime_summary": {'
echo '    "vpn": "'"$vpn_type"'",'
echo '    "container": '"$in_container"','
echo '    "root": '"$running_as_root"','
echo '    "sudo": '"$can_sudo"','
echo '    "exposed": '"$potentially_exposed"','
echo '    "nat": '"$behind_nat"
echo '  },'

# Include CLI audit summary
if [ -n "$cli_audit" ] && echo "$cli_audit" | jq -e '.summary' >/dev/null 2>&1; then
    echo '  "cli_audit_included": true,'
    echo '  "cli_audit_summary": '"$(echo "$cli_audit" | jq -c '.summary')"
else
    echo '  "cli_audit_included": false'
fi

echo "}"
