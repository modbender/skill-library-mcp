#!/bin/bash
# Uninstall hook for personality-switcher skill
# This script runs when the skill is uninstalled

WORKSPACE="${HOME}/.openclaw/workspace"
PERSONALITIES_DIR="${WORKSPACE}/personalities"
HEARTBEAT_FILE="${WORKSPACE}/HEARTBEAT.md"

# Restore default personality if it exists as backup
if [ -d "$PERSONALITIES_DIR/default" ]; then
    if [ -f "$PERSONALITIES_DIR/default/SOUL.md" ]; then
        cp "$PERSONALITIES_DIR/default/SOUL.md" "$WORKSPACE/SOUL.md"
    fi
    if [ -f "$PERSONALITIES_DIR/default/IDENTITY.md" ]; then
        cp "$PERSONALITIES_DIR/default/IDENTITY.md" "$WORKSPACE/IDENTITY.md"
    fi
fi

# Remove personality restoration from HEARTBEAT.md
if [ -f "$HEARTBEAT_FILE" ]; then
    # Use Python for safer parsing and removal of the personality-switcher section
    TEMP_FILE="${HEARTBEAT_FILE}.tmp"
    
    python3 - "$HEARTBEAT_FILE" "$TEMP_FILE" << 'PYTHON_EOF'
import sys

heartbeat_file = sys.argv[1]
temp_file = sys.argv[2]

try:
    with open(heartbeat_file, 'r') as f:
        lines = f.readlines()
    
    # Find and remove the personality-switcher section and surrounding blank lines
    output_lines = []
    skip_section = False
    blank_after_section = 0
    
    for i, line in enumerate(lines):
        # Check if this is the personality-switcher section header
        if "Personality Restoration (Managed by personality-switcher)" in line:
            skip_section = True
            # Also skip the preceding blank line(s) if they exist
            while output_lines and output_lines[-1].strip() == "":
                output_lines.pop()
            continue
        
        # If we're skipping and hit another section header (##) or non-empty content, stop skipping
        if skip_section:
            if line.startswith("## ") or (line.startswith("---") and i > 0):
                skip_section = False
                blank_after_section = 0
            elif line.strip() == "":
                blank_after_section += 1
                continue
            else:
                skip_section = False
        
        # Skip restore_personality.py lines
        if "restore_personality.py" in line:
            continue
        
        # Add line if not skipping
        if not skip_section:
            output_lines.append(line)
    
    # Write cleaned content back
    with open(temp_file, 'w') as f:
        f.writelines(output_lines)
    
except Exception as e:
    print(f"Error cleaning HEARTBEAT.md: {e}", file=sys.stderr)
    sys.exit(1)

PYTHON_EOF
    
    if [ $? -eq 0 ]; then
        mv "$TEMP_FILE" "$HEARTBEAT_FILE"
    else
        rm -f "$TEMP_FILE"
    fi
fi

# Delete state file completely (it's part of this skill's state)
STATE_FILE="${PERSONALITIES_DIR}/_personality_state.json"
if [ -f "$STATE_FILE" ]; then
    rm "$STATE_FILE"
fi

# Delete skill metadata file so clawhub doesn't think it's still installed
SKILL_DIR="${WORKSPACE}/skills/personality-switcher"
META_FILE="${SKILL_DIR}/_meta.json"
if [ -f "$META_FILE" ]; then
    rm "$META_FILE"
fi

# Unregister Telegram commands
if python3 "$SKILL_DIR/scripts/unregister_telegram_commands.py" > /dev/null 2>&1; then
    UNREGISTER_OK=true
else
    UNREGISTER_OK=false
fi

# Remove skill directory completely so clawhub knows it's gone
if [ -d "$SKILL_DIR" ]; then
    rm -rf "$SKILL_DIR"
fi

# Remove from clawhub lock.json so it's no longer tracked as installed
CLAWHUB_LOCK="${WORKSPACE}/.clawhub/lock.json"
if [ -f "$CLAWHUB_LOCK" ]; then
    python3 - "$CLAWHUB_LOCK" << 'PYTHON_LOCK'
import json
import sys

lock_file = sys.argv[1]
try:
    with open(lock_file, 'r') as f:
        lock_data = json.load(f)
    
    # Remove personality-switcher from skills list
    if "skills" in lock_data and "personality-switcher" in lock_data["skills"]:
        del lock_data["skills"]["personality-switcher"]
    
    with open(lock_file, 'w') as f:
        json.dump(lock_data, f, indent=2)
except Exception as e:
    # Silently fail if lock.json doesn't exist or is malformed
    pass
PYTHON_LOCK
fi

# Note: personalities/ folder is intentionally left intact for safety
echo "✓ personality-switcher uninstalled"
echo "  - Default personality restored to workspace root"
echo "  - Personality restoration section removed from HEARTBEAT.md"
echo "  - State file (_personality_state.json) deleted"
echo "  - Skill metadata (_meta.json) deleted"
echo "  - Telegram commands unregistered"
echo "  - Skill directory removed"
echo "  - Clawhub lock.json cleaned"
echo "  - Personalities folder preserved (manual deletion recommended if no longer needed)"
