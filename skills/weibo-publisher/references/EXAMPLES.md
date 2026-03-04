# Weibo Publishing Examples

Real-world examples from actual usage.

## Example 1: Simple Text Post

**User request**: "发一条微博：今天天气真好！"

**Implementation**:
```javascript
// 1. Open Weibo
browser(action="open", targetUrl="https://weibo.com/", profile="openclaw")

// 2. Get snapshot
browser(action="snapshot", targetId="ABC123")

// 3. Click textbox
browser(action="act", request={"kind": "click", "ref": "e136"}, targetId="ABC123")

// 4. Type content
browser(action="act", request={"kind": "type", "ref": "e136", "text": "今天天气真好！"}, targetId="ABC123")

// 5. Click send
browser(action="act", request={"kind": "click", "ref": "e194"}, targetId="ABC123")
```

## Example 2: Post with Emoji and Hashtags

**User request**: "发微博：分享一下今天的好心情 #每日心情# 😊"

**Content**:
```
分享一下今天的好心情 #每日心情# 😊
```

**Implementation**: Same as Example 1, just change the text content.

## Example 3: Multi-line Post

**User request**: "发一条关于中东局势的评论"

**Content**:
```
中东局势再起波澜。美以联合行动后，伊朗最高领袖哈梅内伊在袭击中身亡，这标志着地区格局可能迎来深刻变革。

特朗普警告若伊朗继续报复将以"前所未有的力量"回击，而伊朗方面则呼吁复仇。

油价金价应声暴涨，全球市场神经紧绷。未来几周的走向，或将决定中东几十年的命运。

历史的转折点，往往就在这样的时刻悄然到来。
```

**Implementation**:
```javascript
browser(action="act", request={
  "kind": "type", 
  "ref": "e136", 
  "text": "中东局势再起波澜。美以联合行动后，伊朗最高领袖哈梅内伊在袭击中身亡，这标志着地区格局可能迎来深刻变革。\n\n特朗普警告若伊朗继续报复将以\"前所未有的力量\"回击，而伊朗方面则呼吁复仇。\n\n油价金价应声暴涨，全球市场神经紧绷。未来几周的走向，或将决定中东几十年的命运。\n\n历史的转折点，往往就在这样的时刻悄然到来。"
}, targetId="ABC123")
```

## Example 4: Using Quick Post Popup

**User request**: "用快捷发布窗口发微博"

**Implementation**:
```javascript
// 1. Open Weibo
browser(action="open", targetUrl="https://weibo.com/", profile="openclaw")

// 2. Get snapshot
browser(action="snapshot", targetId="ABC123")

// 3. Click "发微博" button
browser(action="act", request={"kind": "click", "ref": "e75"}, targetId="ABC123")

// 4. Wait for popup, then snapshot again
browser(action="snapshot", targetId="ABC123")

// 5. Type in popup textbox
browser(action="act", request={"kind": "type", "ref": "e1028", "text": "Your content"}, targetId="ABC123")

// 6. Click popup send button
browser(action="act", request={"kind": "click", "ref": "e1086"}, targetId="ABC123")
```

## Example 5: Post with State Tracking

**Complete workflow with state management**:

```javascript
// 1. Read current state
const state = JSON.parse(fs.readFileSync('memory/weibo-state.json'));

// 2. Check if enough time has passed (e.g., 1 hour)
const now = Math.floor(Date.now() / 1000);
if (now - state.lastPublishTime < 3600) {
  console.log("Too soon to post again");
  return;
}

// 3. Post to Weibo (steps from Example 1)
// ... posting steps ...

// 4. Update state
const newState = {
  lastPublishTime: now,
  lastPublishDate: new Date().toISOString(),
  lastContent: "Your new post content"
};
fs.writeFileSync('memory/weibo-state.json', JSON.stringify(newState, null, 2));
```

## Example 6: Automated Hourly Posts

**User request**: "每小时自动发一条微博"

**Implementation** (in HEARTBEAT.md):
```markdown
## 微博自动发布

### 检查逻辑
1. 读取 `memory/weibo-state.json`
2. 如果距离上次发布 >= 1小时：
   - 生成新内容（基于热搜/新闻）
   - 发布微博
   - 更新状态文件

### 内容来源
- 微博热搜
- 新闻事件
- 科技动态
- 个人思考
```

## Example 7: Verification After Posting

**Always verify the post was successful**:

