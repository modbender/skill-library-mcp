#!/bin/bash
# Gather agent configurations comprehensively
# Scans: openclaw.json, agent directories, workspace files

CONFIG_FILE="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
AGENTS_DIR="$HOME/.openclaw/agents"
WORKSPACE_DIR="$HOME/.openclaw/workspace"

echo "{"

#############################################
# 1. Config-based agents
#############################################

echo '  "config_agents": '
if [ -f "$CONFIG_FILE" ]; then
    cat "$CONFIG_FILE" | jq '
      .agents // {} |
      {
        defaults: (.defaults // {} | {
          model: .model,
          workspace: .workspace,
          memorySearch: (.memorySearch | if . then {enabled: .enabled, local: .local} else null end),
          tools: .tools,
          sandbox: .sandbox
        }),
        list: (.list // [] | map({
          id: .id,
          name: .name,
          workspace: .workspace,
          model: .model,
          tools: .tools,
          subagents: .subagents
        }))
      }
    ' 2>/dev/null || echo '{}'
else
    echo '{}'
fi
echo ','

#############################################
# 2. Agent directories scan
#############################################

echo '  "agent_directories": ['
first=true
if [ -d "$AGENTS_DIR" ]; then
    for agent_dir in "$AGENTS_DIR"/*/; do
        [ -d "$agent_dir" ] || continue
        agent_id=$(basename "$agent_dir")
        
        [ "$first" = true ] && first=false || echo ","
        
        echo '    {'
        echo '      "id": "'"$agent_id"'",'
        
        # Check for SOUL.md
        has_soul="false"
        soul_preview=""
        if [ -f "$agent_dir/SOUL.md" ]; then
            has_soul="true"
            # Get first 200 chars for preview (sanitized)
            soul_preview=$(head -c 200 "$agent_dir/SOUL.md" 2>/dev/null | tr '\n' ' ' | sed 's/"/\\"/g')
        fi
        echo '      "has_soul": '"$has_soul"','
        echo '      "soul_preview": "'"$soul_preview"'",'
        
        # Check for tools.yaml or agent.yaml
        has_tools_config="false"
        if [ -f "$agent_dir/tools.yaml" ] || [ -f "$agent_dir/agent.yaml" ]; then
            has_tools_config="true"
        fi
        echo '      "has_tools_config": '"$has_tools_config"','
        
        # Check for sessions directory (activity indicator)
        session_count=0
        if [ -d "$agent_dir/sessions" ]; then
            session_count=$(ls -1 "$agent_dir/sessions" 2>/dev/null | wc -l | tr -d ' ')
        fi
        echo '      "session_count": '"$session_count"','
        
        # Directory permissions
        dir_perms=$(stat -c %a "$agent_dir" 2>/dev/null || stat -f %Lp "$agent_dir" 2>/dev/null || echo "unknown")
        echo '      "permissions": "'"$dir_perms"'"'
        
        echo -n '    }'
    done
fi
echo ''
echo '  ],'

#############################################
# 3. Workspace context files
#############################################

echo '  "workspace": {'

# Check for important workspace files
workspace_files='["AGENTS.md", "SOUL.md", "USER.md", "IDENTITY.md", "TOOLS.md", "MEMORY.md", "HEARTBEAT.md"]'

echo '    "path": "'"$WORKSPACE_DIR"'",'
echo '    "files": {'
first=true
for file in AGENTS.md SOUL.md USER.md IDENTITY.md TOOLS.md MEMORY.md HEARTBEAT.md; do
    [ "$first" = true ] && first=false || echo ","
    filepath="$WORKSPACE_DIR/$file"
    if [ -f "$filepath" ]; then
        size=$(stat -c %s "$filepath" 2>/dev/null || stat -f %z "$filepath" 2>/dev/null || echo 0)
        echo -n '      "'"$file"'": {"exists": true, "size": '"$size"'}'
    else
        echo -n '      "'"$file"'": {"exists": false}'
    fi
done
echo ''
echo '    },'

# Scan AGENTS.md for security-relevant patterns
agents_md_flags=""
if [ -f "$WORKSPACE_DIR/AGENTS.md" ]; then
    # Check for exec mentions
    if grep -q "exec" "$WORKSPACE_DIR/AGENTS.md" 2>/dev/null; then
        agents_md_flags="${agents_md_flags}exec,"
    fi
    # Check for sudo mentions
    if grep -qi "sudo" "$WORKSPACE_DIR/AGENTS.md" 2>/dev/null; then
        agents_md_flags="${agents_md_flags}sudo,"
    fi
    # Check for auto/cron mentions
    if grep -qi "auto\|cron\|schedul" "$WORKSPACE_DIR/AGENTS.md" 2>/dev/null; then
        agents_md_flags="${agents_md_flags}automation,"
    fi
    # Check for external service mentions
    if grep -qiE "api|webhook|http|curl" "$WORKSPACE_DIR/AGENTS.md" 2>/dev/null; then
        agents_md_flags="${agents_md_flags}external_services,"
    fi
    agents_md_flags=$(echo "$agents_md_flags" | sed 's/,$//')
fi
echo '    "agents_md_patterns": "'"$agents_md_flags"'"'

echo '  },'

#############################################
# 4. Security-relevant patterns in SOULs
#############################################

echo '  "soul_security_scan": {'

# Scan all SOUL.md files for risky patterns
risky_patterns=0
soul_files_checked=0

for soul_file in "$AGENTS_DIR"/*/SOUL.md "$WORKSPACE_DIR/SOUL.md"; do
    [ -f "$soul_file" ] || continue
    soul_files_checked=$((soul_files_checked + 1))
    
    # Check for dangerous patterns
    if grep -qiE "ignore.*safety|bypass|override.*restrict|no.*limit" "$soul_file" 2>/dev/null; then
        risky_patterns=$((risky_patterns + 1))
    fi
done

echo '    "files_checked": '"$soul_files_checked"','
echo '    "risky_patterns_found": '"$risky_patterns"
echo '  }'

echo "}"
