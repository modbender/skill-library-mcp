# Weibo Publisher Skill - Changelog

## Version 2.0 (2026-03-02)

### 🎉 Major Updates

#### Critical Bug Fix: Unicode Escape Requirement
- **Problem**: Chinese quotation marks (""'') caused JSON parsing errors
- **Error**: `Validation failed for tool "browser": - request: must be object`
- **Solution**: Implemented Unicode escape for all Chinese content
- **Impact**: Enables reliable posting of Chinese content with quotation marks

#### Dynamic Element Reference Handling
- **Problem**: Element refs (e31, e136, e746) change between sessions
- **Solution**: Documented snapshot-first pattern
- **Impact**: Prevents "element not found" errors

### 📝 Documentation Updates

#### New Files
1. **UNICODE_ESCAPE.md** - Complete guide to Unicode escape
   - Problem statement and root cause analysis
   - Python implementation examples
   - Character support matrix
   - Troubleshooting guide

2. **QUICK_REFERENCE.md** - Copy-paste templates
   - Quick start template
   - Critical rules checklist
   - Common errors and fixes
   - Emergency recovery steps

#### Updated Files
1. **SKILL.md**
   - Added Unicode escape section
   - Updated Quick Start with Python examples
   - Updated element refs (e31, e32 vs e136, e194)
   - Enhanced error handling section
   - Updated best practices

2. **EXAMPLES.md**
   - Added Example 8: Post with Chinese quotation marks
   - Added Example 9: Technical post with emoji and hashtags
   - Added summary of best practices
   - Included real timestamps and results

3. **TROUBLESHOOTING.md**
   - Added Issue 11: "request: must be object" error
   - Added Issue 12: Element references changed
   - Added critical issues summary
   - Included recommended workflow

### 🔧 Technical Improvements

#### Unicode Escape Implementation
```python
# Before (failed)
text = "我们总说要"活在当下""
browser(action="act", request={"kind": "type", "ref": "e31", "text": text})

# After (works)
text = "我们总说要"活在当下""
escaped = text.encode('unicode_escape').decode('ascii')
browser(action="act", request={"kind": "type", "ref": "e31", "text": escaped})
```

#### Snapshot-First Pattern
```python
# Before (unreliable)
browser(action="act", request={"kind": "click", "ref": "e136"})

# After (reliable)
snapshot = browser(action="snapshot", compact=True, targetId=tab_id)
# Extract ref from snapshot
browser(action="act", request={"kind": "click", "ref": "e31"})
```

### ✅ Verified Features

- ✅ Chinese characters (汉字)
- ✅ Chinese punctuation (，。！？：；""'')
- ✅ Emoji (💪✨😊)
- ✅ Special symbols (→←↑↓)
- ✅ Hashtags (#话题#)
- ✅ Line breaks (\n)
- ✅ Mixed Chinese/English content

### 📊 Test Results

**Test Date**: 2026-03-02

| Test | Content Type | Length | Result | Time |
|------|-------------|--------|--------|------|
| 1 | Philosophical reflection | 171 chars | ✅ Success | 14:55 |
| 2 | Technical post with emoji | 114 chars | ✅ Success | 15:08 |

**Success Rate**: 100% (2/2) with Unicode escape

### 🎯 Breaking Changes

**CRITICAL**: All Chinese content must now use Unicode escape:

```python
# Old way (no longer works)
content = "中文内容"
browser(action="act", request={"kind": "type", "ref": "e31", "text": content})

# New way (required)
content = "中文内容"
escaped = content.encode('unicode_escape').decode('ascii')
browser(action="act", request={"kind": "type", "ref": "e31", "text": escaped})
```

### 📚 Migration Guide

If you have existing code:

1. **Add Unicode escape step**:
   ```python
   escaped = content.encode('unicode_escape').decode('ascii')
   ```

2. **Use escaped version in browser tool**:
   ```python
   browser(action="act", request={"kind": "type", "ref": "e31", "text": escaped})
   ```

3. **Always snapshot before operations**:
   ```python
   snapshot = browser(action="snapshot", compact=True, targetId=tab_id)
   # Extract current refs from snapshot
   ```

### 🐛 Known Issues

None currently. All critical issues resolved.

### 🔮 Future Improvements

- [ ] Automated ref extraction helper function
- [ ] Retry logic for transient failures
- [ ] Content validation before posting
- [ ] Scheduled posting support
- [ ] Multi-image upload support

### 📖 Documentation Structure

```
weibo-publisher/
├── SKILL.md                    # Main guide
├── QUICK_REFERENCE.md          # Quick start templates
├── CHANGELOG.md                # This file
├── references/
│   ├── EXAMPLES.md             # Real-world examples
│   ├── TROUBLESHOOTING.md      # Error solutions
│   └── UNICODE_ESCAPE.md       # Unicode escape guide
└── scripts/
    └── post_weibo.py           # Reference implementation
```

### 🙏 Acknowledgments

This update was driven by real-world usage and debugging on 2026-03-02, where we encountered and resolved critical issues with Chinese content posting.

---

## Version 1.0 (2026-03-01)

### Initial Release

- Basic Weibo posting via browser automation
- Support for text, emoji, hashtags
- State management with JSON file
- Examples and troubleshooting guide

### Known Issues (Fixed in v2.0)

- ❌ Chinese quotation marks cause JSON parsing errors
- ❌ Hardcoded element refs break when they change
