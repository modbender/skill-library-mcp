---
name: fastplaywright
description: High-performance browser automation with Fast Playwright MCP. Features token-optimized batch execution, intelligent element selection with fallback, diff detection for change tracking, and comprehensive diagnostics. Use for web testing, form automation, screenshots, navigation flows, and any browser-based task requiring efficient token usage.
---

# Fast Playwright MCP

High-performance browser automation skill using the Fast Playwright MCP server (`@tontoko/fast-playwright-mcp`). This fork of the Microsoft Playwright MCP provides significant token optimization, batch execution, and enhanced element discovery.

## Key Advantages Over Standard Playwright MCP

| Feature | Benefit |
|---------|---------|
| **Token Optimization** | 70-80% reduction via `expectation` parameter |
| **Batch Execution** | 90% token savings for multi-step workflows |
| **Diff Detection** | Track only changes, not full snapshots |
| **Enhanced Selectors** | Multiple selector types with automatic fallback |
| **Diagnostic Tools** | Advanced debugging and element discovery |
| **Image Compression** | JPEG format, quality control, resizing |

## MCP Configuration

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@tontoko/fast-playwright-mcp@latest"]
    }
  }
}
```

## Critical Workflow

Follow these steps in order for optimal results:

### 1. Navigate First
Use `browser_navigate` to load the target page before any other operations.

### 2. Use Batch Execution for Multi-Step Tasks
For 2+ operations, ALWAYS use `browser_batch_execute` instead of individual tool calls.

### 3. Optimize Token Usage
Apply `expectation` parameters to reduce response size.

### 4. Use Diff Detection for State Changes
Enable `diffOptions` when tracking changes without navigation.

## Token Optimization

### The Expectation Parameter

All browser tools support an `expectation` parameter to control response content:

```json
{
  "includeSnapshot": false,    // 70-80% token reduction
  "includeConsole": false,      // Exclude console messages
  "includeTabs": false,         // Hide tab information
  "includeCode": false,         // Suppress code generation
  "includeDownloads": false     // Exclude download info
}
```

### Snapshot Options

Limit snapshot content for focused analysis:

```json
{
  "snapshotOptions": {
    "selector": ".main-content",  // Capture specific section only
    "maxLength": 2000,            // Limit character count
    "format": "aria"              // Use accessibility tree format
  }
}
```

### Diff Detection

Track only changes between operations:

```json
{
  "diffOptions": {
    "enabled": true,
    "format": "minimal",      // Options: unified, split, minimal
    "threshold": 0.1,
    "maxDiffLines": 50,
    "context": 3
  }
}
```

## Enhanced Selector System

### Selector Types (Priority Order)

1. **ref** - System-generated element ID from previous results (highest priority)
2. **css** - Standard CSS selectors (`#id`, `.class`, `tag`)
3. **role** - ARIA roles with optional text (`button`, `textbox`, etc.)
4. **text** - Text content search with optional tag filter

### Selector Arrays with Fallback

All element-based tools accept multiple selectors with automatic fallback:

```json
{
  "selectors": [
    { "css": "#submit-btn" },
    { "role": "button", "text": "Submit" },
    { "text": "Submit", "tag": "button" }
  ]
}
```

Selectors are tried in order until one succeeds. If multiple elements match, returns a candidate list for selection.

## Batch Execution

### Basic Pattern

Execute multiple operations in a single request:

```json
{
  "tool": "browser_batch_execute",
  "arguments": {
    "steps": [
      { "tool": "browser_navigate", "arguments": { "url": "https://example.com/login" } },
      { "tool": "browser_type", "arguments": { "selectors": [{ "css": "#username" }], "text": "user@example.com" } },
      { "tool": "browser_type", "arguments": { "selectors": [{ "css": "#password" }], "text": "password123" } },
      { "tool": "browser_click", "arguments": { "selectors": [{ "role": "button", "text": "Login" }] } }
    ]
  }
}
```

### Advanced Configuration

```json
{
  "tool": "browser_batch_execute",
  "arguments": {
    "steps": [
      {
        "tool": "browser_navigate",
        "arguments": { "url": "https://example.com" },
        "expectation": { "includeSnapshot": false },
        "continueOnError": true
      },
      {
        "tool": "browser_click",
        "arguments": { "selectors": [{ "css": "#submit" }] },
        "expectation": {
          "includeSnapshot": true,
          "snapshotOptions": { "selector": ".result-area" },
          "diffOptions": { "enabled": true, "format": "minimal" }
        }
      }
    ],
    "stopOnFirstError": false,
    "globalExpectation": {
      "includeConsole": false,
      "includeTabs": false
    }
  }
}
```

### Error Handling Options

- `continueOnError` (per-step): Continue even if this step fails
- `stopOnFirstError` (global): Stop entire batch on first error

## Common Patterns

### Navigate and Screenshot

