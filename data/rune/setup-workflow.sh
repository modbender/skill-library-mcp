#!/bin/bash

echo "🛠️ RUNE WORKFLOW INTEGRATION SETUP"
echo "=================================="
echo ""
echo "⚠️  CRITICAL: This step is required for Rune to be useful!"
echo "   Many users skip workflow integration and never use their memory system."
echo ""

# Create scripts directory
mkdir -p ~/.openclaw/workspace/scripts

# Create session start hook
cat > ~/.openclaw/workspace/scripts/session-start.sh << 'SESSIONEOF'
#!/bin/bash
echo "🧠 RUNE MEMORY RECALL - Session Start"
echo "====================================="

# Force context recall
echo "📋 Recent project context:"
rune search "project" | head -5

echo ""
echo "🎯 Active tasks:"  
rune search "task" | head -3

echo ""
echo "💡 Recent decisions:"
rune search "decision" | head -3

echo ""
echo "🚨 REMINDER: Always recall context BEFORE responding!"
echo "Use: rune recall '[topic]' for specific context"
SESSIONEOF

chmod +x ~/.openclaw/workspace/scripts/session-start.sh

# Create context injection helper with SECURITY SANITIZATION
cat > ~/.openclaw/workspace/scripts/context-inject.sh << 'CONTEXTEOF'
#!/bin/bash
TOPIC="$1"

# Security function to sanitize input - prevents shell injection
sanitize_input() {
  local input="$1"
  
  # Remove dangerous characters and limit length
  echo "$input" | \
    head -c 500 | \
    tr -d '`$(){}[]|;&<>' | \
    sed 's/[^a-zA-Z0-9 ._-]//g' | \
    head -c 200
}

# Sanitize the topic input to prevent shell injection attacks
SAFE_TOPIC=$(sanitize_input "$TOPIC")

echo "🧠 INJECTING CONTEXT FOR: $SAFE_TOPIC"
echo "=================================="

# Search for relevant context using SANITIZED input
echo "📋 Relevant context:"
rune recall "$SAFE_TOPIC" 2>/dev/null || rune search "$SAFE_TOPIC" | head -5

# Log usage with sanitized input
echo "$(date): Context recalled for '$SAFE_TOPIC'" >> /tmp/rune-usage.log

echo ""
echo "✅ Context loaded. Proceed with informed response."
CONTEXTEOF

chmod +x ~/.openclaw/workspace/scripts/context-inject.sh

# Create mandatory workflow documentation
cat > ~/.openclaw/workspace/MANDATORY-MEMORY-WORKFLOW.md << 'WORKFLOWEOF'
# MANDATORY MEMORY WORKFLOW - Rune Integration

## 🚨 CRITICAL: Memory Usage Is Not Optional

**Problem**: Many users install Rune but never integrate it into their workflow.
**Result**: Sophisticated memory system goes completely unused.

## 📋 MANDATORY SESSION WORKFLOW

### BEFORE Every Response
```bash
# 1. ALWAYS recall relevant context first
rune recall "current projects recent decisions" 

# 2. Search for specific topic context
rune search "[topic from user message]" | head -5

# 3. Only THEN respond with full context
```

### DURING Conversations
```bash
# Store important decisions immediately
rune add decision "[decision]" --tier [working|long-term]

# Store project context updates  
rune add project "[project].[key]" "[update]" --tier working

# Store lessons learned
rune add lesson "[category].[specific]" "[lesson]" --tier long-term
```

### SUCCESS INDICATORS
✅ Starting responses with recalled context
✅ Referencing past decisions in new work  
✅ Building on previous conversations seamlessly
✅ Never repeating explanations of recent work

### FAILURE INDICATORS  
❌ "Cold start" responses without context
❌ Asking for previously provided information
❌ Losing project continuity between sessions
❌ Not building institutional memory

---
**If you're not using memory, you're not using Rune properly.**
WORKFLOWEOF

echo ""
echo "✅ Workflow integration complete!"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Run session start hook: ~/.openclaw/workspace/scripts/session-start.sh"
echo "2. Use context injection: ~/.openclaw/workspace/scripts/context-inject.sh [topic]"  
echo "3. Read workflow guide: ~/.openclaw/workspace/MANDATORY-MEMORY-WORKFLOW.md"
echo ""
echo "🚨 REMEMBER: Without workflow integration, Rune is just an unused CLI tool!"
