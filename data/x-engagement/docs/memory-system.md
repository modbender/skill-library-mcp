# 记忆系统设计

## 概述

**目的：**
- 记录每次评论内容
- 记录用户说过的话
- 评论前检查历史，避免矛盾
- 学习用户习惯和偏好

**核心原则：**
- 事事记录
- 评论前检查
- 避免自相矛盾

---

## 1. 记忆层结构

```
memory/daily/hotspots/
├── .onboarding_complete     # Onboarding 完成标记
├── .config.json             # 用户配置
│
├── personas/
│   └── [handle].md          # Persona 描述
│
├── events/                  # 重大事件（永久保留）
│   └── iran-war-2026.md
│
├── tables/                  # 每日热点（滚动7天）
│   ├── 2026-03-01.md
│   └── 2026-03-02.md
│
└── history/                 # 历史记录
    ├── comments/            # 评论历史
    │   ├── 2026-03-01.md
    │   └── 2026-03-02.md
    │
    ├── daily/               # 每日日志
    │   ├── 2026-03-01.md
    │   └── 2026-03-02.md
    │
    └── user-facts/          # 用户事实（永久保留）
        ├── preferences.md   # 偏好
        └── events.md        # 事件（如"昨天出去吃饭了"）
```

---

## 2. 评论历史记录

### 2.1 为什么记录

**问题场景：**
```
Day 1: 用户说"昨天出去吃饭了"
Day 2: Bot 评论"你最近都在家做饭啊"
→ 自相矛盾！
```

**解决方案：**
- 记录每次评论内容
- 记录用户说过的话
- 评论前检查历史

### 2.2 记录格式

**文件：** `memory/daily/hotspots/history/comments/YYYY-MM-DD.md`

**格式：**

```markdown
# 2026-03-01 评论历史

## 评论 1
- 时间: 10:23
- 对象: @user1
- 推文: "今天市场大涨！"
- 我的评论: "确实，趋势起来了。"
- 语言: 中文

## 评论 2
- 时间: 10:29
- 对象: @user2
- 推文: "AI will replace all jobs"
- 我的评论: "Facts. Adapt or get left behind."
- 语言: 英文

## 评论 3
- 时间: 10:35
- 对象: @user3
- 推文: "昨天出去吃饭了，好吃"
- 我的评论: "哪家店？"
- 用户回复: "海底捞"
- 语言: 中文

---

*总计: 3 条评论*
```

### 2.3 记录时机

**每次评论后立即记录：**

```python
def record_comment(comment_data):
    today = get_today_date()
    file = f"memory/daily/hotspots/history/comments/{today}.md"
    
    # 追加到文件
    append_to_file(file, format_comment(comment_data))
```

### 2.4 记录内容

**必记：**
- 评论时间
- 评论对象（@handle）
- 原推文内容（简短摘要）
- 我的评论内容
- 语言

**可选：**
- 用户回复
- 点赞数
- 回复数

---

## 3. 用户事实记录

### 3.1 为什么记录

**用户说过的话很重要：**
- "我昨天出去吃饭了" → 记住
- "我不喜欢政治" → 记住
- "我最近在看 AI 项目" → 记住

**避免矛盾：**
- 不要评论"你最近都在家"
- 不要推荐政治内容
- 多推荐 AI 相关

### 3.2 记录格式

**文件：** `memory/daily/hotspots/history/user-facts/events.md`

**格式：**

```markdown
# 用户事件记录

## 2026-03-01
- 用户说: "昨天出去吃饭了，海底捞"
  - 推断: 用户喜欢吃火锅，偶尔外出就餐
  - 记录时间: 2026-03-01 10:35

- 用户说: "最近在看 AI 项目"
  - 推断: 对 AI 感兴趣
  - 记录时间: 2026-03-01 14:22

## 2026-02-28
- 用户说: "我不喜欢政治"
  - 推断: 避免政治话题
  - 记录时间: 2026-02-28 09:15
```

### 3.3 用户偏好

**文件：** `memory/daily/hotspots/history/user-facts/preferences.md`

**格式：**

```markdown
# 用户偏好

## 话题偏好
- 喜欢: AI, crypto, tech, 美食
- 避免: 政治, 战争

## 语言偏好
- 主要: 中文
- 次要: 英文

## 评论风格偏好
- 短、有力、用梗
- 不用 emoji

## 时间偏好
- 活跃时段: 20:00-23:00
- 避免时段: 02:00-08:00

## 其他
- 不喜欢被纠正
- 喜欢直接表达
```

### 3.4 记录时机

**识别用户陈述：**

```python
def detect_user_fact(message):
    patterns = [
        r"我(昨天|今天|最近).*",  # "我昨天出去吃饭了"
        r"我(喜欢|不喜欢|爱|恨).*",  # "我喜欢AI"
        r"我(在|正在|去).*",  # "我在看AI项目"
    ]
    
    for pattern in patterns:
        if match(pattern, message):
            return extract_fact(message)
    
    return None

# 使用
fact = detect_user_fact("我昨天出去吃饭了")
if fact:
    record_user_fact(fact)
```

---

## 4. 评论前检查

### 4.1 检查流程

```
准备评论 → 检查历史 → 检查用户事实 → 确认不矛盾 → 发表评论
```

### 4.2 检查内容

**1. 评论历史：**
- 最近7天对同一用户说过什么
- 避免重复评论
- 避免自相矛盾

**2. 用户事实：**
- 用户说过什么
- 用户偏好是什么
- 避免触雷

### 4.3 实现代码

