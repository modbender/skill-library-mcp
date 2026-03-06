# BrowserMCP Tools Reference

Complete reference for all BrowserMCP automation tools including parameters, return values, and usage examples.

## Tool Categories

1. [Navigation Tools](#navigation-tools)
2. [Interaction Tools](#interaction-tools)
3. [Information Tools](#information-tools)
4. [Utility Tools](#utility-tools)

---

## Navigation Tools

### browser_navigate

Navigate to a specified URL. The page will load and automatically capture an ARIA snapshot after navigation.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | The URL to navigate to, including protocol (http:// or https://) |

**Returns:**
- Text confirmation of navigation
- ARIA snapshot of the new page

**Example:**
```javascript
// Navigate to a website
navigate(url="https://example.com")

// Result includes:
// - "Navigated to https://example.com"
// - ARIA accessibility tree snapshot
```

**Best Practices:**
- Always include full URL with protocol
- Wait for page load before interacting
- Take fresh snapshot after navigation

---

### browser_go_back

Navigate back to the previous page in browser history.

**Parameters:** None

**Returns:**
- Text confirmation
- ARIA snapshot of the previous page

**Example:**
```javascript
// Go back to previous page
go_back()

// Result: "Navigated back" + snapshot
```

**Use Cases:**
- Returning to search results
- Undoing accidental navigation
- Testing back button behavior

---

### browser_go_forward

Navigate forward in browser history (after going back).

**Parameters:** None

**Returns:**
- Text confirmation
- ARIA snapshot of the next page

**Example:**
```javascript
// Go forward after going back
go_forward()

// Result: "Navigated forward" + snapshot
```

---

## Interaction Tools

### browser_click

Click an element on the page. Automatically captures a new snapshot after clicking.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `element` | string | Yes | Human-readable description of the element |
| `ref` | string | Yes | Exact target element reference from page snapshot |

**Returns:**
- Text confirmation of click
- Updated ARIA snapshot

**Example:**
```javascript
// Click a button identified in snapshot
click(element="Submit button", ref="e12")

// Result:
// - "Clicked \"Submit button\""
// - Updated page snapshot
```

**Best Practices:**
- Always use `ref` from the most recent snapshot
- Refresh snapshot if page structure changes
- Wait after clicking navigation-triggering elements

---

### browser_type

Type text into an input field or text area. Supports submitting the form automatically.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `element` | string | Yes | Human-readable description of the input field |
| `ref` | string | Yes | Exact target element reference from snapshot |
| `text` | string | Yes | Text to type into the element |
| `submit` | boolean | No | If true, press Enter after typing (default: false) |

**Returns:**
- Text confirmation with typed content
- Updated ARIA snapshot

**Example:**
```javascript
// Type into search box and submit
type(element="Search box", ref="e15", text="BrowserMCP", submit=true)

// Type without submitting
type(element="Username field", ref="e8", text="john_doe")

// Result: "Typed \"BrowserMCP\" into \"Search box\"" + snapshot
```

**Best Practices:**
- Use `submit=true` for search fields instead of separate press_key
- Ensure field is focused before typing (use snapshot to verify)
- Clear field first if needed (select all + delete)

---

### browser_hover

Hover the mouse over an element. Useful for revealing hover menus or tooltips.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `element` | string | Yes | Human-readable description of the element |
| `ref` | string | Yes | Exact target element reference from snapshot |

**Returns:**
- Text confirmation of hover
- Updated ARIA snapshot (shows revealed content)

**Example:**
```javascript
// Hover over dropdown menu trigger
hover(element="User menu", ref="e22")

// Result:
// - "Hovered over \"User menu\""
// - Snapshot may now show dropdown items
```

**Use Cases:**
- Revealing dropdown menus
- Displaying tooltips
- Triggering hover-dependent UI elements

---

### browser_select_option

Select an option from a dropdown menu (`<select>` element).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `element` | string | Yes | Human-readable description of the dropdown |
| `ref` | string | Yes | Exact target element reference from snapshot |
| `values` | array | Yes | Array of values to select (use option value attribute) |

**Returns:**
- Text confirmation
- Updated ARIA snapshot

**Example:**
```javascript
// Select single option
select_option(element="Country dropdown", ref="e18", values=["US"])

// Select multiple options
select_option(element="Languages", ref="e25", values=["en", "de", "fr"])

// Result: "Selected option in \"Country dropdown\"" + snapshot
```

**Finding Values:**
1. Take a snapshot to see the dropdown
2. Look at the dropdown's options in the ARIA tree
3. Use the `value` attribute, not the displayed text

---

### browser_press_key

Simulate a keyboard key press.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `key` | string | Yes | Name of the key to press |

**Returns:**
- Text confirmation

**Example:**
```javascript
// Press Enter
press_key(key="Enter")

// Press Escape
press_key(key="Escape")

// Press Tab
press_key(key="Tab")

// Result: "Pressed key Enter"
```

**Common Key Values:**

```
Navigation:
  Enter, Escape, Tab, Backspace, Delete

Arrow Keys:
  ArrowUp, ArrowDown, ArrowLeft, ArrowRight

Modifiers (use with other keys):
  Control, Alt, Shift, Meta

Function Keys:
  F1, F2, F3, ... F12

Other:
  Home, End, PageUp, PageDown, Space
  Insert, CapsLock, NumLock
  
Letters/Numbers:
  a, b, c, ..., 0, 1, 2, ...
```

**Use Cases:**
- Submitting forms
- Closing modals (Escape)
- Keyboard navigation
- Triggering keyboard shortcuts

---

### browser_drag

Drag an element from one position to another (drag and drop).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `startElement` | string | Yes | Description of element to drag |
| `startRef` | string | Yes | Reference of element to drag |
| `endElement` | string | Yes | Description of drop target |
| `endRef` | string | Yes | Reference of drop target |

**Returns:**
- Text confirmation
- Updated ARIA snapshot

**Example:**
```javascript
// Drag item to different location
drag(
  startElement="File item",
  startRef="e10",
  endElement="Trash folder",
  endRef="e25"
)

// Result: "Dragged \"File item\" to \"Trash folder\"" + snapshot
```

**Use Cases:**
- Reordering lists
- File uploads via drag-drop zones
- Kanban board interactions
- Moving items between containers

---

## Information Tools

### browser_snapshot

Capture an ARIA accessibility snapshot of the current page. This is the primary tool for understanding page structure.

**Parameters:** None

**Returns:**
- ARIA accessibility tree as text
- Shows all interactive elements with refs

**Example:**
```javascript
// Get page snapshot
snapshot()

// Result (example):
// - heading "Welcome to Example" [e1]
// - textbox "Search" [e2]
// - button "Submit" [e3]
// - link "About Us" [e4]
// - combobox "Country" [e5]
```

**ARIA Tree Format:**
```
- [role] "accessible name": [ref]
```

Common roles:
- `button` - Clickable buttons
- `link` - Hyperlinks
- `textbox` - Text input fields
- `combobox` - Dropdown/select elements
- `heading` - Section headings
- `checkbox` / `radio` - Form controls
- `menuitem` - Menu items
- `tab` / `tabpanel` - Tab interfaces

**Best Practices:**
- Take snapshot before any interaction
- Re-snapshot after page changes
- Use refs in brackets [e12] for interactions
- Descriptions in quotes are for humans

---

### browser_screenshot

Take a PNG screenshot of the current viewport.

**Parameters:** None

**Returns:**
- PNG image data

**Example:**
```javascript
// Capture screenshot
screenshot()

// Result: PNG image of current page state
```

**Use Cases:**
- Visual verification of page state
- Debugging (see what the page actually shows)
- Documentation
- Capturing errors or visual bugs

**Best Practices:**
- Use for visual verification
- Take before and after critical operations
- Check when interactions don't work as expected

---

### browser_get_console_logs

Retrieve recent browser console logs.

**Parameters:** None

**Returns:**
- Console messages as formatted text
- Includes log level, message, source

**Example:**
```javascript
// Get console logs
get_console_logs()

// Result (example):
// {"level":"error","message":"Failed to fetch data","source":"api.js:45"}
// {"level":"warn","message":"Deprecated feature used","source":"app.js:12"}
```

**Log Levels:**
- `error` - JavaScript errors
- `warn` - Warnings
- `info` - Informational messages
- `debug` - Debug output

**Use Cases:**
- Debugging failed interactions
- Checking for API errors
- Identifying JavaScript issues
- Monitoring network failures

**Best Practices:**
- Check after unexpected behavior
- Look for error messages before failures
- Clear logs before testing (if possible)

---

## Utility Tools

### browser_wait

Pause execution for a specified time. Essential for allowing dynamic content to load.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `time` | number | Yes | Time to wait in seconds |

**Returns:**
- Text confirmation with wait duration

**Example:**
```javascript
// Wait 2 seconds
wait(time=2)

// Wait 5 seconds for slow page
wait(time=5)

// Result: "Waited for 2 seconds"
```

**When to Use:**
- After navigation (wait for page load)
- After clicks that trigger requests
- Before checking dynamically loaded content
- When animations need to complete

**Best Practices:**
- Start with 1-2 seconds for most operations
- Use longer waits (3-5s) for heavy pages
- Too short = flakiness, too long = slow tests
- Combine with snapshot to verify readiness

---

## Tool Response Patterns

### Success Responses

Most interaction tools return:
```javascript
{
  content: [
    { type: "text", text: "Action description" },
    // Plus snapshot content for interaction tools
    { type: "text", text: "- button \"Submit\" [e12]" },
    // ... more snapshot content
  ]
}
```

### Error Responses

Common error patterns:
```javascript
// Connection error
{
  error: "No connection to browser extension"
}

// Element not found
{
  error: "Element with ref 'e99' not found"
}

// Action failed
{
  error: "Click action failed: element not visible"
}
```

## Tool Selection Guide

| Task | Primary Tool | Secondary Tool |
|------|--------------|----------------|
| Open a website | `navigate` | `wait` |
| Click a button | `click` | `snapshot` |
| Fill a form | `type` | `press_key` (Enter) |
| Select from dropdown | `select_option` | - |
| Hover for menu | `hover` | `snapshot` |
| Submit form | `type` (submit=true) | `press_key` (Enter) |
| Navigate back | `go_back` | `snapshot` |
| Check page structure | `snapshot` | - |
| Visual verification | `screenshot` | - |
| Debug errors | `get_console_logs` | `screenshot` |
| Wait for load | `wait` | `snapshot` |
| Drag and drop | `drag` | - |

## Example Workflows

### Complete Form Submission
```javascript
navigate(url="https://example.com/contact")
wait(time=1)
snapshot()
type(element="Name field", ref="e5", text="John Doe")
type(element="Email field", ref="e6", text="john@example.com")
type(element="Message area", ref="e7", text="Hello, this is a test message.")
click(element="Submit button", ref="e10")
wait(time=2)
screenshot()
get_console_logs()
```

### Search and Navigate Results
```javascript
navigate(url="https://google.com")
wait(time=1)
snapshot()
type(element="Search box", ref="e12", text="BrowserMCP", submit=true)
wait(time=2)
snapshot()
click(element="First result link", ref="e25")
wait(time=2)
screenshot()
```

### Interactive Menu Navigation
```javascript
navigate(url="https://example.com")
snapshot()
hover(element="Products menu", ref="e8")
wait(time=1)
snapshot()  // Now shows dropdown items
click(element="Software option", ref="e15")
wait(time=2)
snapshot()
```
