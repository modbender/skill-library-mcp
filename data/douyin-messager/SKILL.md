---
name: douyin-messager
description: "Douyin private messaging via browser automation. 抖音私信发送，通过浏览器自动化发送私信、获取聊天记录。Use when user needs to send 抖音私信、回复消息、查看聊天记录。Requires browser login. Triggers: 抖音, douyin, Douyin, TikTok中国, 抖音私信, douyin dm, douyin message, 抖音消息, 抖音发消息, send douyin message, 抖音聊天, douyin chat, 抖音回复, reply douyin, 获取抖音聊天记录, get douyin chat history, 抖音私信发送, send douyin dm, 给抖音用户发消息, message douyin user, 抖音私信自动化, douyin dm automation, 抖音私信工具, douyin messaging tool."
metadata: {"openclaw": {"emoji": "🎵", "requires": {"config": ["browser.enabled"]}}}
---

# 抖音私信发送 | Douyin Private Messaging

通过浏览器自动化发送抖音私信、获取聊天记录。

## ⚠️ 最大前提（必须满足）

**在执行任何操作之前，必须确认以下两点：**

1. **用户已登录抖音账号**
2. **用户已关闭 xdg-open 弹窗**（如果有）

### 标准执行流程

```
1. 打开抖音
2. 等待 2-3 秒
3. 【必须】询问用户："请确认：1) 已登录抖音账号  2) 已关闭 xdg-open 弹窗"
4. 用户确认后，继续后续操作
```

---

## ⚠️ xdg-open 系统弹窗

### 问题描述

打开抖音主页时，会触发 Linux 系统级的 `xdg-open` 弹窗：

```
Open xdg-open?
https://www.douyin.com wants to open this application.
[✓] Always allow www.douyin.com to open links of this type in the associated app
[Cancel] [Open]
```

### 关键点

| 特性 | 说明 |
|------|------|
| 弹窗类型 | Linux 系统级，非浏览器内 |
| AI 可见性 | ❌ 截图看不到 |
| AI 可操作性 | ❌ 无法操作 |
| 阻塞性 | ✅ 阻止所有浏览器操作 |
| 永久关闭 | ❌ 目前无方法 |

### 解决方案

**必须由用户手动关闭**：点击 **Cancel**（不要点 Open）

### AI 检测方法

如果出现以下情况，询问用户是否有弹窗：
- 操作突然无响应
- 截图显示页面正常但操作不执行
- 点击后没有反应

---

## 核心要点

1. **发送方式**：必须用 `type + submit`，不要用 JavaScript 操作 DOM
2. **减少快照**：快照数据量大，容易超时或断网
3. **输入框 ref**：每次页面加载都会变化，需要重新获取快照
4. **连续执行**：不要中途停止

---

## 发送私信流程

### 步骤 1：打开抖音首页

```
browser action=open profile=openclaw targetUrl=https://www.douyin.com/
```

### 步骤 2：等待页面加载

```
browser action=act request={"kind": "wait", "timeMs": 2000}
```

### 步骤 3：【必须】确认用户状态

**询问用户**："请确认：1) 已登录抖音账号  2) 已关闭 xdg-open 弹窗"

用户确认后继续。

### 步骤 4：获取快照，找到私信按钮和目标用户

```
browser action=snapshot
```

**私信按钮特征**：
```
- generic [cursor=pointer]:
    - img
    - paragraph: "私信"
```

**用户列表特征**：
```
- generic [cursor=pointer]:  <- 用户项
    - generic: "井媛"
    - generic: "置顶"
```

### 步骤 5：点击私信按钮

```
browser action=act request={"kind": "click", "ref": "<私信按钮ref>"}
```

### 步骤 6：点击目标用户

```
browser action=act request={"kind": "click", "ref": "<用户项ref>"}
```

### 步骤 7：等待 + 获取快照

```
browser action=act request={"kind": "wait", "timeMs": 500}
browser action=snapshot
```

**输入框特征**：
```
textbox [active] [ref=e3963]
```

### 步骤 8：发送消息

**✅ 正确方法**：
```
browser action=act request={"kind": "type", "ref": "<输入框ref>", "text": "消息内容", "submit": true}
```

**❌ 错误方法**（会导致乱码）：
```
browser action=act request={"kind": "evaluate", "fn": "() => { document.querySelector('...')... }"}
```

### 步骤 9：确认发送成功

```
browser action=screenshot
```

用 image 工具分析截图，确认消息出现在聊天记录中（蓝色气泡）。

---

## 获取对方回复

### 步骤 1：滚动聊天区域到底部

```javascript
browser action=act request={"kind": "evaluate", "fn": "() => {
  const containers = document.querySelectorAll('[class*=\"scroll\"]');
  containers.forEach(c => { c.scrollTop = c.scrollHeight; });
  return 'Scrolled';
}"}
```

### 步骤 2：截图或快照

```
browser action=screenshot
```

或

```
browser action=snapshot
```

### 消息特征

| 类型 | 特征 |
|------|------|
| 自己发送 | 蓝色气泡，右侧，显示时间 |
| 对方发送 | 白色/灰色气泡，左侧，显示头像和名字 |

---

## 完整示例

```
# 1. 打开抖音
browser action=open profile=openclaw targetUrl=https://www.douyin.com/

# 2. 等待加载
browser action=act request={"kind": "wait", "timeMs": 2000}

# 3. 【必须】询问用户确认登录状态和弹窗

# 4. 获取快照
browser action=snapshot

# 5. 点击私信按钮
browser action=act request={"kind": "click", "ref": "e255"}

# 6. 点击目标用户
browser action=act request={"kind": "click", "ref": "e2215"}

# 7. 等待 + 获取快照
browser action=act request={"kind": "wait", "timeMs": 500}
browser action=snapshot

# 8. 发送消息
browser action=act request={"kind": "type", "ref": "e3963", "text": "你好！", "submit": true}

# 9. 确认
browser action=screenshot
```

---

## 常见问题

### Q: 消息发送后显示乱码？

A: 不要用 JavaScript 操作 DOM。用 \`type + submit\`

### Q: 看不到对方回复？

A: 新消息可能在可视区域外。**先滚动到底部**，再截图

### Q: 输入框 ref 找不到或超时？

A: 输入框 ref 每次页面加载都会变化。重新获取快照查找 \`textbox [active]\`

### Q: 私信面板找不到？

A: 确保已登录抖音账号。未登录时私信按钮不会显示

### Q: 操作无响应？

A: 可能是 xdg-open 弹窗阻挡。询问用户是否有系统弹窗需要关闭

### Q: 快照获取失败或断网？

A: 快照数据量大，可能超时。减少快照次数，只在必要时获取

---

## 注意事项

- **消息长度限制**：500字符（超过需分段发送）
- **发送频率限制**：避免刷屏
- **私信面板是悬浮窗**：不会跳转页面
- **不要硬编码 DOM class 哈希值**：它们会变化，用文本内容或相对位置判断

---

## 经验总结

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 消息乱码 | 用 JS 操作 DOM | 用 type + submit |
| 看不到回复 | 新消息在可视区域外 | 先滚动到底部 |
| 输入框超时 | ref 每次变化 | 重新获取快照 |
| 操作无响应 | xdg-open 弹窗 | 用户手动关闭 |
| 快照断网 | 数据量大 | 减少快照次数 |

---

*抖音私信自动化 🎵*
*版本：1.0.0*
*最后更新：2026-03-02*
