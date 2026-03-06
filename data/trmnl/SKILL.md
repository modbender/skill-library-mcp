---
name: trmnl
description: Generate content for TRMNL e-ink display devices using the TRMNL CSS framework and send via the trmnl CLI. Use when the user wants to display information on their TRMNL device, send messages to an e-ink display, create dashboard content, show notifications, or update their terminal display. Supports rich layouts with the TRMNL framework (flexbox, grid, tables, progress bars, typography utilities).
---

# TRMNL Content Generator

Generate HTML content for TRMNL e-ink display devices.

## Prerequisites

**Install the `trmnl` CLI to the latest version:**
```bash
npm install -g trmnl-cli@latest
```

**Configure a webhook plugin (one-time setup):**
```bash
# Add a plugin
trmnl plugin add home "https://trmnl.com/api/custom_plugins/{uuid}"

# Verify it's configured
trmnl plugin
```

## Quick Start Workflow

1. **Install/update CLI:** Run `npm install -g trmnl-cli@latest`
2. **Check plugins:** Run `trmnl plugin` - if none, prompt user to add one
3. Confirm device type (default: TRMNL OG, 2-bit, 800x480)
4. Read relevant reference docs based on content needs
5. Generate HTML using TRMNL framework classes
6. Write HTML to a temp file and send:
   ```bash
   trmnl send --file /tmp/trmnl-content.html
   # Or to a specific plugin:
   trmnl send --file /tmp/trmnl-content.html --plugin office
   ```
7. **Minimal confirmation only** - Do NOT echo content back to chat

## Sending Content

**From file (recommended):**
```bash
# Write HTML content to file first
cat > /tmp/trmnl-content.html << 'EOF'
<div class="layout layout--col gap--space-between">
  <div class="item">
    <span class="value value--xlarge value--tnums">Hello TRMNL!</span>
  </div>
</div>
<div class="title_bar">
  <span class="title">My Plugin</span>
</div>
EOF

# Send to display
trmnl send --file /tmp/trmnl-content.html
```

**Validate before sending:**
```bash
trmnl validate --file /tmp/trmnl-content.html
```

**View send history:**
```bash
trmnl history
trmnl history --today
trmnl history --failed
```

## Webhook Limits

| Tier | Payload Size | Rate Limit |
|------|--------------|------------|
| Free | **2 KB** (2,048 bytes) | 12 requests/hour |
| TRMNL+ | **5 KB** (5,120 bytes) | 30 requests/hour |

Set tier globally for accurate validation:
```bash
trmnl tier plus  # or "free"
```

## Reference Documentation

Read these files as needed:

| File | When to Read |
|------|--------------|
| `references/patterns.md` | **Start here** - Common plugin patterns |
| `references/framework-overview.md` | Device specs, e-ink constraints |
| `references/css-utilities.md` | Colors, typography, sizing, spacing |
| `references/layout-systems.md` | Flexbox, grid, overflow engines |
| `references/components.md` | Title bar, dividers, items, tables |
| `references/webhook-api.md` | Payload format, troubleshooting |
| `assets/anti-patterns.md` | Common mistakes to avoid |

## Standard Plugin Structure

**Every plugin follows this pattern:**

```html
<div class="layout layout--col gap--space-between">
  <!-- Content sections separated by dividers -->
</div>
<div class="title_bar">
  <img class="image" src="icon.svg">
  <span class="title">Plugin Name</span>
  <span class="instance">Context</span>
</div>
```

- `layout` + `layout--col` = vertical flex container
- `gap--space-between` = push sections to edges
- `title_bar` = always at bottom, outside layout
- `divider` = separate major sections
- **CRITICAL:** Only ONE `.layout` element per view

## Quick Reference

### Grid System (10-Column)

```html
<div class="grid">
  <div class="col--span-3">30%</div>
  <div class="col--span-7">70%</div>
</div>
```

### Item Component

```html
<div class="item">
  <div class="content">
    <span class="value value--xlarge value--tnums">$159,022</span>
    <span class="label">Total Sales</span>
  </div>
</div>
```

### Value Typography

**Always use `value--tnums` for numbers.**

| Class | Usage |
|-------|-------|
| `value--xxxlarge` | Hero KPIs |
| `value--xxlarge` | Large prices |
| `value--xlarge` | Secondary metrics |
| `value--tnums` | **Required for numbers** |

### Grayscale Classes

Use dithered classes, not inline colors:
- `bg--black`, `bg--gray-60`, `bg--gray-30`, `bg--gray-10`, `bg--white`
- `text--black`, `text--gray-50`

### Data Attributes

| Attribute | Purpose |
|-----------|---------|
| `data-fit-value="true"` | Auto-resize text to fit |
| `data-clamp="N"` | Limit to N lines |
| `data-overflow="true"` | Enable overflow management |

## Best Practices

1. Use `layout` + `title_bar` structure
2. Always `value--tnums` for numbers
3. Use `data-fit-value` on primary metrics
4. Use `bg--gray-*` dithered classes
5. Keep payload under tier limit
6. **Minimal confirmations** - just "Sent to TRMNL"

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `trmnl: command not found` | Run `npm install -g trmnl-cli@latest` |
| No plugins configured | Run `trmnl plugin add <name> <url>` |
| Webhook fails | `trmnl config` - verify plugin URL |
| Payload too large | `trmnl validate --file` - check size |
| Numbers misaligned | Add `value--tnums` class |
| Send history | `trmnl history --failed` |