```json
{
  "tool": "browser_batch_execute",
  "arguments": {
    "steps": [
      { "tool": "browser_navigate", "arguments": { "url": "https://example.com" } },
      {
        "tool": "browser_take_screenshot",
        "arguments": {
          "filename": "homepage.png",
          "fullPage": true,
          "expectation": { "includeSnapshot": false }
        }
      }
    ]
  }
}
```

### Form Filling with Submission

```json
{
  "tool": "browser_batch_execute",
  "arguments": {
    "steps": [
      { "tool": "browser_navigate", "arguments": { "url": "https://example.com/contact" } },
      { "tool": "browser_type", "arguments": { "selectors": [{ "css": "#name" }], "text": "John Doe" } },
      { "tool": "browser_type", "arguments": { "selectors": [{ "css": "#email" }], "text": "john@example.com" } },
      { "tool": "browser_type", "arguments": { "selectors": [{ "css": "#message" }], "text": "Hello World" } },
      { "tool": "browser_click", "arguments": { "selectors": [{ "role": "button", "text": "Send" }] } }
    ],
    "globalExpectation": { "includeSnapshot": false }
  }
}
```

### Responsive Design Testing

```json
{
  "tool": "browser_batch_execute",
  "arguments": {
    "steps": [
      { "tool": "browser_navigate", "arguments": { "url": "https://example.com" } },
      { "tool": "browser_resize", "arguments": { "width": 1920, "height": 1080 } },
      { "tool": "browser_take_screenshot", "arguments": { "filename": "desktop.png" } },
      { "tool": "browser_resize", "arguments": { "width": 768, "height": 1024 } },
      { "tool": "browser_take_screenshot", "arguments": { "filename": "tablet.png" } },
      { "tool": "browser_resize", "arguments": { "width": 375, "height": 667 } },
      { "tool": "browser_take_screenshot", "arguments": { "filename": "mobile.png" } }
    ]
  }
}
```

### Login Flow with Verification

```json
{
  "tool": "browser_batch_execute",
  "arguments": {
    "steps": [
      { "tool": "browser_navigate", "arguments": { "url": "https://example.com/login" } },
      { "tool": "browser_type", "arguments": { "selectors": [{ "css": "#email" }], "text": "user@example.com" } },
      { "tool": "browser_type", "arguments": { "selectors": [{ "css": "#password" }], "text": "secret", "submit": true } },
      { "tool": "browser_wait_for", "arguments": { "text": "Dashboard" } }
    ],
    "globalExpectation": { "diffOptions": { "enabled": true } }
  }
}
```

## Diagnostic Tools

### Find Elements

Search for elements using multiple criteria:

```json
{
  "tool": "browser_find_elements",
  "arguments": {
    "searchCriteria": {
      "text": "Submit",
      "role": "button"
    },
    "maxResults": 5,
    "enableEnhancedDiscovery": true
  }
}
```

### Page Diagnostics

Comprehensive page analysis:

```json
{
  "tool": "browser_diagnose",
  "arguments": {
    "diagnosticLevel": "detailed",
    "includePerformanceMetrics": true,
    "includeAccessibilityInfo": true,
    "includeTroubleshootingSuggestions": true
  }
}
```

Diagnostic levels: `none`, `basic`, `standard`, `detailed`, `full`

### HTML Inspection

Extract and analyze HTML content:

```json
{
  "tool": "browser_inspect_html",
  "arguments": {
    "selectors": [{ "css": ".content" }],
    "depth": 3,
    "maxSize": 50000,
    "format": "html",
    "optimizeForLLM": true
  }
}
```

## Image Optimization

### Compressed Screenshots

```json
{
  "tool": "browser_take_screenshot",
  "arguments": {
    "filename": "screenshot.jpg",
    "type": "jpeg",
    "expectation": {
      "imageOptions": {
        "format": "jpeg",
        "quality": 50,
        "maxWidth": 1280
      }
    }
  }
}
```

## Network Request Filtering

Monitor specific network activity:

```json
{
  "tool": "browser_network_requests",
  "arguments": {
    "urlPatterns": ["/api/"],
    "excludeUrlPatterns": ["analytics", "tracking"],
    "methods": ["GET", "POST"],
    "statusRanges": [{ "min": 200, "max": 299 }],
    "maxRequests": 10,
    "newestFirst": true
  }
}
```

## Tab Management

### Multi-Tab Workflow

```json
{
  "tool": "browser_batch_execute",
  "arguments": {
    "steps": [
      { "tool": "browser_tab_new", "arguments": { "url": "https://example.com" } },
      { "tool": "browser_tab_list", "arguments": {} },
      { "tool": "browser_tab_select", "arguments": { "index": 0 } },
      { "tool": "browser_tab_close", "arguments": { "index": 1 } }
    ]
  }
}
```

## Wait Strategies

### Wait for Text

```json
{ "tool": "browser_wait_for", "arguments": { "text": "Loading complete" } }
```

### Wait for Text to Disappear

```json
{ "tool": "browser_wait_for", "arguments": { "textGone": "Loading..." } }
```

### Wait for Time

```json
{ "tool": "browser_wait_for", "arguments": { "time": 2 } }
```

