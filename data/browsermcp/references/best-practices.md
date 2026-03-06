# BrowserMCP Best Practices

Advanced techniques and patterns for reliable, efficient browser automation using BrowserMCP.

## Table of Contents

1. [Reliable Interaction Patterns](#reliable-interaction-patterns)
2. [Connection Management](#connection-management)
3. [Error Handling and Debugging](#error-handling-and-debugging)
4. [Working with Dynamic Content](#working-with-dynamic-content)
5. [Form Handling](#form-handling)
6. [Authentication Patterns](#authentication-patterns)
7. [Performance Optimization](#performance-optimization)
8. [Security and Privacy](#security-and-privacy)
9. [Troubleshooting Guide](#troubleshooting-guide)

---

## Reliable Interaction Patterns

### The Snapshot-First Approach

Always start interactions with a snapshot to understand the current page state.

```javascript
// CORRECT: Snapshot first, then interact
snapshot()
click(element="Submit button", ref="e12")

// INCORRECT: Guessing element references
click(element="button#submit")  // May not exist or ref may differ
```

### Refresh Snapshots After Changes

Page structure changes invalidate old element references.

```javascript
// Navigate and wait
navigate(url="https://example.com")
wait(time=2)

// Initial snapshot
snapshot()

// Click something that changes the page
click(element="Load more", ref="e10")
wait(time=2)

// MUST re-snapshot to get new refs
snapshot()

// Now interact with newly loaded content
click(element="New item", ref="e25")  // e25 didn't exist before
```

### Wait Strategically

Use waits at key points to allow dynamic content to stabilize.

| Location | Recommended Wait | Reason |
|----------|------------------|--------|
| After `navigate` | 1-2 seconds | Page load |
| After click (navigation) | 2-3 seconds | New page load |
| After click (AJAX) | 1-2 seconds | Data fetching |
| After form submit | 2-3 seconds | Server processing |
| Before checking dynamic content | 1 second | Content stabilization |

```javascript
// Example: Search with proper waiting
navigate(url="https://search.example.com")
wait(time=1)
snapshot()
type(element="Search box", ref="e8", text="query", submit=true)
wait(time=2)  // Wait for results to load
snapshot()    // Now see search results
```

### Use Descriptive Element Names

Clear descriptions help with debugging and user understanding.

```javascript
// Good: Descriptive and clear
click(element="Primary navigation menu", ref="e5")
type(element="Email address input field", ref="e12", text="user@example.com")

// Avoid: Vague or technical descriptions
click(element="btn", ref="e5")
type(element="input", ref="e12", text="user@example.com")
```

---

## Connection Management

### Ensuring Connection

BrowserMCP requires an active connection to the Chrome extension.

**Before Starting:**
1. Verify the Browser MCP extension is installed
2. User must click the extension icon
3. User must click "Connect" on the target tab
4. Check for connection errors in responses

**Handling Connection Errors:**

```javascript
// If you get: "No connection to browser extension"
// Instruct the user to:
// 1. Click Browser MCP icon in Chrome toolbar
// 2. Click "Connect" button
// 3. Try the action again
```

### Single Tab Limitation

BrowserMCP controls one tab at a time:

```javascript
// Working on Tab A (connected)
navigate(url="https://site-a.com")

// If user switches to Tab B:
// - Tab A automation stops
// - Must reconnect Tab B to continue
// - Previous Tab A state is lost
```

**Workaround for Multi-Tab Workflows:**
1. Complete all actions on current tab
2. Instruct user to switch and reconnect new tab
3. Resume automation on new tab

---

## Error Handling and Debugging

### The Debug Triple

When interactions fail, use this diagnostic pattern:

```javascript
// 1. Visual state check
screenshot()

// 2. Check for JavaScript errors
get_console_logs()

// 3. Get current page structure
snapshot()
```

### Common Error Patterns and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "No connection to browser extension" | Extension not connected | User must click Connect in extension |
| "Element with ref 'eX' not found" | Stale reference | Take fresh snapshot |
| "Element not visible" | Hidden or collapsed | Wait, then re-snapshot |
| Action has no effect | JavaScript error | Check console logs |
| Page not loaded | Network issue | Wait longer, check URL |

### Handling JavaScript Errors

Console logs reveal many automation issues:

```javascript
// After a failed interaction
get_console_logs()

// Look for:
// - "TypeError: Cannot read property..." - JavaScript bugs
// - "Failed to fetch" - Network/API errors
// - "404 Not Found" - Missing resources
// - CORS errors - Cross-origin issues
```

### Using Screenshots for Debugging

Screenshots show the actual page state:

```javascript
// Before critical operation
screenshot()

// After operation (to verify result)
screenshot()

// When something unexpected happens
screenshot()
```

**Common Discoveries:**
- Modal dialogs blocking interaction
- Error messages on page
- Loading spinners still active
- Unexpected page layouts
- CAPTCHA challenges

---

## Working with Dynamic Content

### AJAX-Loaded Content

Modern apps load content dynamically. Handle with waits:

```javascript
// Navigate to page with dynamic content
navigate(url="https://spa.example.com")
wait(time=2)

// Initial load
snapshot()

// Trigger content load
click(element="Load data button", ref="e8")

// Critical: Wait for AJAX to complete
wait(time=2)

// Now content is loaded
snapshot()
```

### Infinite Scroll

Handle infinite scroll patterns:

```javascript
// Scroll and load more items multiple times
for (let i = 0; i < 3; i++) {
  // Scroll to bottom (if scroll tool available)
  // Or click "Load more" button
  click(element="Load more button", ref="e20")
  wait(time=2)
}

// Get final state
snapshot()
```

### Lazy Loading Images

Images may load as you scroll:

```javascript
// Wait for initial viewport
wait(time=2)

// If scrolling is needed to load more:
// (Note: BrowserMCP may have limited scroll control)
// Consider using press_key(key="End") to jump to bottom
press_key(key="End")
wait(time=2)

screenshot()  // Verify images loaded
```

### Polling for Element Appearance

When waiting for specific elements:

```javascript
// Approach: Multiple snapshots with waits
let found = false
let attempts = 0
const maxAttempts = 5

while (!found && attempts < maxAttempts) {
  wait(time=1)
  const result = snapshot()
  
  // Check if desired element exists in snapshot
  // (Parse result content for element)
  if (result.includes("target-element-ref")) {
    found = true
  }
  attempts++
}
```

---

## Form Handling

### Complete Form Submission Pattern

```javascript
// 1. Navigate to form
navigate(url="https://example.com/form")
wait(time=2)

// 2. Get form structure
snapshot()

// 3. Fill fields in order
type(element="First name", ref="e5", text="John")
type(element="Last name", ref="e6", text="Doe")
type(element="Email", ref="e7", text="john.doe@example.com")

// 4. Select from dropdown
select_option(element="Country", ref="e10", values=["US"])

// 5. Fill text area
type(element="Comments", ref="e12", text="This is my feedback...")

// 6. Check/uncheck boxes (if checkbox refs available)
// click(element="Subscribe to newsletter", ref="e15")

// 7. Submit form
type(element="Submit button", ref="e20", text="", submit=true)
// OR:
// click(element="Submit button", ref="e20")

// 8. Wait for response
wait(time=3)

// 9. Verify submission
screenshot()
get_console_logs()
```

### Handling Complex Form Elements

**Dropdowns:**
```javascript
// Single selection
select_option(element="Country", ref="e10", values=["DE"])

// Multiple selection
select_option(element="Languages", ref="e15", values=["en", "de", "fr"])
```

**Radio Buttons:**
```javascript
// Click the radio button option
click(element="Premium plan option", ref="e22")
```

**Checkboxes:**
```javascript
// Toggle checkbox
click(element="Terms agreement checkbox", ref="e25")
```

**Date Pickers:**
```javascript
// Often need to click to open, then select
click(element="Date picker", ref="e30")
wait(time=1)
click(element="Date 15", ref="e35")
```

### Form Validation Handling

Check for validation errors:

```javascript
// Submit form
click(element="Submit", ref="e20")
wait(time=1)

// Check for error messages
snapshot()

// Look for validation errors in snapshot
// - "textbox \"Email\" [e7]" might show aria-invalid
// - Error text might appear near fields

// Take screenshot to see visual error indicators
screenshot()
```

---

## Authentication Patterns

### Using Existing Sessions

BrowserMCP's key advantage: uses existing browser profile with active logins.

```javascript
// User is already logged in via their browser
navigate(url="https://github.com/notifications")
wait(time=2)
snapshot()

// Should show authenticated content immediately
```

### Login Workflow (When Needed)

If user needs to log in:

```javascript
// Navigate to login page
navigate(url="https://example.com/login")
wait(time=2)
snapshot()

// Fill credentials (user may prefer to enter these manually)
// Option A: Have user type password manually first
type(element="Username", ref="e5", text="username")

// Option B: User enters credentials in browser directly
// Then take snapshot to verify logged-in state
wait(time=3)
snapshot()
screenshot()
```

**Privacy Note:** Be cautious with credentials. BrowserMCP uses the real browser profile, so:
- User can enter credentials manually in their browser
- Or use browser's saved password manager
- Avoid typing sensitive passwords through automation if possible

### Two-Factor Authentication (2FA)

```javascript
// Navigate to login
navigate(url="https://example.com/login")
wait(time=2)

// User handles initial login manually in browser
// Then check if 2FA prompt appears
wait(time=5)  // Give user time to handle 2FA
snapshot()

// If 2FA code needs to be entered via automation:
type(element="2FA code field", ref="e15", text="123456")
click(element="Verify", ref="e18")
```

---

## Performance Optimization

### Minimize Unnecessary Operations

```javascript
// Bad: Too many snapshots
snapshot()
click(element="A", ref="e5")
snapshot()
click(element="B", ref="e6")
snapshot()
click(element="C", ref="e7")
snapshot()

// Better: Snapshot only when needed
click(element="A", ref="e5")
click(element="B", ref="e6")
click(element="C", ref="e7")
snapshot()  // One final snapshot
```

### Optimize Wait Times

```javascript
// Bad: Excessive waiting
wait(time=5)
click(element="Button", ref="e5")
wait(time=5)

// Better: Tailored waits
wait(time=2)
click(element="Button", ref="e5")
wait(time=2)

// Best: Progressive waiting
wait(time=1)
click(element="Load", ref="e5")
wait(time=2)  // Adjust based on observed load time
snapshot()    // Verify content loaded
```

### Batch Related Operations

```javascript
// Group form field filling
type(element="First name", ref="e5", text="John")
type(element="Last name", ref="e6", text="Doe")
type(element="Email", ref="e7", text="john@example.com")

// Then single verification
screenshot()
```

---

## Security and Privacy

### Understanding the Security Model

**BrowserMCP Security Characteristics:**
- ✅ Runs locally on user's machine
- ✅ Uses user's real browser profile
- ✅ No data sent to external automation servers
- ✅ Helps bypass basic bot detection
- ⚠️ Has access to user's logged-in sessions
- ⚠️ Can interact with sensitive accounts

### Best Practices

1. **User Consent:** Always confirm with user before accessing sensitive sites
2. **Session Awareness:** Remember you're using their real login sessions
3. **Data Sensitivity:** Be careful with personal or financial data
4. **CAPTCHA Respect:** Don't try to bypass security measures aggressively

### Privacy Reminders for Users

When automating sensitive sites:
- User remains logged in after automation
- Cookies and session data persist
- History is recorded in their browser
- Screenshots show their actual data

---

## Troubleshooting Guide

### Connection Issues

**Problem:** "No connection to browser extension"

**Steps:**
1. Verify extension is installed in Chrome
2. Check extension is enabled
3. User clicks extension icon
4. User clicks "Connect" button
5. Ensure correct tab is active

**Problem:** Connection drops during automation

**Causes:**
- User switched to different tab
- Browser was minimized
- Extension was disabled
- Page was refreshed

**Solution:** Reconnect via extension, resume automation

### Element Interaction Issues

**Problem:** Element reference not found

**Diagnostic Steps:**
1. Take fresh snapshot: `snapshot()`
2. Check if element still exists
3. Verify ref number hasn't changed
4. Look for error messages on page

**Problem:** Click doesn't work

**Possible Causes:**
- Element is hidden (check snapshot visibility)
- Element is behind another element
- JavaScript prevented the click
- Page hasn't finished loading

**Solutions:**
```javascript
// Wait and retry
wait(time=2)
snapshot()
click(element="Button", ref="e12")

// Check for overlays
screenshot()

// Check console for JS errors
get_console_logs()
```

### Navigation Issues

**Problem:** Page doesn't load

**Checks:**
```javascript
// Verify URL
current_url = ?  // Not directly available, use context

// Take screenshot to see error
screenshot()

// Check for error page
get_console_logs()
```

**Problem:** Wrong page loaded

**Causes:**
- Redirects
- Geo-blocking
- Login requirements
- Error pages

**Verification:**
```javascript
snapshot()
// Look for expected elements
// Check page title in snapshot (if shown)
screenshot()
```

### Timing Issues

**Problem:** Content not ready when interacting

**Symptoms:**
- Elements missing from snapshot
- Clicks have no effect
- Stale element references

**Solution:** Add strategic waits:
```javascript
// Before critical operations
wait(time=2)

// After triggering loads
click(element="Load", ref="e5")
wait(time=3)  // Adjust based on observed behavior
snapshot()
```

### Bot Detection

**Problem:** CAPTCHA appears

**Handling:**
- BrowserMCP helps avoid basic detection
- Some sites may still show challenges
- User may need to manually solve
- Avoid rapid repeated requests

**Problem:** Rate limited

**Solutions:**
- Add delays between requests
- Reduce automation frequency
- Use longer wait times
- Respect site's terms of service

---

## Quick Reference Card

### Essential Commands
```javascript
// Navigate and setup
navigate(url="https://example.com")
wait(time=2)
snapshot()

// Basic interaction
click(element="Button", ref="e5")
type(element="Input", ref="e6", text="value", submit=true)
hover(element="Menu", ref="e7")

// Verification
screenshot()
get_console_logs()

// Navigation
go_back()
go_forward()
```

### Common Patterns
```javascript
// Form submission
navigate(url)
wait()
snapshot()
type(element="Field", ref="e5", text="value")
click(element="Submit", ref="e10")
wait()
screenshot()

// Search
navigate(url)
type(element="Search", ref="e8", text="query", submit=true)
wait()
snapshot()
click(element="Result", ref="e15")

// Debugging
screenshot()
get_console_logs()
snapshot()
```

### Error Recovery
```javascript
// When action fails
screenshot()        // See current state
get_console_logs()  // Check for JS errors
snapshot()          // Get fresh element refs
// Retry with new refs
```
