# 浏览器操作模块

## 设计原则

**基于 Chirp skill，但优化 token 消耗：**
- 使用 `profile=openclaw`（稳定，不依赖 Chrome 扩展）
- 使用 DOM 操作（避免频繁 snapshot，节省 token）
- 添加人类行为模拟（避免被检测）
- 偶尔用 snapshot 验证（确保操作正确）

---

## 1. 基础配置

### 1.1 Profile 选择

```javascript
// ✓ 推荐：OpenClaw 内置浏览器
profile: "openclaw"

// ✗ 不推荐：Chrome 扩展（不稳定）
profile: "chrome"
```

**原因：**
- `openclaw`: 独立浏览器进程，100% 稳定
- `chrome`: Browser Relay 扩展，连接不稳定

### 1.2 浏览器启动

```javascript
// 启动浏览器
browser action=start profile=openclaw

// 打开页面
browser action=open profile=openclaw targetUrl="https://x.com/home"
```

---

## 2. 人类行为模拟

### 2.1 安全的点击操作

```javascript
async function humanClick(element) {
  // 1. 模拟鼠标移动
  element.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
  await new Promise(r => setTimeout(r, 100 + Math.random() * 200));
  
  // 2. 模拟鼠标悬停
  element.dispatchEvent(new MouseEvent('mousemove', {bubbles: true}));
  await new Promise(r => setTimeout(r, 50 + Math.random() * 100));
  
  // 3. 点击
  element.click();
  await new Promise(r => setTimeout(r, 200 + Math.random() * 300));
}
```

### 2.2 随机延迟

```javascript
// 正态分布随机数
function normalRandom(mean, stdDev) {
  let u = 0, v = 0;
  while (u === 0) u = Math.random();
  while (v === 0) v = Math.random();
  return mean + stdDev * Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

// 随机等待
function randomWait(min, max) {
  return new Promise(r => setTimeout(r, min + Math.random() * (max - min)));
}
```

---

## 3. 核心操作

### 3.1 点赞推文

```javascript
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": "async () => {
    // 找到推文
    const tweets = document.querySelectorAll('[data-testid=\"tweet\"]');
    const tweet = tweets[0]; // 第一条推文
    
    // 找到点赞按钮
    const likeBtn = tweet.querySelector('[data-testid=\"like\"]');
    
    // 模拟人类点击
    likeBtn.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
    await new Promise(r => setTimeout(r, 100 + Math.random() * 200));
    likeBtn.dispatchEvent(new MouseEvent('mousemove', {bubbles: true}));
    await new Promise(r => setTimeout(r, 50 + Math.random() * 100));
    likeBtn.click();
    
    return 'liked';
  }"
}
```

### 3.2 评论推文

```javascript
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": "async () => {
    // 找到推文
    const tweets = document.querySelectorAll('[data-testid=\"tweet\"]');
    const tweet = tweets[0];
    
    // 获取作者信息
    const author = tweet.querySelector('[data-testid=\"User-Name\"]')?.innerText;
    
    // 点击回复按钮
    const replyBtn = tweet.querySelector('[data-testid=\"reply\"]');
    replyBtn.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
    await new Promise(r => setTimeout(r, 100 + Math.random() * 200));
    replyBtn.click();
    
    // 等待评论框出现
    await new Promise(r => setTimeout(r, 2000 + Math.random() * 1000));
    
    // 输入评论
    const editor = document.querySelector('[data-testid=\"tweetTextarea_0\"]');
    editor.focus();
    
    const text = '评论内容'; // 从 x-engagement skill 获取
    for (const char of text) {
      document.execCommand('insertText', false, char);
      await new Promise(r => setTimeout(r, 80 + Math.random() * 40));
    }
    
    // 等待一下
    await new Promise(r => setTimeout(r, 500 + Math.random() * 500));
    
    // 发送
    const sendBtn = document.querySelector('[data-testid=\"tweetButton\"]');
    sendBtn.click();
    
    return 'comment sent to ' + author;
  }"
}
```

### 3.3 滚动页面

```javascript
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": "async () => {
    // 小滚动（200-400px）
    const scrollAmount = 200 + Math.random() * 200;
    window.scrollBy({
      top: scrollAmount,
      behavior: 'smooth'
    });
    
    await new Promise(r => setTimeout(r, 1000 + Math.random() * 500));
    return 'scrolled ' + scrollAmount + 'px';
  }"
}
```

---

## 4. Token 优化策略

### 4.1 避免频繁 snapshot

**错误做法：**
```javascript
// 每次操作前都 snapshot
browser action=snapshot profile=openclaw
browser action=act ...
browser action=snapshot profile=openclaw
```

**正确做法：**
```javascript
// 直接操作 DOM
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": "async () => {
    // 直接操作，不需要 snapshot
    document.querySelector('[data-testid=\"like\"]').click();
  }"
}

// 只在需要时 snapshot（比如读取推文内容）
browser action=snapshot profile=openclaw compact=true
```

