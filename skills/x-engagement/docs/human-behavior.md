# 人类行为模拟规范

## 核心原则

**不追求完美，追求"足够像真人"。**

真人行为特点：
- 有随机性
- 有停顿和发呆
- 有失误和修正
- 有节奏变化

---

## 1. 随机时间生成器

### 1.1 正态分布随机数

**为什么用正态分布：**
- 真人行为不是均匀分布
- 大部分时间在均值附近
- 偶尔极端（很快或很慢）

**实现：**

```javascript
const normalRandom = (mean, stdDev) => {
  let u = 0, v = 0;
  while (u === 0) u = Math.random();
  while (v === 0) v = Math.random();
  return mean + stdDev * Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
};
```

### 1.2 阅读时间

**真人阅读特点：**
- 短推文：1-2秒
- 中等推文：3-5秒
- 长推文：5-10秒
- 偶尔快速略过（0.5秒）
- 偶尔仔细阅读（10秒+）

**实现：**

```javascript
const readingTime = (textLength) => {
  const baseTime = Math.max(1500, normalRandom(3500, 1000));
  
  // 根据文本长度调整
  if (textLength < 50) return baseTime * 0.5;
  if (textLength > 200) return baseTime * 1.5;
  return baseTime;
};
```

### 1.3 停顿/发呆

**真人特点：**
- 85% 正常阅读
- 15% 发呆（10-30秒）

**实现：**

```javascript
const pauseTime = () => {
  if (Math.random() > 0.85) {
    return 10000 + Math.random() * 20000; // 10-30秒
  }
  return 0;
};
```

### 1.4 操作间隔

**不同操作的间隔：**

| 操作 | 间隔 | 说明 |
|------|------|------|
| 滚动 | 1-3秒 | 阅读时间 |
| 点赞 | 0.5-2秒 | 决策+点击 |
| 评论 | 3-6分钟 | 重要！避免机器人检测 |
| 关注 | 2-5秒 | 阅读主页+决策 |

**实现：**

```javascript
const actionDelay = {
  scroll: () => 1000 + Math.random() * 2000,
  like: () => 500 + Math.random() * 1500,
  comment: () => 180000 + Math.random() * 180000, // 3-6分钟
  follow: () => 2000 + Math.random() * 3000
};
```

---

## 2. 人类滚动模式

### 2.1 三种滚动模式

**真人特点：**
- 小滚动（30-50%）：30%
- 中滚动（50-80%）：50%
- 大滚动（80-100%）：20%

**实现：**

```javascript
const humanScroll = () => {
  const patterns = [
    { ratio: 0.3 + Math.random() * 0.2, name: 'small' },
    { ratio: 0.5 + Math.random() * 0.3, name: 'medium' },
    { ratio: 0.8 + Math.random() * 0.2, name: 'large' }
  ];
  
  const weights = [0.3, 0.5, 0.2];
  const rand = Math.random();
  let cumulative = 0, chosen = patterns[1];
  
  for (let i = 0; i < weights.length; i++) {
    cumulative += weights[i];
    if (rand < cumulative) {
      chosen = patterns[i];
      break;
    }
  }
  
  window.scrollBy({
    top: window.innerHeight * chosen.ratio,
    behavior: "smooth"
  });
  
  return chosen.name;
};
```

### 2.2 滚动后微调

**真人特点：**
- 30% 概率滚完再微调
- 20% 概率回滚一点

**实现：**

```javascript
// 滚动后微调
if (Math.random() > 0.7) {
  setTimeout(() => {
    window.scrollBy({
      top: 50 - Math.random() * 100,
      behavior: "smooth"
    });
  }, 500 + Math.random() * 300);
}

// 回滚
if (Math.random() > 0.8) {
  setTimeout(() => {
    window.scrollBy({
      top: -100 - Math.random() * 200,
      behavior: "smooth"
    });
  }, 800 + Math.random() * 400);
}
```

---

## 3. 鼠标轨迹模拟

### 3.1 不点正中心

**真人特点：**
- 不会每次都点正中心
- 有随机偏移

**实现：**

```javascript
const humanClick = (element) => {
  if (!element) return "not found";
  
  const rect = element.getBoundingClientRect();
  
  // 随机偏移（30-70% 范围）
  const targetX = rect.left + rect.width * (0.3 + Math.random() * 0.4);
  const targetY = rect.top + rect.height * (0.3 + Math.random() * 0.4);
  
  // 模拟鼠标事件
  element.dispatchEvent(new MouseEvent('mouseover', {
    bubbles: true,
    clientX: targetX,
    clientY: targetY
  }));
  
  // 短暂延迟后点击
  setTimeout(() => {
    element.dispatchEvent(new MouseEvent('mousedown', {
      bubbles: true,
      clientX: targetX,
      clientY: targetY
    }));
    
    element.dispatchEvent(new MouseEvent('mouseup', {
      bubbles: true,
      clientX: targetX,
      clientY: targetY
    }));
    
    element.click();
  }, 50 + Math.random() * 100);
  
  return "clicked";
};
```

---

## 4. 打字模拟

### 4.1 逐字输入

**真人特点：**
- 每个字间隔 50-200ms
- 偶尔停顿思考
- 偶尔打错删除

**实现：**

