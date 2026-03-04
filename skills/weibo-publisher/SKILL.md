---
name: weibo-publisher
description: Publish posts to Weibo (Sina Weibo) using browser automation. Use when the user wants to post content to Weibo, share updates on Weibo, publish microblogs, or automate Weibo posting. Supports text posts with emoji, hashtags, and mentions. No API key required - uses browser automation with managed browser profile.
---

# Weibo Publisher

Automate posting to Weibo (Sina Weibo) using browser automation through OpenClaw's managed browser.

## Prerequisites

- Weibo account must be logged in via managed browser (profile="openclaw")
- Browser must have active session with valid cookies

## Quick Start

### Basic Post

```python
# 1. Prepare content with Unicode escape (for Chinese text)
content = "刚刚解决了一个技术难题！💪"
escaped_content = content.encode('unicode_escape').decode('ascii')

# 2. Navigate to Weibo homepage
browser(action="navigate", targetUrl="https://weibo.com/", targetId=<tab_id>)

# 3. Get page snapshot to find elements
browser(action="snapshot", targetId=<tab_id>)

# 4. Click the post textbox (ref from snapshot, usually e31 or e136)
browser(action="act", request={"kind": "click", "ref": "e31"}, targetId=<tab_id>)

# 5. Type content with Unicode escape
browser(action="act", request={"kind": "type", "ref": "e31", "text": escaped_content}, targetId=<tab_id>)

# 6. Get fresh snapshot to find send button
browser(action="snapshot", targetId=<tab_id>)

# 7. Click send button (ref from snapshot, usually e32 or e194)
browser(action="act", request={"kind": "click", "ref": "e32"}, targetId=<tab_id>)

# 8. Wait and verify by navigating to profile
sleep(3)
browser(action="navigate", targetUrl="https://weibo.com/u/<your_uid>", targetId=<tab_id>)
browser(action="snapshot", targetId=<tab_id>)
```

## Element References

Common element references on Weibo homepage (as of 2026-03-02):

- **Main post textbox**: `e31` (placeholder: "有什么新鲜事想分享给大家？")
- **Send button**: `e32` (text: "发送", becomes enabled after typing)
- **Quick post button** (top nav): `e10` (text: "发微博")
- **Quick post textbox** (popup): `e746` (when using quick post popup)
- **Quick post send button**: `e804`

**Important Notes**:
- Element references **change frequently** between sessions
- **Always take a fresh snapshot** before each operation
- Refs may differ between homepage (`/`) and profile page (`/u/<uid>`)
- Send button is **disabled** until content is entered

## Content Features

### Supported Content Types

1. **Plain text**: Direct text input
2. **Emoji**: Include emoji directly in text (e.g., "😊🎉")
3. **Hashtags**: Use `#topic#` format (e.g., "#微博话题#")
4. **Mentions**: Use `@username` format
5. **Line breaks**: Use `\n` in text

### Content Limits

- Maximum length: ~2000 characters (Weibo's limit)
- Recommended length: 140-280 characters for better engagement

## Workflows

### Workflow 1: Simple Post

Use the main homepage textbox for quick posts:

1. Open `https://weibo.com/`
2. Snapshot to get element refs
3. Click textbox (e136)
4. Type content
5. Click send (e194)
6. Verify success

### Workflow 2: Quick Post (Popup)

Use the "发微博" button for popup posting:

1. Open `https://weibo.com/`
2. Click "发微博" button (usually e75)
3. Snapshot to get popup element refs
4. Type in popup textbox (e1028)
5. Click popup send button (e1086)
6. Verify success

### Workflow 3: Scheduled Post

For posts to be published later:

1. Follow Workflow 1 or 2 to enter content
2. Click "定时微博" icon (clock icon, ref varies)
3. Select date and time
4. Click send

## State Management

Track posting history in `memory/weibo-state.json`:

```json
{
  "lastPublishTime": 1740880260,
  "lastPublishDate": "2026-03-02T12:38:00+08:00",
  "lastContent": "Your last post content..."
}
```

Update this file after each successful post.

## Error Handling

### Common Issues

1. **"request: must be object" validation error**
   - Symptom: `Validation failed for tool "browser": - request: must be object`
   - Cause: Chinese quotation marks in text causing JSON parsing failure
   - Solution: **Use Unicode escape** for all Chinese characters (see Technical Details)

2. **Login expired**
   - Symptom: Redirected to login page
   - Solution: Manually log in via browser, then retry

3. **Send button disabled**
   - Symptom: Button has `disabled` attribute
   - Solution: Check if textbox is empty or content violates rules

4. **Element refs changed**
   - Symptom: Elements not found with old refs
   - Solution: Take fresh snapshot and use updated refs

5. **Content rejected**
   - Symptom: Error message after clicking send
   - Solution: Check for sensitive words, adjust content

6. **Post not appearing**
   - Symptom: No error but post doesn't show on timeline
   - Solution: Wait 5-10 seconds, refresh page, check if content triggered review

## Best Practices

1. **Always use Unicode escape for Chinese**: Prevents JSON parsing errors with quotation marks
2. **Always snapshot first**: Element refs change frequently between sessions
3. **Separate operations**: Click textbox → Type content → Snapshot → Click send (don't combine)
4. **Verify after posting**: Navigate to profile page and snapshot to confirm post appears
5. **Rate limiting**: Wait at least 60 seconds between posts to avoid restrictions
6. **Content quality**: Keep posts engaging, use hashtags for visibility
7. **State tracking**: Always update weibo-state.json after successful posts
8. **Handle emoji properly**: Emoji work in Unicode escape format (e.g., `\ud83d\udcaa` for 💪)

## Technical Details

### Browser Automation

- **Profile**: `openclaw` (managed browser)
- **Method**: Chrome DevTools Protocol (CDP)
- **Session**: Cookie-based, persists across restarts
- **No API needed**: Pure browser automation

### Request Format

**Critical**: The `request` parameter must be a JSON object, not a string:

```javascript
// ✅ Correct
request={"kind": "type", "ref": "e136", "text": "content"}

// ❌ Wrong
request="{\"kind\": \"type\", \"ref\": \"e136\", \"text\": \"content\"}"
```

### Unicode Escape for Chinese Content (IMPORTANT!)

**Problem**: Chinese quotation marks (""、'') in JSON text can cause parsing errors.

**Solution**: Use Unicode escape (`\uXXXX`) for all Chinese characters:

```python
# Convert Chinese text to Unicode escape
text = "刚刚解决了一个技术难题，感觉特别有成就感！"
escaped = text.encode('unicode_escape').decode('ascii')
# Result: \u521a\u521a\u89e3\u51b3\u4e86...
```

**Example**:

```javascript
// ✅ Correct - Unicode escaped
request={"kind": "type", "ref": "e31", "text": "\u521a\u521a\u89e3\u51b3\u4e86\u4e00\u4e2a\u6280\u672f\u96be\u9898"}

// ❌ Wrong - Direct Chinese with quotes
request={"kind": "type", "ref": "e31", "text": "刚刚解决了一个"技术难题""}
```

**Why**: Chinese quotation marks conflict with JSON string delimiters, causing the `request` parameter to be serialized as a string instead of an object.

## Reference Files

- **[EXAMPLES.md](references/EXAMPLES.md)**: Real-world posting examples (including Unicode escape examples)
- **[TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)**: Detailed error solutions (including critical Issue 11 & 12)
- **[UNICODE_ESCAPE.md](references/UNICODE_ESCAPE.md)**: Complete guide to Unicode escape for Chinese content

## Scripts

- **[post_weibo.py](scripts/post_weibo.py)**: Standalone Python script for posting (optional)
