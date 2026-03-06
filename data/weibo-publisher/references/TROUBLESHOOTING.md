# Weibo Publisher Troubleshooting

Detailed solutions for common issues.

## Issue 1: Login Expired / Not Logged In

### Symptoms
- Browser redirects to `https://passport.weibo.com/`
- Login form appears instead of homepage
- "请登录" (Please log in) message

### Solution
1. Manually log in via browser:
   ```javascript
   browser(action="open", targetUrl="https://weibo.com/", profile="openclaw")
   ```
2. Complete login in the browser window
3. Verify login by checking for username in top-right corner
4. Retry posting

### Prevention
- Cookies persist in managed browser profile
- Login should remain valid for weeks/months
- Check login status before posting

## Issue 2: Send Button Disabled

### Symptoms
- Send button has `disabled` attribute in snapshot
- Button appears grayed out
- Clicking has no effect

### Causes & Solutions

**Cause 1: Empty textbox**
- Solution: Ensure content was typed successfully
- Verify: Take snapshot after typing, check textbox has content

**Cause 2: Content too short**
- Solution: Weibo may require minimum length (usually 1 character is enough)
- Verify: Check content length

**Cause 3: Content violates rules**
- Solution: Weibo may detect sensitive words
- Verify: Try different content
- Workaround: Use synonyms or add spaces

**Cause 4: Rate limiting**
- Solution: Wait 30-60 seconds before next post
- Verify: Check if you posted recently

## Issue 3: Element References Changed

### Symptoms
- Error: "Element not found"
- Actions fail silently
- Snapshot shows different refs

### Solution
1. Take fresh snapshot:
   ```javascript
   browser(action="snapshot", targetId="ABC123")
   ```
2. Find new element refs in snapshot output
3. Update your code with new refs

### Common Element Refs

| Element | Common Refs | How to Find |
|---------|-------------|-------------|
| Main textbox | e136, e140 | Look for `textbox "有什么新鲜事想分享给大家？"` |
| Send button | e194, e198 | Look for `button "发送"` |
| Quick post textbox | e1028, e1032 | In popup, look for textbox |
| Quick post send | e1086, e1090 | In popup, look for `button "发送"` |

### Prevention
- Always snapshot before acting
- Don't hardcode element refs
- Parse snapshot output dynamically

## Issue 4: Content Not Appearing After Post

### Symptoms
- Send button clicked successfully
- No error message
- But post doesn't appear in timeline

### Diagnosis Steps

1. **Wait and refresh**:
   ```javascript
   // Wait 2-3 seconds
   await sleep(3000);
   
   // Refresh page
   browser(action="navigate", targetUrl="https://weibo.com/", targetId="ABC123")
   
   // Snapshot to check
   browser(action="snapshot", targetId="ABC123")
   ```

2. **Check for error messages**:
   - Look for red error text in snapshot
   - Common errors: "内容违规" (content violation), "发布失败" (post failed)

3. **Verify login status**:
   - Check if still logged in
   - Look for username in snapshot

### Solutions

**If content violated rules**:
- Modify content to avoid sensitive words
- Remove URLs if they're blocked
- Try shorter content

**If rate limited**:
- Wait 5-10 minutes
- Reduce posting frequency

**If technical error**:
- Refresh page and retry
- Clear browser cache (restart managed browser)
- Re-login if needed

## Issue 5: Request Parameter Format Error

### Symptoms
- Error: "Validation failed for tool 'browser'"
- Error: "request: must be object"

### Cause
Passing `request` as a string instead of JSON object.

### Solution

**❌ Wrong**:
```javascript
browser(action="act", request="{\"kind\": \"type\", \"ref\": \"e136\", \"text\": \"content\"}")
```

**✅ Correct**:
```javascript
browser(action="act", request={"kind": "type", "ref": "e136", "text": "content"})
```

### Prevention
- Always use JSON object syntax
- Don't stringify the request parameter
- Let the tool handle serialization

