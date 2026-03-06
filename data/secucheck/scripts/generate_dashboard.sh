#!/bin/bash
# Generate HTML dashboard from full_audit.sh results
# Usage: ./generate_dashboard.sh [output.html] [lang]
# lang: ko, en, ja, zh (default: ko)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT="${1:-$HOME/.openclaw/workspace/secucheck-report.html}"
LANG="${2:-ko}"

# Select template based on language
TEMPLATE="$SKILL_DIR/dashboard/template-${LANG}.html"
if [ ! -f "$TEMPLATE" ]; then
    TEMPLATE="$SKILL_DIR/dashboard/template-ko.html"
fi

# Run full audit and capture JSON
audit_json=$(bash "$SCRIPT_DIR/full_audit.sh" 2>/dev/null)

# Also get runtime for detailed display
runtime_json=$(bash "$SCRIPT_DIR/runtime_check.sh" 2>/dev/null)

# Parse audit counts
count_critical=$(echo "$audit_json" | jq -r '.counts.critical // 0')
count_high=$(echo "$audit_json" | jq -r '.counts.high // 0')
count_medium=$(echo "$audit_json" | jq -r '.counts.medium // 0')
count_low=$(echo "$audit_json" | jq -r '.counts.low // 0')
count_info=$(echo "$audit_json" | jq -r '.counts.info // 0')

# Parse runtime data
external_ip=$(echo "$runtime_json" | jq -r '.network.external_ip // "unknown"')
vpn_type=$(echo "$runtime_json" | jq -r '.network.vpn_type // "none"')
behind_nat=$(echo "$runtime_json" | jq -r '.network.behind_nat // false')
potentially_exposed=$(echo "$runtime_json" | jq -r '.network.potentially_exposed // false')
in_container=$(echo "$runtime_json" | jq -r '.isolation.in_container // false')
container_type=$(echo "$runtime_json" | jq -r '.isolation.container_type // "none"')
running_as_root=$(echo "$runtime_json" | jq -r '.privileges.running_as_root // false')
can_sudo=$(echo "$runtime_json" | jq -r '.privileges.can_sudo // false')
current_user=$(echo "$runtime_json" | jq -r '.privileges.current_user // "unknown"')
openclaw_dir_perms=$(echo "$runtime_json" | jq -r '.filesystem.openclaw_dir_perms // "unknown"')

# Determine overall score
if [ "$count_critical" -gt 0 ]; then
    score_class="score-critical"
    score_emoji="🔴"
    score_label="Critical"
    score_desc="즉시 조치가 필요합니다"
elif [ "$count_high" -gt 0 ]; then
    score_class="score-high"
    score_emoji="🟠"
    score_label="High Risk"
    score_desc="빠른 조치를 권장합니다"
elif [ "$count_medium" -gt 0 ]; then
    score_class="score-medium"
    score_emoji="🟡"
    score_label="Medium"
    score_desc="개선이 필요합니다"
else
    score_class="score-good"
    score_emoji="🟢"
    score_label="Good"
    score_desc="전반적으로 양호합니다"
fi

# Generate runtime content
runtime_content="
<div class=\"runtime-card\">
    <h4>🌐 Network</h4>
    <div class=\"runtime-item\"><span>External IP</span><span class=\"runtime-value\">$external_ip</span></div>
    <div class=\"runtime-item\"><span>VPN</span><span class=\"runtime-value $([ "$vpn_type" != "none" ] && echo 'good' || echo 'warn')\">$vpn_type</span></div>
    <div class=\"runtime-item\"><span>Behind NAT</span><span class=\"runtime-value $([ "$behind_nat" = "true" ] && echo 'good' || echo 'warn')\">$behind_nat</span></div>
    <div class=\"runtime-item\"><span>Exposed</span><span class=\"runtime-value $([ "$potentially_exposed" = "true" ] && echo 'warn' || echo 'good')\">$potentially_exposed</span></div>
</div>
<div class=\"runtime-card\">
    <h4>📦 Isolation</h4>
    <div class=\"runtime-item\"><span>Container</span><span class=\"runtime-value $([ "$in_container" = "true" ] && echo 'good' || echo 'warn')\">$in_container</span></div>
    <div class=\"runtime-item\"><span>Type</span><span class=\"runtime-value\">$container_type</span></div>