### 4.2 使用 compact snapshot

```javascript
// ✓ 推荐：compact=true（节省 token）
browser action=snapshot profile=openclaw compact=true

// ✗ 不推荐：完整 snapshot（消耗大量 token）
browser action=snapshot profile=openclaw
```

---

## 5. 操作频率限制

### 5.1 评论间隔

**建议：**
- 最小间隔：3 分钟
- 最大间隔：6 分钟
- 随机分布：正态分布

**实现：**
```javascript
// 评论间隔：3-6分钟
const interval = 180000 + Math.random() * 180000; // 3-6分钟
await new Promise(r => setTimeout(r, interval));
```

### 5.2 每日配额

**建议：**
- 点赞：10-30 条/天
- 评论：5-15 条/天
- 关注：5-10 人/天

---

## 6. 错误处理

### 6.1 元素不存在

```javascript
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": "async () => {
    const element = document.querySelector('[data-testid=\"like\"]');
    if (!element) {
      return 'element not found';
    }
    element.click();
    return 'success';
  }"
}
```

### 6.2 页面加载失败

```javascript
// 等待页面加载
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": "async () => {
    // 等待推文加载
    let attempts = 0;
    while (attempts < 10) {
      const tweets = document.querySelectorAll('[data-testid=\"tweet\"]');
      if (tweets.length > 0) {
        return 'page loaded';
      }
      await new Promise(r => setTimeout(r, 1000));
      attempts++;
    }
    return 'timeout';
  }"
}
```

---

## 7. 完整示例

### 7.1 刷推 5 分钟

```javascript
// 1. 启动浏览器
browser action=start profile=openclaw

// 2. 打开页面
browser action=open profile=openclaw targetUrl="https://x.com/home"

// 3. 等待加载
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": "async () => {
    await new Promise(r => setTimeout(r, 5000));
    return 'loaded';
  }"
}

// 4. 点赞
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": "async () => {
    const tweet = document.querySelectorAll('[data-testid=\"tweet\"]')[0];
    const likeBtn = tweet.querySelector('[data-testid=\"like\"]');
    likeBtn.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
    await new Promise(r => setTimeout(r, 100 + Math.random() * 200));
    likeBtn.click();
    return 'liked';
  }"
}

// 5. 评论（使用 x-engagement persona）
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": "async () => {
    const tweet = document.querySelectorAll('[data-testid=\"tweet\"]')[0];
    const replyBtn = tweet.querySelector('[data-testid=\"reply\"]');
    replyBtn.click();
    await new Promise(r => setTimeout(r, 2000));
    
    const editor = document.querySelector('[data-testid=\"tweetTextarea_0\"]');
    editor.focus();
    
    const text = '妙啊'; // 从 persona 获取
    for (const char of text) {
      document.execCommand('insertText', false, char);
      await new Promise(r => setTimeout(r, 80 + Math.random() * 40));
    }
    
    await new Promise(r => setTimeout(r, 500));
    document.querySelector('[data-testid=\"tweetButton\"]').click();
    
    return 'commented';
  }"
}
```

---

## 8. 与 x-engagement 整合

### 8.1 配置读取

```javascript
// 读取配置
const config = JSON.parse(
  readFileSync('memory/daily/hotspots/.config.json')
);

// 读取 persona
const persona = readFileSync(
  `memory/daily/hotspots/personas/${config.active_persona}.md`
);
```

### 8.2 评论生成

```javascript
// 根据推文内容生成评论（使用 persona 风格）
const comment = generateComment(tweetContent, persona);

// 发送评论
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": `async () => {
    // ... 评论逻辑
    const text = '${comment}';
    // ...
  }`
}
```

---

## 9. 对比 Chirp

| 特性 | Chirp | x-engagement (改进版) |
|------|-------|----------------------|
| **Profile** | openclaw | openclaw |
| **操作方式** | DOM + snapshot | DOM（优化） |
| **Token 消耗** | 高（频繁 snapshot） | 低（偶尔 snapshot） |
| **稳定性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **人类行为** | 无 | 有（随机延迟） |
| **Persona** | 无 | 有（个性化） |
| **记忆系统** | 无 | 有（避免矛盾） |

---

## 10. 最佳实践

1. **使用 `profile=openclaw`** - 稳定
2. **避免频繁 snapshot** - 节省 token
3. **添加随机延迟** - 避免检测
4. **使用 compact snapshot** - 进一步节省
5. **偶尔验证** - 确保操作正确
6. **限制频率** - 3-6 分钟评论间隔
7. **使用 persona** - 个性化评论
8. **记录历史** - 避免自相矛盾

---

*整合自 Chirp skill + x-engagement skill*
*版本: 1.0.0*
*更新时间: 2026-03-02*
