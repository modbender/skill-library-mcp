#!/bin/bash
#
# Patch OpenClaw to wire up before_tool_call hooks
# This enables plugins to intercept and block tool execution
#
set -e

OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/src/clawdbot-moltbot-openclaw}"
TARGET_FILE="$OPENCLAW_DIR/src/agents/pi-tool-definition-adapter.ts"
PATCH_MARKER="// EXEC-DISPLAY-PATCH: before_tool_call hook"

echo "🔧 OpenClaw before_tool_call Hook Patcher"
echo "========================================="
echo ""

# Check if OpenClaw directory exists
if [ ! -d "$OPENCLAW_DIR" ]; then
    echo "❌ OpenClaw directory not found: $OPENCLAW_DIR"
    echo "   Set OPENCLAW_DIR environment variable to your OpenClaw source path"
    exit 1
fi

# Check if target file exists
if [ ! -f "$TARGET_FILE" ]; then
    echo "❌ Target file not found: $TARGET_FILE"
    exit 1
fi

# Check if already patched
if grep -q "$PATCH_MARKER" "$TARGET_FILE"; then
    echo "✅ Already patched! No changes needed."
    exit 0
fi

echo "📝 Patching $TARGET_FILE..."

# Create backup
cp "$TARGET_FILE" "$TARGET_FILE.backup.$(date +%Y%m%d_%H%M%S)"
echo "   Backup created"

# Apply patch using sed
# 1. Add import at the top (after existing imports)
sed -i '/^import.*logger.*$/a import { getGlobalHookRunner } from "../plugins/hook-runner-global.js";' "$TARGET_FILE"

# 2. Add the hook call before tool.execute
# Find the line with "return await tool.execute" and insert hook code before it
sed -i '/return await tool\.execute(toolCallId, params, signal, onUpdate);/i\
        '"$PATCH_MARKER"'\
        const hookRunner = getGlobalHookRunner();\
        if (hookRunner) {\
          const hookResult = await hookRunner.runBeforeToolCall(\
            { toolName: normalizedName, params: params as Record<string, unknown> },\
            { toolName: normalizedName }\
          );\
          if (hookResult?.block) {\
            return jsonResult({\
              status: "error",\
              tool: normalizedName,\
              error: hookResult.blockReason ?? "Tool call blocked by plugin hook",\
            });\
          }\
        }\
        // END EXEC-DISPLAY-PATCH' "$TARGET_FILE"

echo "   Patch applied"

# Verify patch was applied
if grep -q "$PATCH_MARKER" "$TARGET_FILE"; then
    echo "✅ Patch verified"
else
    echo "❌ Patch verification failed"
    exit 1
fi

# Rebuild
echo ""
echo "🔨 Rebuilding OpenClaw..."
cd "$OPENCLAW_DIR"

# Use pnpm if available, otherwise npm
if command -v pnpm &> /dev/null; then
    pnpm build
else
    npm run build
fi

echo ""
echo "✅ Done! Restart the OpenClaw gateway to apply changes."
echo ""
echo "To restart:"
echo "  systemctl --user restart openclaw-gateway"
echo ""
echo "To verify the hook is working, check logs for:"
echo "  [exec-display] 🟢 SAFE: ..."