```python
def check_before_comment(tweet, proposed_comment):
    issues = []
    
    # 1. 检查评论历史
    recent_comments = load_recent_comments(days=7)
    
    # 避免重复
    for c in recent_comments:
        if c.target == tweet.author:
            if similarity(c.text, proposed_comment) > 0.8:
                issues.append(f"最近对 @{tweet.author} 说过类似的话")
    
    # 避免矛盾
    for c in recent_comments:
        if contradicts(c.text, proposed_comment):
            issues.append(f"与之前的评论矛盾: '{c.text}'")
    
    # 2. 检查用户事实
    user_facts = load_user_facts()
    
    # 检查偏好
    if contains_political_content(proposed_comment):
        if "政治" in user_facts.avoid_topics:
            issues.append("用户不喜欢政治内容")
    
    # 检查事件矛盾
    if "在家" in proposed_comment and user_facts.has_event("昨天出去吃饭了"):
        issues.append("用户昨天出去吃饭了，说'在家'会矛盾")
    
    return issues
```

### 4.4 矛盾检测示例

**场景：**

```python
# 用户说过
user_fact = "昨天出去吃饭了"

# 准备评论
proposed_comment = "你最近都在家做饭啊"

# 检测矛盾
def is_contradiction(fact, comment):
    keywords_pairs = [
        (["出去", "外出", "餐厅"], ["在家", "家里", "自己做"]),
        (["喜欢", "爱"], ["不喜欢", "讨厌"]),
        (["买了", "入手"], ["没钱", "穷"]),
    ]
    
    for pos, neg in keywords_pairs:
        if any(p in fact for p in pos) and any(n in comment for n in neg):
            return True
    
    return False

# 结果: True → 矛盾 → 拒绝评论
```

---

## 5. 每日日志

### 5.1 记录内容

**文件：** `memory/daily/hotspots/history/daily/YYYY-MM-DD.md`

**格式：**

```markdown
# 2026-03-01 每日日志

## 刷推统计
- 总时长: 30分钟
- For You 浏览: 20屏
- Following 点赞: 15条
- Following 评论: 5条
- 新关注: 3人

## 评论记录
1. @user1: "确实，趋势起来了。"
2. @user2: "Facts."
3. @user3: "哪家店？"
4. @user4: "This is the way."
5. @user5: "妙啊"

## 用户互动
- 用户说: "昨天出去吃饭了"
- 用户说: "最近在看AI项目"

## 重大事件
- 伊朗战争爆发（记录到 events/iran-war-2026.md）

## 备注
- 用户今天心情不错
- 避免政治话题

---

*生成时间: 2026-03-01 23:00*
```

### 5.2 日志用途

- 回顾每日活动
- 分析刷推效果
- 调整策略
- 记忆持久化

---

## 6. 记忆清理策略

### 6.1 滚动删除

| 类型 | 保留时间 | 说明 |
|------|----------|------|
| 评论历史 | 30天 | 超过30天删除 |
| 每日日志 | 30天 | 超过30天删除 |
| 热点表格 | 7天 | 超过7天删除 |
| 用户事实 | 永久 | 一直保留 |
| 重大事件 | 永久 | 一直保留 |
| Persona | 永久 | 一直保留 |

### 6.2 清理脚本

```bash
# 每周运行一次
find memory/daily/hotspots/history/comments -mtime +30 -delete
find memory/daily/hotspots/history/daily -mtime +30 -delete
find memory/daily/hotspots/tables -mtime +7 -delete
```

---

## 7. 记忆检索

### 7.1 检索场景

**评论前：**
- 检索最近7天评论历史
- 检索用户事实

**生成 persona：**
- 检索用户偏好
- 检索历史评论风格

**每日总结：**
- 检索当日日志
- 检索当日评论

### 7.2 检索代码

```python
def retrieve_memory(query_type, **kwargs):
    if query_type == "recent_comments":
        days = kwargs.get("days", 7)
        return load_comments_from_last_n_days(days)
    
    elif query_type == "user_facts":
        return load_user_facts()
    
    elif query_type == "daily_log":
        date = kwargs.get("date", today())
        return load_daily_log(date)
    
    elif query_type == "persona":
        handle = kwargs.get("handle")
        return load_persona(handle)
```

---

## 8. 完整流程示例

### 8.1 评论流程（带记忆检查）

```python
def comment_with_memory_check(tweet, persona):
    # 1. 准备评论
    proposed_comment = generate_comment(tweet, persona)
    
    # 2. 检查历史
    issues = check_before_comment(tweet, proposed_comment)
    
    # 3. 如果有问题，重新生成
    if issues:
        print(f"问题: {issues}")
        proposed_comment = regenerate_comment(tweet, persona, avoid=issues)
    
    # 4. 发表评论
    post_comment(proposed_comment)
    
    # 5. 记录到历史
    record_comment({
        "time": now(),
        "target": tweet.author,
        "tweet": tweet.text,
        "comment": proposed_comment,
        "language": detect_language(proposed_comment)
    })
    
    return proposed_comment
```

### 8.2 用户说了一句话（记录）

```python
def handle_user_message(message):
    # 1. 检测是否是事实陈述
    fact = detect_user_fact(message)
    
    # 2. 如果是，记录
    if fact:
        record_user_fact(fact)
        print(f"记录用户事实: {fact}")
    
    # 3. 检测偏好
    preference = detect_preference(message)
    if preference:
        update_user_preference(preference)
        print(f"更新用户偏好: {preference}")
```

---

## 9. 记忆系统检查清单

```
□ 评论历史目录已创建
□ 每日日志目录已创建
□ 用户事实目录已创建
□ 评论前检查逻辑已实现
□ 矛盾检测已实现
□ 记录函数已实现
□ 清理脚本已设置
```

---

*文档版本: 1.0*
*更新: 2026-03-02*
