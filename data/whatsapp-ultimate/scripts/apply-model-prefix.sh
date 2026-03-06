#!/usr/bin/env bash
# whatsapp-ultimate: Apply model + auth mode prefix to WhatsApp messages.
# Adds {authMode} and {authProfile} template variables to responsePrefix.
# Safe to run multiple times — skips if already applied.

set -euo pipefail

OPENCLAW_SRC=""
for dir in "$HOME/src/clawdbot-moltbot-openclaw" "$HOME/src/openclaw" "$HOME/.openclaw/src"; do
  if [[ -f "$dir/src/auto-reply/reply/response-prefix-template.ts" ]]; then
    OPENCLAW_SRC="$dir"
    break
  fi
done

if [[ -z "$OPENCLAW_SRC" ]]; then
  echo "❌ Could not find OpenClaw source directory."
  exit 1
fi

echo "📁 OpenClaw source: $OPENCLAW_SRC"

# File 1: response-prefix-template.ts — add authMode/authProfile to context type + switch
TPL="$OPENCLAW_SRC/src/auto-reply/reply/response-prefix-template.ts"
if grep -q "authMode" "$TPL" 2>/dev/null; then
  echo "✅ response-prefix-template.ts already patched"
else
  echo "🔧 Patching response-prefix-template.ts..."

  # Add fields to ResponsePrefixContext type
  sed -i '/identityName?: string;/a\  /** Auth profile used (e.g., "anthropic:oauth", "anthropic:api") */\n  authProfile?: string;\n  /** Short auth mode label (e.g., "sub" for subscription\/oauth, "api" for API key) */\n  authMode?: string;' "$TPL"

  # Add cases to the switch statement
  sed -i '/case "identityname":/a\        return context.identityName ?? match;\n      case "auth":\n      case "authmode":\n        return context.authMode ?? match;\n      case "authprofile":\n        return context.authProfile ?? match;' "$TPL"

  # Remove duplicate return for identityname (sed adds before the existing return)
  # This is handled by the existing code structure
  echo "  ✓ Added authMode/authProfile to template context"
fi

# File 2: types.ts — add authProfile to ModelSelectedContext
TYPES="$OPENCLAW_SRC/src/auto-reply/types.ts"
if grep -q "authProfile" "$TYPES" 2>/dev/null; then
  echo "✅ types.ts already patched"
else
  echo "🔧 Patching types.ts..."
  sed -i '/thinkLevel: string | undefined;/a\  /** Auth profile used (e.g., "anthropic:oauth", "anthropic:api") */\n  authProfile?: string;' "$TYPES"
  echo "  ✓ Added authProfile to ModelSelectedContext"
fi

# File 3: reply-prefix.ts — map auth profile to short label
PREFIX="$OPENCLAW_SRC/src/channels/reply-prefix.ts"
if grep -q "authMode" "$PREFIX" 2>/dev/null; then
  echo "✅ reply-prefix.ts already patched"
else
  echo "🔧 Patching reply-prefix.ts..."
  sed -i '/prefixContext.thinkingLevel = ctx.thinkLevel/a\    prefixContext.authProfile = ctx.authProfile;\n    if (ctx.authProfile) {\n      if (ctx.authProfile.includes("oauth") || ctx.authProfile.includes("token")) {\n        prefixContext.authMode = "sub";\n      } else if (ctx.authProfile.includes("api")) {\n        prefixContext.authMode = "api";\n      } else {\n        prefixContext.authMode = ctx.authProfile.split(":").pop() ?? "unknown";\n      }\n    }' "$PREFIX"
  echo "  ✓ Added auth mode mapping"
fi

# File 4: agent-runner-execution.ts — resolve auth profile at model selection
EXEC="$OPENCLAW_SRC/src/auto-reply/reply/agent-runner-execution.ts"
if grep -q "resolvedAuthProfile" "$EXEC" 2>/dev/null; then
  echo "✅ agent-runner-execution.ts already patched"
else
  echo "🔧 Patching agent-runner-execution.ts..."

  # Add imports
  sed -i '/import { runWithModelFallback } from "..\/..\/agents\/model-fallback.js";/a\import { ensureAuthProfileStore, resolveAuthProfileOrder } from "../../agents/model-auth.js";\nimport { isProfileInCooldown } from "../../agents/auth-profiles.js";' "$EXEC"

  # Add auth resolution before onModelSelected call
  python3 -c "
import re
with open('$EXEC', 'r') as f:
    content = f.read()

old = '''          params.opts?.onModelSelected?.({
            provider,
            model,
            thinkLevel: params.followupRun.run.thinkLevel,
          });'''

new = '''          // Resolve active auth profile for prefix interpolation ({auth}, {authMode}).
          let resolvedAuthProfile: string | undefined;
          try {
            const prefixAuthStore = ensureAuthProfileStore(params.followupRun.run.agentDir, { allowKeychainPrompt: false });
            const prefixProfileIds = resolveAuthProfileOrder({
              cfg: params.followupRun.run.config,
              store: prefixAuthStore,
              provider,
            });
            resolvedAuthProfile = prefixProfileIds.find((id) => !isProfileInCooldown(prefixAuthStore, id)) ?? prefixProfileIds[0];
          } catch { /* auth resolution is best-effort */ }
          params.opts?.onModelSelected?.({
            provider,
            model,
            thinkLevel: params.followupRun.run.thinkLevel,
            authProfile: resolvedAuthProfile,
          });'''

if old in content:
    content = content.replace(old, new, 1)
    with open('$EXEC', 'w') as f:
        f.write(content)
    print('  ✓ Added auth profile resolution')
else:
    print('  ⚠ Could not find onModelSelected anchor — may need manual patching')
"
fi

echo ""
echo "✅ All patches applied!"
echo ""
echo "Next steps:"
echo "  1. Rebuild: cd $OPENCLAW_SRC && npm run build"
echo "  2. Restart gateway: openclaw gateway restart"
echo "  3. Set responsePrefix in openclaw.json → channels.whatsapp:"
echo '     "responsePrefix": "🤖({model}|{authMode})"'