</div>
<div class=\"runtime-card\">
    <h4>👤 Privileges</h4>
    <div class=\"runtime-item\"><span>User</span><span class=\"runtime-value\">$current_user</span></div>
    <div class=\"runtime-item\"><span>Root</span><span class=\"runtime-value $([ "$running_as_root" = "true" ] && echo 'bad' || echo 'good')\">$running_as_root</span></div>
    <div class=\"runtime-item\"><span>Sudo</span><span class=\"runtime-value $([ "$can_sudo" = "true" ] && echo 'warn' || echo 'good')\">$can_sudo</span></div>
</div>
<div class=\"runtime-card\">
    <h4>📁 Filesystem</h4>
    <div class=\"runtime-item\"><span>~/.openclaw perms</span><span class=\"runtime-value $([ "$openclaw_dir_perms" = "700" ] && echo 'good' || echo 'warn')\">$openclaw_dir_perms</span></div>
</div>
"

# Function to generate findings section
generate_section() {
    local category="$1"
    local icon="$2"
    local title="$3"
    
    # Get findings for this category
    local findings=$(echo "$audit_json" | jq -r "
        [.findings.critical[], .findings.high[], .findings.medium[], .findings.low[], .findings.info[]] |
        map(select(.category == \"$category\"))
    ")
    
    local count=$(echo "$findings" | jq 'length')
    
    # Determine badge
    local has_critical=$(echo "$findings" | jq '[.[] | select(.category == "'"$category"'")] | map(select(. as \$f | ["critical"] | index(\$f.severity // "unknown"))) | length')
    local has_high=$(echo "$audit_json" | jq "[.findings.high[] | select(.category == \"$category\")] | length")
    local has_medium=$(echo "$audit_json" | jq "[.findings.medium[] | select(.category == \"$category\")] | length")
    local has_low=$(echo "$audit_json" | jq "[.findings.low[] | select(.category == \"$category\")] | length")
    
    local badge="badge-ok"
    local status="OK"
    if [ "$has_critical" -gt 0 ] 2>/dev/null; then
        badge="badge-critical"
        status="Critical"
    elif [ "$has_high" -gt 0 ] 2>/dev/null; then
        badge="badge-high"
        status="High"
    elif [ "$has_medium" -gt 0 ] 2>/dev/null; then
        badge="badge-medium"
        status="Medium"
    elif [ "$has_low" -gt 0 ] 2>/dev/null; then
        badge="badge-low"
        status="Low"
    fi
    
    # Generate findings HTML
    local findings_html=""
    if [ "$count" -gt 0 ] 2>/dev/null && [ "$count" != "0" ]; then
        findings_html="<ul class=\"findings-list\">"
        
        # Critical
        while IFS= read -r finding; do
            [ -z "$finding" ] && continue
            local title=$(echo "$finding" | jq -r '.title')
            local action=$(echo "$finding" | jq -r '.action')
            findings_html+="<li class=\"finding-item critical\">🔴 $title<br><small>→ $action</small></li>"
        done <<< "$(echo "$audit_json" | jq -c ".findings.critical[] | select(.category == \"$category\")")"
        
        # High
        while IFS= read -r finding; do
            [ -z "$finding" ] && continue
            local title=$(echo "$finding" | jq -r '.title')
            local action=$(echo "$finding" | jq -r '.action')
            findings_html+="<li class=\"finding-item high\">🟠 $title<br><small>→ $action</small></li>"
        done <<< "$(echo "$audit_json" | jq -c ".findings.high[] | select(.category == \"$category\")")"
        
        # Medium
        while IFS= read -r finding; do
            [ -z "$finding" ] && continue
            local title=$(echo "$finding" | jq -r '.title')
            local action=$(echo "$finding" | jq -r '.action')
            findings_html+="<li class=\"finding-item medium\">🟡 $title<br><small>→ $action</small></li>"
        done <<< "$(echo "$audit_json" | jq -c ".findings.medium[] | select(.category == \"$category\")")"
        
        # Low
        while IFS= read -r finding; do
            [ -z "$finding" ] && continue
            local title=$(echo "$finding" | jq -r '.title')
            local action=$(echo "$finding" | jq -r '.action')
            findings_html+="<li class=\"finding-item low\">🟢 $title<br><small>→ $action</small></li>"
        done <<< "$(echo "$audit_json" | jq -c ".findings.low[] | select(.category == \"$category\")")"
        
        # Info
        while IFS= read -r finding; do
            [ -z "$finding" ] && continue
            local title=$(echo "$finding" | jq -r '.title')
            local action=$(echo "$finding" | jq -r '.action')
            findings_html+="<li class=\"finding-item info\">⚪ $title<br><small>→ $action</small></li>"
        done <<< "$(echo "$audit_json" | jq -c ".findings.info[] | select(.category == \"$category\")")"
        
        findings_html+="</ul>"
    else
        findings_html="<p style=\"color: var(--text-muted);\">이 영역은 양호합니다.</p>"
    fi
    
    echo "
<div class=\"section\" id=\"section-$(echo $category | tr '[:upper:]' '[:lower:]')\">
    <div class=\"section-header\" onclick=\"toggleSection('$(echo $category | tr '[:upper:]' '[:lower:]')')\">
        <div class=\"section-title\"><span>$icon</span> $title</div>
        <span class=\"section-badge $badge\">$status</span>
    </div>
    <div class=\"section-content expandable\">$findings_html</div>
</div>"
}

# Runtime badge
runtime_findings=$(echo "$audit_json" | jq '[.findings.critical[], .findings.high[], .findings.medium[], .findings.low[], .findings.info[] | select(.category == "RUNTIME")] | length')
if [ "$runtime_findings" -gt 0 ] 2>/dev/null; then
    has_crit=$(echo "$audit_json" | jq '[.findings.critical[] | select(.category == "RUNTIME")] | length')
    has_high=$(echo "$audit_json" | jq '[.findings.high[] | select(.category == "RUNTIME")] | length')
    has_med=$(echo "$audit_json" | jq '[.findings.medium[] | select(.category == "RUNTIME")] | length')
    
    if [ "$has_crit" -gt 0 ] 2>/dev/null; then
        runtime_badge="badge-critical"
        runtime_status="Critical"
    elif [ "$has_high" -gt 0 ] 2>/dev/null; then
        runtime_badge="badge-high"
        runtime_status="High"
    elif [ "$has_med" -gt 0 ] 2>/dev/null; then
        runtime_badge="badge-medium"
        runtime_status="Medium"
    else
        runtime_badge="badge-low"
        runtime_status="Low"
    fi
else
    runtime_badge="badge-ok"
    runtime_status="OK"
fi

# Generate all sections
findings_sections=""
findings_sections+=$(generate_section "CHANNEL" "📢" "Channels")
findings_sections+=$(generate_section "AGENT" "🤖" "Agents")
findings_sections+=$(generate_section "WORKSPACE" "📁" "Workspace")
findings_sections+=$(generate_section "SKILL" "🧩" "Skills")
findings_sections+=$(generate_section "CRON" "⏰" "Cron Jobs")
findings_sections+=$(generate_section "NETWORK" "🌐" "Network")

# Read template and replace placeholders
html=$(cat "$TEMPLATE")
html="${html//\{\{SCAN_TIME\}\}/$(date '+%Y-%m-%d %H:%M:%S')}"
html="${html//\{\{HOSTNAME\}\}/$(hostname)}"
html="${html//\{\{SCORE_CLASS\}\}/$score_class}"
html="${html//\{\{SCORE_EMOJI\}\}/$score_emoji}"
html="${html//\{\{SCORE_LABEL\}\}/$score_label}"
html="${html//\{\{SCORE_DESC\}\}/$score_desc}"
html="${html//\{\{COUNT_CRITICAL\}\}/$count_critical}"
html="${html//\{\{COUNT_HIGH\}\}/$count_high}"
html="${html//\{\{COUNT_MEDIUM\}\}/$count_medium}"
html="${html//\{\{COUNT_LOW\}\}/$count_low}"
html="${html//\{\{COUNT_INFO\}\}/$count_info}"
html="${html//\{\{RUNTIME_BADGE\}\}/$runtime_badge}"
html="${html//\{\{RUNTIME_STATUS\}\}/$runtime_status}"
html="${html//\{\{RUNTIME_CONTENT\}\}/$runtime_content}"
html="${html//\{\{FINDINGS_SECTIONS\}\}/$findings_sections}"

# Write output
echo "$html" > "$OUTPUT"
echo "Dashboard generated: $OUTPUT"
