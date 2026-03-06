# Onboarding 流程

## Phase 0: 检查初始化状态

**检查文件：**
```
memory/daily/hotspots/.onboarding_complete
```

- 存在 → 跳过 onboarding
- 不存在 → 开始 onboarding

---

## Phase 1: 浏览器连接 + 登录检查

**步骤：**

```
1. 检测浏览器方式
   - 优先: OpenClaw Browser Relay
   - 回退: mcporter

2. 导航到 x.com

3. 检查登录状态
   方法: 检查页面是否有 "Log in" 按钮
   - 有 "Log in" → 未登录
   - 无 "Log in" + 有用户头像 → 已登录

4. 未登录处理
   提示: "请在浏览器中登录 X 账号，然后回复'已登录'"
   等待用户回复 → 继续
```

**登录检测代码：**

```javascript
// 检查是否登录
() => {
  const loginBtn = document.querySelector('[data-testid="login"]');
  const userAvatar = document.querySelector('[data-testid="UserAvatar"]');
  
  if (loginBtn) return { logged_in: false };
  if (userAvatar) return { logged_in: true, handle: getCurrentUserHandle() };
  return { logged_in: false };
}
```

---

## Phase 2: 选择 Persona

**问用户：**

```
以后按照哪个账号的风格发推和评论？

1. 我的账号
2. 其他账号（输入 handle，如 @elonmusk）

请选择 1 或 2：
```

**选项 1（我的账号）：**
- 获取当前登录账号的 handle
- 保存到配置
- 继续 Phase 3

**选项 2（其他账号）：**
```
请输入要学习的账号 handle（不带@，如 elonmusk）：
```
- 用户输入 → 验证账号是否存在
- 不存在 → 提示重新输入
- 存在 → 保存 handle → 继续 Phase 3

**账号验证：**

```javascript
// 验证账号是否存在
async (handle) => {
  const url = `https://x.com/${handle}`;
  // 尝试访问页面
  // 如果返回 404 → 不存在
  // 如果正常 → 存在
}
```

---

## Phase 3: 学习 Persona

**步骤：**

### 3.1 打开主页

```
导航到: https://x.com/[handle]
等待: 3-5 秒（模拟真人访问）
```

### 3.2 抓取推文

**滚动 + 抓取循环：**

```
1. 初始快照 → 提取可见推文
2. 滚动 70% 屏幕高度
3. 等待 2-3 秒
4. 快照 → 提取新推文
5. 重复直到抓取 100 条或到达底部
```

**提取内容：**

```javascript
// 提取推文
() => {
  const tweets = document.querySelectorAll('[data-testid="tweet"]');
  return Array.from(tweets).map(tweet => ({
    text: tweet.querySelector('[data-testid="tweetText"]')?.innerText,
    likes: tweet.querySelector('[data-testid="like"]')?.getAttribute('aria-label'),
    retweets: tweet.querySelector('[data-testid="retweet"]')?.getAttribute('aria-label'),
    replies: tweet.querySelector('[data-testid="reply"]')?.getAttribute('aria-label'),
    isReply: tweet.closest('[data-testid="cellInnerDiv"]')?.previousElementSibling !== null,
    timestamp: tweet.querySelector('time')?.getAttribute('datetime')
  }));
}
```

### 3.3 分析 Persona

**分析维度：**

```
1. 语言分布
   - 中文占比
   - 英文占比
   - 混合占比

2. 推文长度
   - 平均字数
   - 1-2句话占比
   - 3-5句话占比
   - 长推文占比

3. 语气分析
   - 正式/随意
   - 幽默/严肃
   - 讽刺/直接

4. 常用词汇
   - 高频词（排除停用词）
   - 特殊词汇（梗、术语）

5. 评论风格
   - 平均长度
   - 用梗频率
   - 表情使用

6. 话题偏好
   - crypto/web3
   - AI/tech
   - 体育
   - 政治
   - 其他
```

**分析代码（伪代码）：**

```python
def analyze_persona(tweets):
    # 1. 语言分布
    languages = detect_languages(tweets)
    
    # 2. 长度分布
    lengths = [len(t.text) for t in tweets]
    
    # 3. 语气分析
    tone = analyze_tone(tweets)
    
    # 4. 常用词汇
    words = extract_keywords(tweets)
    
    # 5. 评论风格（只分析 replies）
    replies = [t for t in tweets if t.isReply]
    comment_style = analyze_comments(replies)
    
    # 6. 话题偏好
    topics = extract_topics(tweets)
    
    return {
        'languages': languages,
        'lengths': lengths,
        'tone': tone,
        'words': words,
        'comment_style': comment_style,
        'topics': topics
    }
```

### 3.4 生成 Persona 描述

**使用模板：** `templates/persona.md`

**填充内容：**
- 基本信息（handle、语言、风格）
- 发推风格（长度、语气、常用词）
- 评论风格（示例）
- 话题偏好

### 3.5 展示给用户

```
我分析了 @[handle] 的前100条推文和评论，总结出以下风格：

## 基本信息
- Handle: @username
- 语言: 英文为主（80%），偶尔中文（20%）
- 风格: 随意、幽默、偶尔讽刺

## 发推风格
- 长度: 1-2句话（60%），3-5句话（30%），长推文（10%）
- 语气: 直接、有力、不废话
- 常用词汇: facts, real talk, no cap, based

## 评论风格
- 长度: 1句话为主
- 特点: 短、有力、用梗
- 示例:
  1. "Facts."
  2. "This is the way."
  3. "Real talk: most won't make it."