## Issue 6: Special Characters in Content

### Symptoms
- Content with quotes/newlines fails
- Text appears garbled
- Emoji don't display correctly

### Solutions

**For quotes**:
```javascript
// Escape quotes in content
text: "He said \"hello\" to me"
```

**For newlines**:
```javascript
// Use \n for line breaks
text: "Line 1\nLine 2\nLine 3"
```

**For emoji**:
```javascript
// Emoji work directly, no escaping needed
text: "Hello 😊🎉"
```

**For special characters**:
```javascript
// Most Unicode characters work fine
text: "中文、日本語、한글、العربية"
```

## Issue 7: Browser Not Responding

### Symptoms
- Actions timeout
- No response from browser
- Snapshot fails

### Diagnosis
1. Check browser status:
   ```javascript
   browser(action="status")
   ```

2. Check if browser is running:
   ```bash
   ps aux | grep -i chrome
   ```

### Solutions

**If browser crashed**:
```javascript
// Restart browser
browser(action="stop", profile="openclaw")
browser(action="start", profile="openclaw")
```

**If browser is frozen**:
```bash
# Kill and restart
pkill -f "Chrome.*openclaw"
# Then start again via browser tool
```

**If CDP connection lost**:
- Close and reopen the tab
- Restart managed browser
- Check network connectivity

## Issue 8: Posting Too Frequently

### Symptoms
- Posts succeed but don't appear
- Account temporarily restricted
- "操作过于频繁" (too frequent) message

### Solution
1. **Immediate**: Stop posting for 10-15 minutes
2. **Short-term**: Reduce frequency to max 1 post per hour
3. **Long-term**: Implement rate limiting in code

### Rate Limiting Implementation

```javascript
// Check last post time
const state = JSON.parse(fs.readFileSync('memory/weibo-state.json'));
const now = Math.floor(Date.now() / 1000);
const timeSinceLastPost = now - state.lastPublishTime;

// Enforce minimum interval (e.g., 1 hour = 3600 seconds)
if (timeSinceLastPost < 3600) {
  console.log(`Too soon. Wait ${3600 - timeSinceLastPost} more seconds.`);
  return;
}

// Proceed with posting
```

### Recommended Intervals
- **Safe**: 1 post per hour
- **Moderate**: 1 post per 30 minutes
- **Risky**: More than 2 posts per hour

## Issue 9: Content Length Exceeded

### Symptoms
- Send button disabled after typing
- Character count shows red
- Warning message about length

### Solution
1. **Check length**:
   ```javascript
   if (content.length > 2000) {
     content = content.substring(0, 1997) + "...";
   }
   ```

2. **Split into multiple posts**:
   ```javascript
   const parts = splitContent(content, 2000);
   for (const part of parts) {
     await postWeibo(part);
     await sleep(60000); // Wait 1 minute between posts
   }
   ```

### Weibo Length Limits
- **Maximum**: ~2000 characters
- **Recommended**: 140-280 characters (better engagement)
- **Minimum**: 1 character

## Issue 10: Snapshot Shows Unexpected Page

### Symptoms
- Snapshot shows different page than expected
- Elements not found
- Page structure different

### Causes & Solutions

**Cause 1: Page not loaded**
- Solution: Wait for page load before snapshot
- Add delay: `await sleep(2000)`

**Cause 2: Redirected**
- Solution: Check URL in snapshot response
- Navigate back to correct page

**Cause 3: Popup/modal appeared**
- Solution: Close popup first
- Look for close button in snapshot

**Cause 4: Wrong tab**
- Solution: Verify targetId
- List tabs: `browser(action="tabs")`

## Debugging Checklist

When something goes wrong, check these in order:

1. ✅ Browser is running (`browser(action="status")`)
2. ✅ Logged into Weibo (check snapshot for username)
3. ✅ On correct page (`https://weibo.com/`)
4. ✅ Element refs are current (fresh snapshot)
5. ✅ Request format is correct (JSON object, not string)
6. ✅ Content is valid (length, no violations)
7. ✅ Not rate limited (check last post time)
8. ✅ Network is working (can load page)