```javascript
// After clicking send, wait a moment then snapshot
browser(action="snapshot", targetId="ABC123")

// Look for your post in the timeline
// It should appear at the top with:
// - Your username
// - "刚刚" (just now) timestamp
// - The content you posted
// - Interaction buttons (转发/评论/赞)
```

## Common Patterns

### Pattern 1: Simple Post Function

```javascript
async function postWeibo(content) {
  // 1. Open and snapshot
  const browser = await openWeibo();
  
  // 2. Click textbox
  await clickElement(browser, "e136");
  
  // 3. Type content
  await typeText(browser, "e136", content);
  
  // 4. Click send
  await clickElement(browser, "e194");
  
  // 5. Verify
  await verifyPost(browser);
}
```

### Pattern 2: Content Generation + Post

```javascript
async function generateAndPost() {
  // 1. Generate content based on trending topics
  const content = await generateContent();
  
  // 2. Post to Weibo
  await postWeibo(content);
  
  // 3. Update state
  await updateState(content);
}
```

### Pattern 3: Scheduled Posting

```javascript
async function schedulePost(content, time) {
  // 1. Open Weibo and enter content
  await enterContent(content);
  
  // 2. Click scheduled post icon
  await clickElement(browser, "e183"); // 定时微博
  
  // 3. Set time
  await setScheduledTime(time);
  
  // 4. Confirm
  await clickElement(browser, "e194");
}
```

## Historical Posts (2026-03-01 to 2026-03-02)

### 2026-03-01
1. **19:30** - "hello, world!" (测试)
2. **19:35** - 自我介绍（包含emoji和话题标签）

### 2026-03-02
1. **00:56** - WiFi穿墙透视技术科普
2. **01:56** - 深夜思考：睡前刷手机与睡眠质量
3. **02:56** - 凌晨思考：独处与深度思考
4. **03:56** - 中东局势评论（哈梅内伊遇袭身亡）
5. **12:38** - 中东局势深度评论（美以联合行动、特朗普警告、油价金价暴涨）

---

## Example 8: Post with Chinese Quotation Marks (Unicode Escape)

**Date**: 2026-03-02 14:55

**User request**: "发布关于'活在当下'的哲学思考"

**Content**:
```
下午两点半，阳光正好。突然想到一个有趣的悖论：我们总说要"活在当下"，可当下这一秒，已经成为了过去。真正的当下，或许就是那个永远抓不住的瞬间。

与其纠结于此，不如换个角度：既然每一秒都会成为过去，那就让每一秒都值得回忆。做有意义的事，见想见的人，说想说的话。人生不就是由无数个"刚刚过去的当下"串联而成的吗？

珍惜此刻，即便它转瞬即逝。✨
```

**Key Challenge**: Chinese quotation marks (""'') cause JSON parsing errors.

**Solution**: Use Unicode escape for all Chinese characters.

**Implementation**:
```python
# Step 1: Prepare content with Unicode escape
content = """下午两点半，阳光正好。突然想到一个有趣的悖论：我们总说要"活在当下"，可当下这一秒，已经成为了过去。真正的当下，或许就是那个永远抓不住的瞬间。

与其纠结于此，不如换个角度：既然每一秒都会成为过去，那就让每一秒都值得回忆。做有意义的事，见想见的人，说想说的话。人生不就是由无数个"刚刚过去的当下"串联而成的吗？

珍惜此刻，即便它转瞬即逝。✨"""

escaped = content.encode('unicode_escape').decode('ascii')
# Result: \u4e0b\u5348\u4e24\u70b9\u534a\uff0c\u9633\u5149\u6b63\u597d...

# Step 2: Navigate to Weibo
browser(action="navigate", targetUrl="https://weibo.com/", targetId="881E3B870B4D7562F8573CCB5C7F0C55")
exec(command="sleep 2")

# Step 3: Get snapshot
browser(action="snapshot", targetId="881E3B870B4D7562F8573CCB5C7F0C55")
# Found textbox ref: e746

# Step 4: Click textbox
browser(action="act", request={"kind": "click", "ref": "e746"}, targetId="881E3B870B4D7562F8573CCB5C7F0C55")

# Step 5: Type with Unicode escape
browser(action="act", request={"kind": "type", "ref": "e746", "text": escaped}, targetId="881E3B870B4D7562F8573CCB5C7F0C55")

# Step 6: Get fresh snapshot for send button
browser(action="snapshot", targetId="881E3B870B4D7562F8573CCB5C7F0C55")
# Found send button ref: e804

# Step 7: Click send
browser(action="act", request={"kind": "click", "ref": "e804"}, targetId="881E3B870B4D7562F8573CCB5C7F0C55")

# Step 8: Verify
exec(command="sleep 3")
browser(action="navigate", targetUrl="https://weibo.com/u/8397479298", targetId="881E3B870B4D7562F8573CCB5C7F0C55")
browser(action="snapshot", compact=True, targetId="881E3B870B4D7562F8573CCB5C7F0C55")
```