## Console Monitoring

### Filter Console Messages

```json
{
  "tool": "browser_console_messages",
  "arguments": {
    "consoleOptions": {
      "levels": ["error", "warn"],
      "maxMessages": 10,
      "patterns": ["^Error:"],
      "removeDuplicates": true
    }
  }
}
```

## JavaScript Evaluation

### Page-Level Evaluation

```json
{
  "tool": "browser_evaluate",
  "arguments": {
    "function": "() => document.title"
  }
}
```

### Element-Level Evaluation

```json
{
  "tool": "browser_evaluate",
  "arguments": {
    "selectors": [{ "css": "#counter" }],
    "function": "(element) => element.textContent"
  }
}
```

## Dialog Handling

```json
{
  "tool": "browser_handle_dialog",
  "arguments": {
    "accept": true,
    "promptText": "Optional prompt response"
  }
}
```

## File Upload

```json
{
  "tool": "browser_file_upload",
  "arguments": {
    "paths": ["/absolute/path/to/file.pdf"]
  }
}
```

## Drag and Drop

```json
{
  "tool": "browser_drag",
  "arguments": {
    "startSelectors": [{ "css": "#draggable" }],
    "endSelectors": [{ "css": "#dropzone" }]
  }
}
```

## Select Options

```json
{
  "tool": "browser_select_option",
  "arguments": {
    "selectors": [{ "css": "#country" }],
    "values": ["us", "de"]
  }
}
```

## Keyboard Input

```json
{
  "tool": "browser_press_key",
  "arguments": {
    "key": "Enter"
  }
}
```

Special keys: `Enter`, `Tab`, `Escape`, `ArrowUp`, `ArrowDown`, `ArrowLeft`, `ArrowRight`, `Backspace`, `Delete`, `Home`, `End`

## Best Practices

### Token Efficiency

1. **Use batch execution** for 2+ operations
2. **Disable snapshots** for intermediate steps
3. **Enable diff detection** for state tracking
4. **Filter console messages** to relevant levels
5. **Use selective snapshots** with CSS selectors
6. **Compress images** when quality is not critical

### Selector Strategy

1. **Use ref from previous results** when available
2. **Provide fallback selectors** for robustness
3. **Prefer role-based selectors** for accessibility
4. **Use CSS selectors** for specific targeting
5. **Text selectors** as last resort

### Error Handling

1. **Use `continueOnError`** for non-critical steps
2. **Set `stopOnFirstError: false`** for best-effort execution
3. **Use diagnostic tools** when automation fails
4. **Check console messages** for JavaScript errors

### Performance

1. **Minimize snapshot size** with selectors
2. **Use minimal diff format** for change tracking
3. **Filter network requests** to relevant patterns
4. **Batch related operations** together

## Troubleshooting

### Element Not Found

1. Use `browser_find_elements` to discover alternatives
2. Run `browser_diagnose` for page analysis
3. Check for iframes or shadow DOM
4. Verify page has finished loading

### Timeout Issues

1. Use `browser_wait_for` with specific conditions
2. Increase wait time for slow pages
3. Check network requests for blocked resources

### Token Overflow

1. Enable `includeSnapshot: false`
2. Use `snapshotOptions.selector` to limit scope
3. Enable `diffOptions.enabled: true`
4. Reduce `maxRequests` in network filtering

## Tool Reference

### Core Automation
- `browser_navigate` - Navigate to URL
- `browser_click` - Click element
- `browser_type` - Type text
- `browser_hover` - Hover over element
- `browser_drag` - Drag and drop
- `browser_select_option` - Select dropdown option
- `browser_press_key` - Press keyboard key
- `browser_file_upload` - Upload files
- `browser_evaluate` - Execute JavaScript
- `browser_wait_for` - Wait for condition

### Batch Operations
- `browser_batch_execute` - Execute multiple actions

### Information Gathering
- `browser_snapshot` - Capture accessibility snapshot
- `browser_take_screenshot` - Take screenshot
- `browser_console_messages` - Get console output
- `browser_network_requests` - List network requests
- `browser_find_elements` - Find elements by criteria
- `browser_diagnose` - Page diagnostics
- `browser_inspect_html` - HTML content extraction

### Tab Management
- `browser_tab_list` - List all tabs
- `browser_tab_new` - Open new tab
- `browser_tab_select` - Switch to tab
- `browser_tab_close` - Close tab

### Navigation
- `browser_navigate_back` - Go back
- `browser_navigate_forward` - Go forward

### Browser Control
- `browser_resize` - Resize window
- `browser_close` - Close browser
- `browser_install` - Install browser
- `browser_handle_dialog` - Handle alerts/confirms

### Vision (requires `--caps=vision`)
- `browser_mouse_click_xy` - Click at coordinates
- `browser_mouse_move_xy` - Move mouse to coordinates
- `browser_mouse_drag_xy` - Drag between coordinates

### PDF (requires `--caps=pdf`)
- `browser_pdf_save` - Save page as PDF
