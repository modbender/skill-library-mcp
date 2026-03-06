#!/bin/bash
# Gather installed skills information with security-relevant analysis

SKILLS_DIR="${OPENCLAW_SKILLS:-$HOME/.openclaw/skills}"
BUILTIN_SKILLS="${OPENCLAW_BUILTIN_SKILLS:-$(dirname $(which openclaw 2>/dev/null || echo '/usr/local/lib/node_modules/openclaw'))/skills}"

echo "{"
echo '  "user_skills": ['

first=true
if [ -d "$SKILLS_DIR" ]; then
    for skill_dir in "$SKILLS_DIR"/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            skill_md="$skill_dir/SKILL.md"
            scripts_dir="${skill_dir}scripts"
            
            if [ "$first" = true ]; then
                first=false
            else
                echo ","
            fi
            
            echo -n "    {"
            echo -n '"name": "'"$skill_name"'"'
            echo -n ', "path": "'"$skill_dir"'"'
            
            # Check SKILL.md existence
            if [ -f "$skill_md" ]; then
                echo -n ', "has_skill_md": true'
            else
                echo -n ', "has_skill_md": false'
            fi
            
            # Check skill.json existence
            if [ -f "${skill_dir}skill.json" ]; then
                echo -n ', "has_metadata": true'
                author=$(jq -r '.author // "unknown"' "${skill_dir}skill.json" 2>/dev/null)
                echo -n ', "author": "'"$author"'"'
            else
                echo -n ', "has_metadata": false'
            fi
            
            # Scan scripts for security-relevant patterns
            if [ -d "$scripts_dir" ]; then
                script_count=$(find "$scripts_dir" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.js" \) | wc -l)
                echo -n ', "script_count": '"$script_count"
                
                # Check for network calls
                net_calls=$(grep -rl "curl\|wget\|http.get\|requests.get\|fetch(" "$scripts_dir" 2>/dev/null | wc -l)
                echo -n ', "scripts_with_network": '"$net_calls"
                
                # Check for encoding (potential obfuscation)
                encoding=$(grep -rl "base64\|btoa\|atob" "$scripts_dir" 2>/dev/null | wc -l)
                echo -n ', "scripts_with_encoding": '"$encoding"
                
                # Check for sensitive path access
                sensitive=$(grep -rl "\.ssh\|\.aws\|\.config/gcloud\|\.env" "$scripts_dir" 2>/dev/null | wc -l)
                echo -n ', "scripts_accessing_sensitive": '"$sensitive"
                
                # Check for destructive commands
                destructive=$(grep -rl "rm -rf\|mkfs\|dd if=" "$scripts_dir" 2>/dev/null | wc -l)
                echo -n ', "scripts_with_destructive": '"$destructive"
            fi
            
            echo -n "}"
        fi
    done
fi

echo ""
echo "  ],"

# Count builtin skills
builtin_count=0
if [ -d "$BUILTIN_SKILLS" ]; then
    builtin_count=$(find "$BUILTIN_SKILLS" -maxdepth 1 -type d 2>/dev/null | wc -l)
    builtin_count=$((builtin_count - 1))
fi

echo '  "builtin_skills_count": '"$builtin_count"','
echo '  "skills_dir": "'"$SKILLS_DIR"'"'
echo "}"