## Getting Help

If issues persist:

1. **Capture full context**:
   - Take snapshot and save output
   - Note exact error messages
   - Record steps to reproduce

2. **Check recent changes**:
   - Did Weibo update their UI?
   - Did element refs change?
   - Did login expire?

3. **Try manual operation**:
   - Can you post manually in the browser?
   - If manual works, issue is in automation
   - If manual fails, issue is with account/network

4. **Review logs**:
   - Check `memory/2026-03-02.md` for recent activity
   - Look for patterns in failures
   - Compare with successful posts

---

## Issue 11: "request: must be object" Validation Error

### Symptoms
- Error message: `Validation failed for tool "browser": - request: must be object`
- Post fails before even reaching Weibo
- OpenClaw tool validation fails

### Root Cause
Chinese quotation marks (""、'') in the text content cause JSON parsing errors. The `request` parameter gets serialized as a string instead of an object.

**Example of problematic content**:
```
我们总说要"活在当下"，可当下这一秒...
            ^        ^
            These Chinese quotes break JSON parsing
```

### Solution: Use Unicode Escape

**Step 1**: Convert all Chinese characters to Unicode escape:

```python
content = "我们总说要"活在当下"，可当下这一秒..."
escaped = content.encode('unicode_escape').decode('ascii')
# Result: \u6211\u4eec\u603b\u8bf4\u8981\u201c\u6d3b\u5728\u5f53\u4e0b\u201d...
```

**Step 2**: Use the escaped version in browser tool:

```python
browser(
    action="act",
    request={"kind": "type", "ref": "e31", "text": escaped},
    targetId="881E3B870B4D7562F8573CCB5C7F0C55"
)
```

### Why This Works

Unicode escape converts characters to `\uXXXX` format, which:
- Contains no quotation marks
- Is pure ASCII (safe for JSON)
- Renders correctly in browser (Weibo displays normal Chinese)

### Complete Example

```python
# Original content with problematic quotes
content = """下午两点半，阳光正好。突然想到一个有趣的悖论：我们总说要"活在当下"，可当下这一秒，已经成为了过去。"""

# Convert to Unicode escape
escaped = content.encode('unicode_escape').decode('ascii')

# Use in browser tool - this works!
browser(action="act", request={"kind": "type", "ref": "e31", "text": escaped}, targetId=tab_id)
```

### Prevention

**Always use Unicode escape for Chinese content**:

```python
def prepare_weibo_content(text):
    """Prepare content for Weibo posting"""
    return text.encode('unicode_escape').decode('ascii')

# Usage
content = "你的中文内容"
safe_content = prepare_weibo_content(content)
```

### Related Issues

This also fixes:
- Chinese punctuation issues (，。！？：；)
- Mixed Chinese/English content
- Emoji rendering (💪✨😊)
- Special symbols (→←↑↓)

### Historical Context

This issue was discovered on 2026-03-02 after multiple failed attempts:
1. ❌ Direct Chinese text → JSON parsing error
2. ❌ Escaped JSON string → Still treated as string
3. ❌ CDP WebSocket → Connection closed
4. ✅ Unicode escape → Success!

### See Also

- [UNICODE_ESCAPE.md](UNICODE_ESCAPE.md) - Detailed guide on Unicode escape
- [EXAMPLES.md](EXAMPLES.md) - Examples 8 & 9 show successful usage

---

## Issue 12: Element References Changed

### Symptoms
- Elements not found with previously working refs
- "Element not found" errors
- Clicks/types have no effect

### Root Cause
Weibo's frontend updates element IDs dynamically. Refs like `e136`, `e31`, `e746` change between:
- Different sessions
- Different pages (homepage vs profile)
- Different times of day
- Browser restarts

### Solution: Always Snapshot First

