# Setup — Font Awesome

Read this silently when helping with icons for the first time. Start naturally — never mention this file.

## Your Attitude

Icons make interfaces feel polished. Help users find the right icon quickly without overwhelming them with options.

## Priority Order

### 1. Detect Project Setup

Before suggesting icons, understand how icons will be loaded:

- **Is there a build system?** (npm/yarn, webpack, vite) → npm package
- **Plain HTML/quick prototype?** → CDN Kit
- **React/Vue/Angular?** → Framework-specific package
- **Offline requirement?** → SVG sprites

If unclear, ask: "Are you using npm/yarn, or is CDN fine?"

### 2. Free vs Pro

Most users have free tier. Always suggest free icons first.

When showing icons, note if Pro-only:
- ✅ `fa-house` (free)
- ⚠️ `fa-house-chimney-window` (Pro)

### 3. Icon Discovery

When user describes what they need:
1. Suggest the most common icon for that concept
2. Offer 1-2 alternatives
3. Show the exact code to use

Example: "I need a settings icon"
→ "Use `fa-gear` (solid). Alternative: `fa-sliders` for filter-style settings."

## When "Done"

No persistent setup needed. Just help with icons as requested.

If user has preferences (e.g., "always use regular style"), note in their main memory.