## 话题偏好
- 主要: crypto, AI, tech
- 避免: 政治

---

需要补充或修改吗？

1. 没问题，继续
2. 需要补充

请选择 1 或 2：
```

### 3.6 保存 Persona

**保存位置：**
```
memory/daily/hotspots/personas/[handle].md
```

**用户补充：**
- 如果用户选择"需要补充" → 等待输入 → 更新 persona → 保存

---

## Phase 4: 刷推习惯配置

### 4.1 For You 关注设置

**问题 1：**

```
在 For You 页面刷推时，是否关注新账号？

1. 是
2. 否

请选择 1 或 2：
```

**如果选"是" → 问题 2：**

```
希望关注什么样的账号？（可多选）

1. 推文阅读量 100万+
2. Crypto/Web3 相关
3. AI/Tech 相关
4. 认证账号（蓝标）
5. 粉丝数 10万+
6. 其他（自定义）

请输入选项（如 1,2,3）：
```

### 4.2 Following 互动设置

**问题 3：**

```
在 Following 页面，评论发布多久内的推文？

1. 1小时内
2. 2小时内
3. 4小时内
4. 不限制

请选择 1-4：
```

**问题 4：**

```
每5分钟刷推的配额：

- 点赞: 3 条
- 评论: 1 条

需要调整吗？

1. 默认就好
2. 自定义

请选择 1 或 2：
```

### 4.3 保存配置

**保存到：** `memory/daily/hotspots/.config.json`

**配置模板：** `templates/config.json`

---

## Phase 4.5: 刷推时间设置

**问题：**

```
每天刷推多少次？希望是固定时间还是随机时间？

可以用自然语言描述，例如：
- "每天3次，随机时间"
- "早上9点、下午3点、晚上9点"
- "每天随机2-4次"
- "工作日晚上8点，周末随机3次"

请描述你的刷推时间：
```

**解析自然语言：**

```python
def parse_schedule(user_input):
    # 示例输入解析
    
    # "每天3次，随机时间"
    if "随机" in user_input:
        count = extract_number(user_input)  # 3
        return {
            "type": "random",
            "countPerDay": count,
            "timeRange": ["09:00", "22:00"]  # 默认活跃时段
        }
    
    # "早上9点、下午3点、晚上9点"
    elif "点" in user_input:
        times = extract_times(user_input)  # ["09:00", "15:00", "21:00"]
        return {
            "type": "fixed",
            "times": times
        }
    
    # "每天随机2-4次"
    elif "随机" in user_input and "-" in user_input:
        range = extract_range(user_input)  # [2, 4]
        return {
            "type": "random_range",
            "minPerDay": range[0],
            "maxPerDay": range[1],
            "timeRange": ["09:00", "22:00"]
        }
    
    # "工作日晚上8点，周末随机3次"
    elif "工作日" in user_input or "周末" in user_input:
        return {
            "type": "weekday_weekend",
            "weekday": parse_weekday_schedule(user_input),
            "weekend": parse_weekend_schedule(user_input)
        }
    
    # 默认
    else:
        return {
            "type": "random",
            "countPerDay": 3,
            "timeRange": ["09:00", "22:00"]
        }
```

**解析示例：**

| 用户输入 | 解析结果 |
|----------|----------|
| "每天3次，随机时间" | `{"type": "random", "countPerDay": 3}` |
| "早上9点、下午3点、晚上9点" | `{"type": "fixed", "times": ["09:00", "15:00", "21:00"]}` |
| "每天随机2-4次" | `{"type": "random_range", "minPerDay": 2, "maxPerDay": 4}` |
| "工作日晚上8点，周末随机3次" | `{"type": "weekday_weekend", "weekday": {"times": ["20:00"]}, "weekend": {"countPerDay": 3}}` |
| "每天早上起来刷一次" | `{"type": "fixed", "times": ["08:00"]}` |

**确认配置：**

```
理解了，你的刷推时间设置：

- 类型: 随机
- 每天次数: 3次
- 时间范围: 09:00 - 22:00

系统会在这个范围内随机选择时间提醒你刷推。

确认吗？

1. 确认
2. 重新设置

请选择 1 或 2：
```

**保存到配置：**

```json
{
  "schedule": {
    "type": "random",
    "countPerDay": 3,
    "timeRange": ["09:00", "22:00"],
    "reminderEnabled": true
  }
}
```

---

## Phase 5: 完成 Onboarding

**步骤：**

```
1. 保存刷推时间配置
   更新 memory/daily/hotspots/.config.json

2. 设置刷推提醒（如果启用）
   根据 schedule.type 创建 cron 任务

3. 创建完成标记
   touch memory/daily/hotspots/.onboarding_complete

4. 创建记忆目录
   mkdir -p memory/daily/hotspots/history/comments
   mkdir -p memory/daily/hotspots/history/daily

5. 设置每日热点总结（询问用户）
   "是否设置每日热点总结？每天早上10点推送。"
   - 是 → 运行 ./scripts/setup-cron.sh
   - 否 → 跳过

6. 通知用户
   "Onboarding 完成！配置已保存。回复'刷推'开始。"
```

---

## Onboarding 检查清单

```
□ 浏览器已连接
□ X 账号已登录
□ Persona 已选择
□ Persona 已学习（100条）
□ Persona 已确认/补充
□ For You 关注条件已配置
□ Following 互动规则已配置
□ 刷推时间已设置（新增）
□ 配置已保存
□ 记忆目录已创建
□ 定时任务已设置（可选）
□ 完成标记已创建
```

---

*文档版本: 1.0*
*更新: 2026-03-02*
