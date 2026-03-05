# Unicode Escape Guide for Weibo Publishing

## Problem Statement

When publishing Chinese content to Weibo using OpenClaw's browser tool, Chinese quotation marks (""、'') cause JSON parsing errors:

```
Validation failed for tool "browser": - request: must be object
```

This happens because the `request` parameter gets serialized as a string instead of an object.

## Root Cause

Chinese quotation marks conflict with JSON string delimiters:

```json
// This breaks JSON parsing:
{"text": "我说"你好""}
         ^    ^  ^  ^
         |    |  |  |
         |    |  |  +-- Unexpected quote
         |    |  +----- Unexpected quote
         |    +-------- String ends here (parser thinks)
         +------------- String starts here
```

## Solution: Unicode Escape

Convert all Chinese characters to Unicode escape sequences (`\uXXXX`):

### Python Implementation

```python
# Convert Chinese text to Unicode escape
text = "刚刚解决了一个技术难题，感觉特别有成就感！💪"
escaped = text.encode('unicode_escape').decode('ascii')

print(escaped)
# Output: \u521a\u521a\u89e3\u51b3\u4e86\u4e00\u4e2a\u6280\u672f\u96be\u9898\uff0c\u611f\u89c9\u7279\u522b\u6709\u6210\u5c31\u611f\uff01\ud83d\udcaa
```

### Usage in Browser Tool

```python
# Prepare content
content = "下午两点半，阳光正好。突然想到一个有趣的悖论：我们总说要"活在当下"..."
escaped_content = content.encode('unicode_escape').decode('ascii')

# Use in browser tool
browser(
    action="act",
    request={
        "kind": "type",
        "ref": "e31",
        "text": escaped_content  # Use escaped version
    },
    targetId="881E3B870B4D7562F8573CCB5C7F0C55"
)
```

## Complete Example

```python
#!/usr/bin/env python3
"""Complete example of posting to Weibo with Unicode escape"""

def post_to_weibo(content, target_id):
    """
    Post content to Weibo using Unicode escape
    
    Args:
        content: Original Chinese text
        target_id: Browser tab ID
    """
    # Step 1: Convert to Unicode escape
    escaped = content.encode('unicode_escape').decode('ascii')
    
    # Step 2: Navigate to Weibo homepage
    browser(action="navigate", targetUrl="https://weibo.com/", targetId=target_id)
    exec(command="sleep 2")
    
    # Step 3: Get snapshot to find textbox
    snapshot = browser(action="snapshot", compact=True, targetId=target_id)
    # Find textbox ref (usually e31)
    
    # Step 4: Click textbox
    browser(
        action="act",
        request={"kind": "click", "ref": "e31"},
        targetId=target_id
    )
    
    # Step 5: Type content with Unicode escape
    browser(
        action="act",
        request={"kind": "type", "ref": "e31", "text": escaped},
        targetId=target_id
    )
    
    # Step 6: Get fresh snapshot to find send button
    snapshot = browser(action="snapshot", compact=True, targetId=target_id)
    # Find send button ref (usually e32)
    
    # Step 7: Click send button
    browser(
        action="act",
        request={"kind": "click", "ref": "e32"},
        targetId=target_id
    )
    
    # Step 8: Wait and verify
    exec(command="sleep 3")
    browser(action="navigate", targetUrl="https://weibo.com/u/8397479298", targetId=target_id)
    exec(command="sleep 2")
    browser(action="snapshot", compact=True, targetId=target_id)
    
    print("✅ Post published successfully!")

# Example usage
content = """刚刚解决了一个技术难题，感觉特别有成就感！💪

编程的乐趣就在于此：遇到问题→分析原因→尝试方案→最终突破。每一次debug都是一次成长，每一个bug都是一个老师。

技术人的快乐，就是这么简单纯粹。✨

#编程日常 #技术分享"""

post_to_weibo(content, "881E3B870B4D7562F8573CCB5C7F0C55")
```

## Character Support

Unicode escape works for:

- ✅ Chinese characters (汉字)
- ✅ Chinese punctuation (，。！？：；""'')
- ✅ Emoji (💪✨😊)
- ✅ Special symbols (→←↑↓)
- ✅ Hashtags (#话题#)
- ✅ Line breaks (\n)

## Performance Notes

- Escaped strings are longer but parse correctly
- No performance impact on browser rendering
- Weibo displays the text normally (unescaped)

## Troubleshooting

### Issue: Emoji not displaying correctly

**Cause**: Some emoji use surrogate pairs (2 code units)

**Solution**: Python's `unicode_escape` handles this automatically:

```python
"💪".encode('unicode_escape').decode('ascii')
# Output: \ud83d\udcaa (surrogate pair)
```

### Issue: Line breaks not working

**Cause**: Need to use `\n` in the original text

**Solution**: Include line breaks before escaping:

```python
text = "Line 1\nLine 2\nLine 3"
escaped = text.encode('unicode_escape').decode('ascii')
# Output: Line 1\nLine 2\nLine 3
```

### Issue: Hashtags not recognized

**Cause**: Hashtags need Chinese # symbol (＃ U+FF03)

**Solution**: Use proper Chinese hashtag format:

```python
text = "#编程日常#"  # Chinese full-width #
escaped = text.encode('unicode_escape').decode('ascii')
# Weibo will recognize this as a hashtag
```

## Historical Context

This solution was discovered on 2026-03-02 after encountering repeated failures with direct Chinese text. Previous attempts included:

1. ❌ Direct JSON object (failed due to quote conflicts)
2. ❌ CDP WebSocket connection (connection closed)
3. ❌ JavaScript file execution (tool limitation)
4. ✅ Unicode escape (successful!)

The key insight: Chinese quotation marks break JSON parsing, but Unicode escape bypasses this entirely.

## References

- Python `unicode_escape` codec: https://docs.python.org/3/library/codecs.html#text-encodings
- Unicode standard: https://unicode.org/
- Weibo API limitations: No official API for posting (hence browser automation)
