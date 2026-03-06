# Weibo Publishing Quick Reference

## 🚀 Quick Start (Copy-Paste Template)

```python
# 1. Prepare content with Unicode escape
content = """你的中文内容"""
escaped = content.encode('unicode_escape').decode('ascii')

# 2. Navigate to Weibo
browser(action="navigate", targetUrl="https://weibo.com/", targetId="<TAB_ID>")
exec(command="sleep 2")

# 3. Snapshot to find textbox
browser(action="snapshot", compact=True, targetId="<TAB_ID>")
# Look for: textbox "有什么新鲜事" [ref=eXX]

# 4. Click textbox
browser(action="act", request={"kind": "click", "ref": "e31"}, targetId="<TAB_ID>")

# 5. Type content
browser(action="act", request={"kind": "type", "ref": "e31", "text": escaped}, targetId="<TAB_ID>")

# 6. Snapshot to find send button
browser(action="snapshot", compact=True, targetId="<TAB_ID>")
# Look for: button "发送" [ref=eXX]

# 7. Click send
browser(action="act", request={"kind": "click", "ref": "e32"}, targetId="<TAB_ID>")

# 8. Verify
exec(command="sleep 3")
browser(action="navigate", targetUrl="https://weibo.com/u/<UID>", targetId="<TAB_ID>")
browser(action="snapshot", compact=True, targetId="<TAB_ID>")
```

## ⚠️ Critical Rules

### 1. ALWAYS Use Unicode Escape for Chinese
```python
# ✅ Correct
escaped = content.encode('unicode_escape').decode('ascii')
browser(action="act", request={"kind": "type", "ref": "e31", "text": escaped})

# ❌ Wrong - Will fail with "request: must be object"
browser(action="act", request={"kind": "type", "ref": "e31", "text": "中文内容"})
```

### 2. ALWAYS Snapshot Before Each Operation
```python
# ✅ Correct - Fresh snapshot
browser(action="snapshot", targetId=tab_id)
browser(action="act", request={"kind": "click", "ref": "e31"})

# ❌ Wrong - Hardcoded ref (will break when refs change)
browser(action="act", request={"kind": "click", "ref": "e136"})
```

### 3. ALWAYS Separate Operations
```python
# ✅ Correct - Separate click and type
browser(action="act", request={"kind": "click", "ref": "e31"})
browser(action="act", request={"kind": "type", "ref": "e31", "text": escaped})

# ❌ Wrong - Combined operations (unreliable)
browser(action="act", request={"kind": "click", "ref": "e31", "text": escaped})
```

## 📋 Common Element Refs

| Element | Common Refs | How to Find |
|---------|-------------|-------------|
| Post textbox | e31, e136, e746 | Search for "有什么新鲜事" |
| Send button | e32, e194, e804 | Search for "发送" |
| Quick post | e10, e75, e77 | Search for "发微博" |

**Note**: Refs change frequently! Always snapshot first.

## 🐛 Common Errors

### Error: "request: must be object"
**Cause**: Chinese quotation marks in text  
**Fix**: Use Unicode escape

### Error: Element not found
**Cause**: Element ref changed  
**Fix**: Take fresh snapshot, use new ref

### Error: Send button disabled
**Cause**: Empty textbox or rate limit  
**Fix**: Verify content typed, wait 60s between posts

## ✅ Verification Checklist

After posting:
- [ ] Wait 3 seconds
- [ ] Navigate to profile page
- [ ] Take snapshot
- [ ] Confirm post appears in timeline
- [ ] Update `memory/weibo-state.json`

## 📊 State File Format

```json
{
  "lastPublishTime": 1772435680,
  "lastPublishDate": "2026-03-02T15:08:00+08:00",
  "lastContent": "Your last post content..."
}
```

## 🎯 Best Practices

1. **Unicode escape**: Always for Chinese content
2. **Snapshot first**: Never hardcode refs
3. **Separate ops**: Click → Type → Snapshot → Send
4. **Verify**: Always check post appeared
5. **Rate limit**: Wait 60s between posts
6. **State tracking**: Update JSON after each post

## 📚 Full Documentation

- [SKILL.md](../SKILL.md) - Complete guide
- [UNICODE_ESCAPE.md](UNICODE_ESCAPE.md) - Unicode escape details
- [EXAMPLES.md](EXAMPLES.md) - Real-world examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Error solutions

## 🔗 Quick Links

- Weibo homepage: https://weibo.com/
- Your profile: https://weibo.com/u/8397479298
- Browser tab ID: Check with `browser(action="tabs")`

## 💡 Pro Tips

1. **Emoji support**: Works perfectly with Unicode escape (💪 → `\ud83d\udcaa`)
2. **Hashtags**: Use Chinese # (＃) for proper recognition
3. **Line breaks**: Include `\n` in original text before escaping
4. **Special chars**: Arrows (→), symbols (✨) all work
5. **Content length**: 140-280 chars optimal for engagement

## 🚨 Emergency Recovery

If posting fails:
1. Check browser status: `browser(action="status")`
2. Check tabs: `browser(action="tabs")`
3. Navigate to Weibo: `browser(action="navigate", targetUrl="https://weibo.com/")`
4. Take snapshot: `browser(action="snapshot")`
5. Verify login: Look for username in snapshot
6. Retry with fresh refs

## 📅 Last Updated

2026-03-02 - Added Unicode escape requirement and dynamic ref handling