```javascript
const humanType = async (element, text) => {
  element.focus();
  
  const chars = text.split('');
  for (let i = 0; i < chars.length; i++) {
    // 偶尔停顿（5%概率）
    if (Math.random() > 0.95) {
      await sleep(500 + Math.random() * 1000);
    }
    
    // 输入字符
    element.value += chars[i];
    element.dispatchEvent(new Event("input", { bubbles: true }));
    
    // 随机间隔
    await sleep(50 + Math.random() * 150);
  }
};
```

### 4.2 OpenClaw Browser Relay 打字

**使用 slowly: true 参数：**

```
browser action=act profile=chrome request={"kind": "type", "ref": "e123", "text": "内容", "slowly": true}
```

**这个参数会自动模拟真人打字。**

---

## 5. 频率限制

### 5.1 每小时上限

| 操作 | 每小时上限 | 说明 |
|------|-----------|------|
| 关注 | 10 | 新号建议 5 以内 |
| 点赞 | 30 | 分散在整个会话 |
| 评论 | 10 | 不要连续发 |
| 发推 | 5 | 原创内容 |
| 滚动 | 100 | 自然浏览 |

### 5.2 频率检查

**实现：**

```javascript
const checkRateLimit = (action) => {
  const limits = {
    follow: { max: 10, window: 3600000 },
    like: { max: 30, window: 3600000 },
    reply: { max: 10, window: 3600000 },
    tweet: { max: 5, window: 3600000 },
    scroll: { max: 100, window: 3600000 }
  };
  
  const key = `xagent_${action}`;
  const now = Date.now();
  const limit = limits[action];
  
  let history = JSON.parse(localStorage.getItem(key) || '[]');
  history = history.filter(t => now - t < limit.window);
  
  if (history.length >= limit.max) {
    return { allowed: false, waitMs: limit.window - (now - history[0]) };
  }
  
  history.push(now);
  localStorage.setItem(key, JSON.stringify(history));
  return { allowed: true };
};
```

---

## 6. 评论间隔（重要）

### 6.1 为什么重要

**Twitter 反作弊机制：**
- 连续发多条评论 → 机器人特征
- 需要间隔 3-6 分钟

### 6.2 实现方式

**评论流程：**

```
1. 发表评论
2. 等待 3-6 分钟（随机）
3. 继续下一条评论
```

**代码：**

```javascript
const commentInterval = () => {
  return 180000 + Math.random() * 180000; // 3-6分钟
};

// 使用
await postComment(text);
await sleep(commentInterval());
// 继续下一条
```

---

## 7. 会话时间限制

### 7.1 每天上限

**真人特点：**
- 不会24小时在线
- 有明显的使用时段

**建议：**
- 每天总时长 < 2小时
- 分散在多个时段

### 7.2 时段分布

**建议时段：**
- 早上 8-10点
- 中午 12-14点
- 晚上 20-22点

**避免：**
- 凌晨 2-6点（不自然）

---

## 8. 完整人类浏览循环

### 8.1 单次循环

```javascript
const humanBrowseAction = async () => {
  const results = {
    action: null,
    tweets: [],
    nextDelay: 0
  };
  
  // 1. 滚动
  results.action = humanScroll();
  
  // 2. 等待加载
  await sleep(500 + Math.random() * 500);
  
  // 3. 获取可见推文
  const tweets = document.querySelectorAll('[data-testid="tweet"]');
  results.tweets = Array.from(tweets).slice(-3).map(t => ({
    author: t.querySelector('[data-testid="User-Name"]')?.innerText?.split('\n')[0],
    text: t.querySelector('[data-testid="tweetText"]')?.innerText?.slice(0, 80),
    time: t.querySelector('time')?.getAttribute('datetime')
  }));
  
  // 4. 计算下次延迟
  const avgTextLength = results.tweets.reduce((sum, t) => sum + (t.text?.length || 0), 0) / results.tweets.length;
  results.nextDelay = readingTime(avgTextLength) + pauseTime();
  
  return results;
};
```

### 8.2 多次循环

```javascript
const browseLoop = async (count) => {
  for (let i = 0; i < count; i++) {
    const result = await humanBrowseAction();
    console.log(`滚动 ${i+1}/${count}: ${result.action}`);
    console.log(`推文: ${result.tweets.map(t => t.author).join(', ')}`);
    console.log(`等待: ${result.nextDelay}ms`);
    
    await sleep(result.nextDelay);
  }
};
```

---

## 9. 反检测清单

### 9.1 必须做的

| 项目 | 说明 |
|------|------|
| ✓ 随机延迟 | 每个操作后随机等待 |
| ✓ 平滑滚动 | `behavior: "smooth"` |
| ✓ 频率限制 | 严格遵守每小时上限 |
| ✓ 评论间隔 | 3-6分钟 |
| ✓ 慢速打字 | `slowly: true` |
| ✓ 鼠标模拟 | mouseover + mousedown + mouseup |

### 9.2 不要做的

| 禁止 | 原因 |
|------|------|
| ✗ 固定延迟 | 机器人特征 |
| ✗ 批量操作 | 一眼假 |
| ✗ 快速连续点击 | 不像人类 |
| ✗ 每天超2小时 | 太活跃 |
| ✗ 凌晨操作 | 不自然 |

---

## 10. 环境一致性

**保持一致：**
- 同一台电脑
- 同一个 Chrome profile
- 同一个 IP
- 同一个时区
- 同一个屏幕分辨率

**不要：**
- 切换 VPN
- 使用无头模式
- 频繁更换设备

---

*文档版本: 1.0*
*更新: 2026-03-02*
