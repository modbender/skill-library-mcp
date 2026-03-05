# 评论规则（重要！）

## ⚠️ 绝对禁止的错误

### 1. 错误的页面

**❌ 错误：**
- 在 Following 的 Popular 页面评论
- 在 For You 页面评论

**✓ 正确：**
- **只在 Following 的 Recent 页面评论**

**原因：**
- Popular 页面是热门推文，评论已经很多
- Recent 页面是最新推文，评论少，更自然
- For You 页面是算法推荐，不是关注的人

**操作流程：**
```
1. 打开 https://x.com/home
2. 点击 "Following" 标签
3. 确保是 "Recent"（不是 Popular）
4. 开始评论
```

---

### 2. 重复评论同一推文

**❌ 错误：**
- 在同一条推文下评论两次
- 在同一个博主的同一条推文下重复评论

**✓ 正确：**
- **每次评论前检查历史**
- 确保没有评论过这条推文
- 确保没有评论过这个博主

**检查流程：**
```
1. 读取 memory/daily/hotspots/history/comments/[日期].json
2. 检查是否已评论过这个博主
3. 检查是否已评论过这条推文
4. 如果已评论，跳过这条推文
```

**示例：**
```json
{
  "2026-03-02": [
    {
      "author": "@siantgirl",
      "tweet_id": "2028297844399153394",
      "content": "确实，小红书流量太少了。B站可以试试",
      "time": "2026-03-02 13:34:00"
    }
  ]
}
```

---

## 正确的评论流程

### Step 1: 打开正确的页面

```javascript
// 1. 打开首页
browser action=open profile=openclaw targetUrl="https://x.com/home"

// 2. 点击 Following 标签
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": "async () => {
    const followingTab = document.querySelector('[href=\"/home\"]');
    followingTab?.click();
    await new Promise(r => setTimeout(r, 2000));
    
    // 确保是 Recent（不是 Popular）
    const recentBtn = document.querySelector('[href=\"/home?tab=recent\"]');
    if (recentBtn) {
      recentBtn.click();
      await new Promise(r => setTimeout(r, 2000));
    }
    
    return 'on Following Recent page';
  }"
}
```

### Step 2: 读取评论历史

```javascript
// 读取今天的评论历史
const today = new Date().toISOString().split('T')[0]; // 2026-03-02
const historyFile = `memory/daily/hotspots/history/comments/${today}.json`;

let history = [];
try {
  history = JSON.parse(readFileSync(historyFile));
} catch (e) {
  // 文件不存在，创建新文件
  history = [];
}
```

### Step 3: 选择推文并检查

```javascript
browser action=act profile=openclaw request={
  "kind": "evaluate",
  "fn": "async () => {
    const tweets = document.querySelectorAll('[data-testid=\"tweet\"]');
    
    for (const tweet of tweets) {
      const author = tweet.querySelector('[data-testid=\"User-Name\"]')?.innerText;
      const tweetLink = tweet.querySelector('a[href*=\"/status/\"]');
      const tweetId = tweetLink?.href.match(/status\\/(\\d+)/)?.[1];
      
      // 返回推文信息
      return {
        author: author,
        tweetId: tweetId,
        content: tweet.querySelector('[data-testid=\"tweetText\"]')?.innerText
      };
    }
    
    return null;
  }"
}
```

### Step 4: 检查历史并评论

```javascript
// 检查是否已评论
const alreadyCommented = history.some(h => 
  h.author === tweet.author || 
  h.tweet_id === tweet.tweetId
);

if (alreadyCommented) {
  // 跳过这条推文
  continue;
}

// 生成评论
const comment = generateComment(tweet.content, persona);

// 发表评论
await postComment(tweet, comment);

// 记录到历史
history.push({
  author: tweet.author,
  tweet_id: tweet.tweetId,
  content: comment,
  time: new Date().toISOString()
});

writeFileSync(historyFile, JSON.stringify(history, null, 2));
```

---

## 检查清单

**每次评论前必须检查：**

- [ ] 页面是否正确（Following → Recent）
- [ ] 是否已评论过这个博主
- [ ] 是否已评论过这条推文
- [ ] 评论是否符合 persona
- [ ] 评论是否与推文相关

**如果任何一项是 "否"，则跳过这条推文。**

---

## 示例：完整的评论流程

```javascript
async function commentWithChecks() {
  // 1. 打开正确页面
  await openFollowingRecent();
  
  // 2. 读取历史
  const history = loadHistory();
  
  // 3. 遍历推文
  const tweets = await getTweets();
  
  for (const tweet of tweets) {
    // 4. 检查历史
    if (hasCommented(history, tweet)) {
      continue; // 跳过
    }
    
    // 5. 生成评论
    const comment = generateComment(tweet);
    
    // 6. 发表
    await postComment(tweet, comment);
    
    // 7. 记录
    saveToHistory(history, tweet, comment);
    
    // 8. 只评论一条
    break;
  }
}

function hasCommented(history, tweet) {
  return history.some(h => 
    h.author === tweet.author || 
    h.tweet_id === tweet.tweetId
  );
}
```

---

## 常见错误示例

### 错误 1: 在 Popular 页面评论

```
❌ 错误：
- 打开 Following → Popular
- 评论热门推文

✓ 正确：
- 打开 Following → Recent
- 评论最新推文
```

### 错误 2: 重复评论同一人

```
❌ 错误：
- 13:00 评论 @siantgirl 的推文 A："妙啊"
- 13:05 评论 @siantgirl 的推文 B："确实"

✓ 正确：
- 13:00 评论 @siantgirl 的推文 A："妙啊"
- 13:05 跳过 @siantgirl 的推文 B（已评论过这个博主）
- 13:10 评论 @other_user 的推文 C："Facts."
```

### 错误 3: 重复评论同一推文

```
❌ 错误：
- 13:00 评论推文 ID 123："妙啊"
- 13:05 评论推文 ID 123："确实"

✓ 正确：
- 13:00 评论推文 ID 123："妙啊"
- 13:05 跳过推文 ID 123（已评论）
- 13:10 评论推文 ID 456："Facts."
```

---

## 记忆文件结构

```
memory/daily/hotspots/history/
├── comments/
│   ├── 2026-03-01.json  # 每天的评论历史
│   ├── 2026-03-02.json
│   └── 2026-03-03.json
└── daily/
    └── 2026-03-02.md    # 每日日志
```

**comments/[日期].json 格式：**
```json
[
  {
    "author": "@siantgirl",
    "tweet_id": "2028297844399153394",
    "content": "确实，小红书流量太少了。B站可以试试",
    "time": "2026-03-02T13:34:00+08:00"
  },
  {
    "author": "@petergyang",
    "tweet_id": "2028335209347944624",
    "content": "Facts. Taste is human.",
    "time": "2026-03-02T13:02:00+08:00"
  }
]
```

---

## 总结

**三个绝对禁止的错误：**

1. ❌ 在 Following 的 Popular 页面评论
2. ❌ 重复评论同一个博主
3. ❌ 重复评论同一条推文

**正确的做法：**

1. ✓ 只在 Following 的 Recent 页面评论
2. ✓ 每次评论前检查历史
3. ✓ 记录每次评论到历史文件

**违反任何一条，立即停止并修正。**

---

*版本: 1.0.0*
*创建时间: 2026-03-02*
*原因: 防止重复评论错误*