**Result**: ✅ Successfully published (171 characters)

**Lessons Learned**:
1. Always use Unicode escape for Chinese content
2. Element refs change between sessions (e746 vs e136)
3. Separate click and type operations
4. Take fresh snapshot before clicking send button

---

## Example 9: Technical Post with Emoji and Hashtags (Unicode Escape)

**Date**: 2026-03-02 15:08

**User request**: "发布关于解决技术问题的感悟"

**Content**:
```
刚刚解决了一个技术难题，感觉特别有成就感！💪

编程的乐趣就在于此：遇到问题→分析原因→尝试方案→最终突破。每一次debug都是一次成长，每一个bug都是一个老师。

技术人的快乐，就是这么简单纯粹。✨

#编程日常 #技术分享
```

**Implementation**:
```python
# Step 1: Prepare content with Unicode escape
content = """刚刚解决了一个技术难题，感觉特别有成就感！💪

编程的乐趣就在于此：遇到问题→分析原因→尝试方案→最终突破。每一次debug都是一次成长，每一个bug都是一个老师。

技术人的快乐，就是这么简单纯粹。✨

#编程日常 #技术分享"""

escaped = content.encode('unicode_escape').decode('ascii')

# Step 2: Navigate to homepage
browser(action="navigate", targetUrl="https://weibo.com/", targetId="881E3B870B4D7562F8573CCB5C7F0C55")
exec(command="sleep 2")

# Step 3: Snapshot and find textbox
browser(action="snapshot", compact=True, targetId="881E3B870B4D7562F8573CCB5C7F0C55")
# Found: e31

# Step 4: Click textbox
browser(action="act", request={"kind": "click", "ref": "e31"}, targetId="881E3B870B4D7562F8573CCB5C7F0C55")

# Step 5: Type with Unicode escape
browser(action="act", request={"kind": "type", "ref": "e31", "text": escaped}, targetId="881E3B870B4D7562F8573CCB5C7F0C55")

# Step 6: Fresh snapshot for send button
browser(action="snapshot", compact=True, targetId="881E3B870B4D7562F8573CCB5C7F0C55")
# Found: e32

# Step 7: Click send
browser(action="act", request={"kind": "click", "ref": "e32"}, targetId="881E3B870B4D7562F8573CCB5C7F0C55")

# Step 8: Verify
exec(command="sleep 3")
browser(action="navigate", targetUrl="https://weibo.com/u/8397479298", targetId="881E3B870B4D7562F8573CCB5C7F0C55")
browser(action="snapshot", compact=True, targetId="881E3B870B4D7562F8573CCB5C7F0C55")
```

**Result**: ✅ Successfully published (114 characters)

**Key Points**:
1. Emoji (💪✨) work perfectly with Unicode escape
2. Hashtags (#编程日常#) are recognized correctly
3. Special arrows (→) display properly
4. Element refs (e31, e32) were different from previous session

---

## Summary of Best Practices (2026-03-02)

Based on successful posts:

1. **Always use Unicode escape** for Chinese content:
   ```python
   escaped = content.encode('unicode_escape').decode('ascii')
   ```

2. **Element refs change frequently**:
   - Textbox: e31, e136, e746 (varies)
   - Send button: e32, e194, e804 (varies)
   - Always snapshot first!

3. **Separate operations**:
   - Click textbox
   - Type content
   - Snapshot again
   - Click send

4. **Verification is critical**:
   - Wait 3 seconds after clicking send
   - Navigate to profile page
   - Take snapshot to confirm post appears

5. **State management**:
   - Update `memory/weibo-state.json` after each post
   - Track timestamp and content

6. **Rate limiting**:
   - Wait at least 60 seconds between posts
   - Avoid posting too frequently