**Never hardcode element refs**. Always follow this pattern:

```python
# Step 1: Navigate to page
browser(action="navigate", targetUrl="https://weibo.com/", targetId=tab_id)
exec(command="sleep 2")

# Step 2: Take snapshot to get current refs
snapshot = browser(action="snapshot", compact=True, targetId=tab_id)

# Step 3: Find the textbox ref from snapshot
# Look for: textbox "有什么新鲜事想分享给大家？"
# Example output: textbox [ref=e31]

# Step 4: Use the current ref
browser(action="act", request={"kind": "click", "ref": "e31"}, targetId=tab_id)
```

### Common Ref Variations

| Element | Observed Refs | Notes |
|---------|---------------|-------|
| Post textbox | e31, e136, e746 | Changes most frequently |
| Send button | e32, e194, e804 | Enabled only after typing |
| Quick post button | e10, e75, e77 | Top navigation |
| Profile link | e6, e49, e50 | Usually stable |

### Best Practice

Create a helper function to extract refs:

```python
def find_element_ref(snapshot_text, element_description):
    """
    Extract element ref from snapshot text
    
    Args:
        snapshot_text: Output from browser snapshot
        element_description: Text to search for (e.g., "有什么新鲜事")
    
    Returns:
        Element ref (e.g., "e31") or None
    """
    import re
    # Look for pattern: [ref=eXXX] near the description
    pattern = rf'{re.escape(element_description)}.*?\[ref=(e\d+)\]'
    match = re.search(pattern, snapshot_text, re.DOTALL)
    return match.group(1) if match else None

# Usage
snapshot = browser(action="snapshot", compact=True, targetId=tab_id)
textbox_ref = find_element_ref(snapshot, "有什么新鲜事")
send_ref = find_element_ref(snapshot, "发送")
```

### Prevention

1. **Never cache refs** across sessions
2. **Always snapshot** before each operation
3. **Verify refs** in snapshot output before using
4. **Handle missing refs** gracefully with error messages

### Recovery

If refs changed mid-operation:
1. Take fresh snapshot
2. Find new refs
3. Retry operation with new refs
4. Update any stored refs

---

## Summary: Critical Issues (2026-03-02)

The two most critical issues discovered:

### 1. Unicode Escape Required (Issue 11)
- **Impact**: Blocks all Chinese content posting
- **Solution**: Always use `text.encode('unicode_escape').decode('ascii')`
- **Priority**: CRITICAL - Must implement for every post

### 2. Dynamic Element Refs (Issue 12)
- **Impact**: Operations fail when refs change
- **Solution**: Always snapshot before each operation
- **Priority**: HIGH - Implement snapshot-first pattern

**Recommended Workflow**:
```python
# 1. Prepare content with Unicode escape
escaped = content.encode('unicode_escape').decode('ascii')

# 2. Navigate and snapshot
browser(action="navigate", targetUrl="https://weibo.com/", targetId=tab_id)
snapshot = browser(action="snapshot", compact=True, targetId=tab_id)

# 3. Extract current refs from snapshot
textbox_ref = extract_ref(snapshot, "有什么新鲜事")

# 4. Click textbox
browser(action="act", request={"kind": "click", "ref": textbox_ref}, targetId=tab_id)

# 5. Type with Unicode escape
browser(action="act", request={"kind": "type", "ref": textbox_ref, "text": escaped}, targetId=tab_id)

# 6. Fresh snapshot for send button
snapshot = browser(action="snapshot", compact=True, targetId=tab_id)
send_ref = extract_ref(snapshot, "发送")

# 7. Click send
browser(action="act", request={"kind": "click", "ref": send_ref}, targetId=tab_id)

# 8. Verify
exec(command="sleep 3")
browser(action="navigate", targetUrl="https://weibo.com/u/<uid>", targetId=tab_id)
browser(action="snapshot", compact=True, targetId=tab_id)
```

This workflow addresses both critical issues and ensures reliable posting.
