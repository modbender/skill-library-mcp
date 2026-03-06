# Test Patterns

Browser automation patterns for QA testing with OpenClaw's `browser` tool.

## Table of Contents
1. [Navigation](#navigation)
2. [Snapshots](#snapshots)
3. [Form Interaction](#form-interaction)
4. [Auth Flows](#auth-flows)
5. [Modal Handling](#modal-handling)
6. [Multi-Tab Testing](#multi-tab-testing)
7. [Async Operations](#async-operations)
8. [Console Monitoring](#console-monitoring)
9. [Network Monitoring](#network-monitoring)
10. [Screenshot Capture](#screenshot-capture)

---

## Navigation

### Basic Navigation
```python
browser(action="navigate", targetUrl="https://example.com")
browser(action="navigate", targetUrl="https://example.com/dashboard")
```

### Relative Navigation
```python
# After initial navigation, use relative paths
browser(action="navigate", targetUrl="/settings")
```

### Wait for Navigation
```python
# Click triggers navigation, wait for URL change
browser(action="act", request={
    "kind": "click",
    "ref": "dashboard_link"
})
# Take snapshot to verify new page
browser(action="snapshot")
```

---

## Snapshots

### Basic Snapshot
```python
result = browser(action="snapshot")
# Returns accessibility tree with element refs
```

### Snapshot with Aria Refs
```python
# Use aria refs for more stable selectors
result = browser(action="snapshot", refs="aria")
```

### Compact Snapshot
```python
# Reduce token usage for large pages
result = browser(action="snapshot", compact=True)
```

### Finding Elements
After snapshot, use `ref` values to interact:
```
button "Sign In" [ref=e15]
textbox "Email" [ref=e23]
```
Then: `browser(action="act", request={"kind": "click", "ref": "e15"})`

---

## Form Interaction

### Click Element
```python
browser(action="act", request={
    "kind": "click",
    "ref": "submit_button"
})
```

### Type Text
```python
browser(action="act", request={
    "kind": "type",
    "ref": "email_input",
    "text": "user@example.com"
})
```

### Clear and Type
```python
# Triple-click to select all, then type
browser(action="act", request={
    "kind": "click",
    "ref": "email_input"
})
browser(action="act", request={
    "kind": "press",
    "key": "Meta+a"
})
browser(action="act", request={
    "kind": "type",
    "ref": "email_input",
    "text": "new@example.com"
})
```

### Select Dropdown
```python
browser(action="act", request={
    "kind": "select",
    "ref": "country_select",
    "values": ["Canada"]
})
```

### Press Key
```python
browser(action="act", request={
    "kind": "press",
    "key": "Enter"
})

browser(action="act", request={
    "kind": "press",
    "key": "Tab"
})
```

### Submit Form
```python
browser(action="act", request={
    "kind": "type",
    "ref": "search_input",
    "text": "query",
    "submit": True  # Presses Enter after typing
})
```

---

## Auth Flows

### Sign In Flow
```python
# Navigate to auth page
browser(action="navigate", targetUrl="https://app.com/auth")
browser(action="snapshot")

# Fill credentials
browser(action="act", request={
    "kind": "type",
    "ref": "email_input",
    "text": "user@test.com"
})
browser(action="act", request={
    "kind": "type",
    "ref": "password_input",
    "text": "password123"
})

# Submit
browser(action="act", request={
    "kind": "click",
    "ref": "sign_in_button"
})

# Wait for redirect
import time
time.sleep(2)
browser(action="snapshot")
# Verify URL contains /home or /dashboard
```

### Check Auth State
```python
# Snapshot and look for user-specific elements
result = browser(action="snapshot")
# Look for: user avatar, logout button, user email display
```

### Sign Out Flow
```python
# Open user menu
browser(action="act", request={
    "kind": "click",
    "ref": "user_menu"
})
browser(action="snapshot")

# Click sign out
browser(action="act", request={
    "kind": "click",
    "ref": "sign_out"
})

# Verify redirect to login
browser(action="snapshot")
```

### Session Persistence Test
```python
# After sign in, refresh the page
browser(action="navigate", targetUrl="https://app.com/dashboard")
# Check if still authenticated
result = browser(action="snapshot")
# Should still see user-specific elements
```

---

## Modal Handling

### Open Modal
```python
browser(action="act", request={
    "kind": "click",
    "ref": "open_modal_button"
})
# Wait for modal animation
import time
time.sleep(0.5)
browser(action="snapshot")
```

### Interact with Modal Content
```python
# Modal elements appear in snapshot with refs
browser(action="act", request={
    "kind": "type",
    "ref": "modal_input",
    "text": "value"
})
browser(action="act", request={
    "kind": "click",
    "ref": "modal_confirm"
})
```

### Close Modal
```python
# Click close button
browser(action="act", request={
    "kind": "click",
    "ref": "modal_close"
})

# Or press Escape
browser(action="act", request={
    "kind": "press",
    "key": "Escape"
})
```

### Alert/Confirm Dialogs
```python
# Handle browser dialogs
browser(action="dialog", accept=True)  # Click OK
browser(action="dialog", accept=False)  # Click Cancel
browser(action="dialog", accept=True, promptText="input value")  # For prompts
```

---

## Multi-Tab Testing

### Stripe Checkout Flow
```python
# Click checkout button (opens new tab)
browser(action="act", request={
    "kind": "click",
    "ref": "checkout_button"
})

# Wait for new tab
import time
time.sleep(3)

# List tabs
tabs = browser(action="tabs")
# Find Stripe tab by URL
stripe_tab = [t for t in tabs if "checkout.stripe.com" in t.url][0]

# Focus Stripe tab
browser(action="focus", targetId=stripe_tab.targetId)
browser(action="snapshot")

# Verify Stripe checkout loaded
# Look for card input elements
```

### Return to Original Tab
```python
# After Stripe interaction
browser(action="focus", targetId=original_tab_id)
browser(action="snapshot")
```

---

## Async Operations

### Wait for Element
```python
# Poll until element appears
import time
max_wait = 10
waited = 0
while waited < max_wait:
    result = browser(action="snapshot")
    if "target_element" in str(result):
        break
    time.sleep(1)
    waited += 1
```

### Wait for URL Change
```python
# After action that triggers navigation
import time
target_url = "/dashboard"
max_wait = 10
waited = 0
while waited < max_wait:
    result = browser(action="snapshot")
    # Check current URL from snapshot context
    if target_url in current_url:
        break
    time.sleep(1)
    waited += 1
```

### Wait for Loading to Complete
```python
# Look for loading indicators to disappear
import time
max_wait = 15
waited = 0
while waited < max_wait:
    result = browser(action="snapshot")
    if "loading" not in str(result).lower() and "spinner" not in str(result).lower():
        break
    time.sleep(1)
    waited += 1
```

### Wait Request
```python
# Use built-in wait (use sparingly)
browser(action="act", request={
    "kind": "wait",
    "timeMs": 2000
})
```

---

## Console Monitoring

### Check for Errors
```python
errors = browser(action="console", level="error")
# Returns list of console.error messages
if errors:
    for error in errors:
        print(f"Console Error: {error}")
```

### Check All Logs
```python
# Get all console output
logs = browser(action="console")
# Filter by level: error, warn, info, log
```

### Common Error Patterns
- `Failed to fetch` - Network/CORS issue
- `Uncaught TypeError` - JS runtime error
- `ChunkLoadError` - Code splitting issue
- `401 Unauthorized` - Auth issue
- `403 Forbidden` - Permission issue

---

## Network Monitoring

Network errors surface in console or can be observed through UI behavior:

### Detect Failed Requests
```python
# Check for error UI elements after action
result = browser(action="snapshot")
# Look for: "error", "failed", "try again", "offline"
```

### Test Offline Behavior
```python
# Note: Browser tool doesn't directly control network
# Test by checking error handling UI
```

---

## Screenshot Capture

### Full Page Screenshot
```python
browser(action="screenshot", fullPage=True)
# Returns path to screenshot file
```

### Viewport Screenshot
```python
browser(action="screenshot")
# Captures visible viewport only
```

### Screenshot Format
```python
browser(action="screenshot", type="jpeg")  # JPEG format
browser(action="screenshot", type="png")   # PNG format (default)
```

---

## Common Test Sequences

### Smoke Test Sequence
```python
# 1. Navigate
browser(action="navigate", targetUrl="https://app.com")

# 2. Snapshot
result = browser(action="snapshot")

# 3. Check console
errors = browser(action="console", level="error")

# 4. Verify key elements exist
assert "main" in str(result) or "app" in str(result)
assert not errors or len(errors) == 0

# 5. Screenshot for evidence
browser(action="screenshot")
```

### Full Auth Test Sequence
```python
# 1. Start signed out
browser(action="navigate", targetUrl="https://app.com/auth")

# 2. Sign in
browser(action="act", request={"kind": "type", "ref": "email", "text": "user@test.com"})
browser(action="act", request={"kind": "type", "ref": "password", "text": "pass123"})
browser(action="act", request={"kind": "click", "ref": "submit"})

# 3. Wait and verify
time.sleep(2)
result = browser(action="snapshot")
assert "/home" in current_url or "/dashboard" in current_url

# 4. Test session persistence
browser(action="navigate", targetUrl="https://app.com/dashboard")
result = browser(action="snapshot")
assert "user_avatar" in str(result) or "logout" in str(result)

# 5. Sign out
browser(action="act", request={"kind": "click", "ref": "user_menu"})
browser(action="act", request={"kind": "click", "ref": "sign_out"})

# 6. Verify signed out
time.sleep(1)
result = browser(action="snapshot")
assert "sign_in" in str(result).lower() or "/auth" in current_url
```
