---
name: bilibili-messager
description: "Bilibili private messaging via browser automation. B站私信发送，通过浏览器自动化发送私信、获取聊天记录。Use when user needs to send B站私信、回复消息、获取聊天记录。Requires browser login. Triggers: B站, b站, bilibili, Bilibili, 哔哩哔哩, B站私信, bilibili dm, bilibili message, B站消息, B站发消息, send bilibili message, B站聊天, bilibili chat, B站回复, reply bilibili, 获取B站聊天记录, get bilibili chat history, B站私信发送, send bilibili dm, 给B站用户发消息, message bilibili user, B站私信自动化, bilibili dm automation, 哔哩哔哩私信, 哔哩哔哩消息."
metadata: {"openclaw": {"emoji": "📺", "requires": {"config": ["browser.enabled"]}}}
---

# Bilibili Private Messaging

通过浏览器自动化发送B站私信、获取聊天记录。

## ⚠️ 执行模式

**重要：连续执行所有步骤，中途不要停止！**

## ⚠️ 减少快照

快照数据量大，可能导致网络超时。**只在必要时获取快照：**
- 第一次：打开页面后，需要找到用户
- 最后一次：发送后确认结果

**点击后不需要快照，直接发送消息！**

## 前置条件

- 用户需要在浏览器中已登录 B站账号
- 需要知道目标用户的用户名（支持部分匹配）

## 发送私信流程

### 步骤 1：打开页面

```
browser action=open targetUrl=https://message.bilibili.com/#/whisper
```

### 步骤 2：获取快照，找到用户

```
browser action=snapshot
```

在快照中找到目标用户（按用户名部分匹配），记录 ref。

### 步骤 3：点击进入对话

```
browser action=act request={"kind": "click", "ref": "<用户ref>"}
```

### 步骤 4：直接发送消息（不要获取快照！）

**点击后立即用 JavaScript 发送，不要再获取快照：**

```javascript
() => {
  const inputArea = document.querySelector('[contenteditable="true"]');
  if (inputArea) {
    inputArea.textContent = '消息内容';
    inputArea.dispatchEvent(new InputEvent('input', { bubbles: true }));
    const sendBtn = document.evaluate(
      "//div[contains(text(), '发送')]", 
      document, 
      null, 
      XPathResult.FIRST_ORDERED_NODE_TYPE, 
      null
    ).singleNodeValue;
    if (sendBtn) sendBtn.click();
    return 'Message sent';
  }
  return 'Input not found';
}
```

### 步骤 5：获取快照确认发送成功

```
browser action=snapshot
```

确认消息已出现在聊天记录中，然后向用户报告结果。

## 获取聊天记录

### ⚠️ 重要：确定发送方的方法

**B站私信的 DOM class 哈希值（如 `_MsgIsMe_o7f0t_9`）可能因用户/会话不同而变化，不能硬编码！**

**推荐方法：通过头像位置判断**

1. 先获取快照或截图，观察消息布局
2. 左侧头像 = 对方发送的消息
3. 右侧头像 = 自己发送的消息

### 通过头像位置提取聊天记录

```javascript
() => {
  const main = document.querySelector('main');
  if (!main) return 'No main';

  const msgBlocks = main.querySelectorAll('[class*="_Msg_"]');
  const messages = [];

  msgBlocks.forEach(block => {
    const text = block.textContent.trim();
    
    // 提取日期
    const dateMatch = text.match(/(202[56]年\d+月\d+日 \d+:\d+|今天 \d+:\d+)/);
    
    if (dateMatch) {
      const date = dateMatch[1];
      let content = text.replace(dateMatch[0], '').trim();
      content = content.replace(/^(\d+:\d+)?/, '').trim();
      
      if (content && content.length > 1) {
        // 通过头像位置判断发送方
        const img = block.querySelector('img');
        let sender = '对方'; // 默认
        
        if (img) {
          const imgRect = img.getBoundingClientRect();
          const blockRect = block.getBoundingClientRect();
          // 如果头像在右侧，是自己发送的
          if (imgRect.left > blockRect.left + blockRect.width / 2) {
            sender = '自己';
          }
        }
        
        messages.push({
          date,
          sender,
          content: content.substring(0, 200)
        });
      }
    }
  });

  // 去重
  const seen = new Set();
  return messages.filter(msg => {
    const key = msg.date + msg.content.substring(0, 50);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}
```

### 备用方法：通过 class 名称包含 "Me" 判断

如果 class 名称包含 "Me" 或 "Self" 等关键词，可以辅助判断：

```javascript
const className = block.className;
const isMe = className.toLowerCase().includes('me') || 
             className.toLowerCase().includes('self');
```

**但要注意：** 哈希值部分可能变化，不要依赖完整的 class 名！

### 滚动加载历史记录

B站私信使用懒加载，需要滚动才能加载更早的记录：

```javascript
() => {
  // 查找滚动容器（通过 overflow 样式）
  const allElements = document.querySelectorAll('*');
  for (const el of allElements) {
    const style = window.getComputedStyle(el);
    if ((style.overflow === 'auto' || style.overflowY === 'auto') && 
        el.scrollHeight > el.clientHeight &&
        el.closest('main')) {
      el.scrollTop = 0;
      return 'Scrolled container: ' + el.className;
    }
  }
  return 'No scroll container found';
}
```

滚动后等待 1-2 秒让内容加载，再获取快照或提取消息。

## 注意事项

- 消息长度限制：500字符（超过需分段发送）
- 发送频率有限制，避免刷屏
- 如果找不到用户，先向用户确认用户名是否正确
- 获取历史记录时可能需要多次滚动触发懒加载
- **不要硬编码 DOM class 的哈希值**，它们可能变化！用头像位置或关键词判断更可靠
