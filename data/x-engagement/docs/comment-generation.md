# 评论生成逻辑

## 概述

**目标：**
- 生成符合 persona 风格的评论
- 匹配推文语言
- 避免自相矛盾
- 短、有力、有趣

---

## 1. 评论流程

```
推文 → 检查 → 生成 → 检查历史 → 检查用户事实 → 发表 → 记录
```

### 1.1 完整流程

```python
def comment_workflow(tweet):
    # 1. 检查推文
    if not should_comment(tweet):
        return None
    
    # 2. 生成评论
    persona = load_persona(config.persona)
    proposed = generate_comment(tweet, persona)
    
    # 3. 检查历史
    issues = check_history(tweet, proposed)
    if issues:
        proposed = regenerate(proposed, avoid=issues)
    
    # 4. 检查用户事实
    issues = check_user_facts(proposed)
    if issues:
        proposed = regenerate(proposed, avoid=issues)
    
    # 5. 发表
    post_comment(proposed)
    
    # 6. 记录
    record_comment(tweet, proposed)
    
    return proposed
```

---

## 2. 推文检查

### 2.1 跳过条件

| 条件 | 说明 |
|------|------|
| 发布时间 > 2小时 | 只评论新推文 |
| 政治/战争内容 | 避免敏感话题 |
| 已评论过 | 避免重复 |
| 推文语言不匹配 | 无法用正确语言评论 |

### 2.2 检查代码

```python
def should_comment(tweet):
    # 1. 检查时间
    age_hours = (now() - tweet.timestamp) / 3600
    if age_hours > 2:
        return False
    
    # 2. 检查类型
    if is_political(tweet.text) or is_war(tweet.text):
        return False
    
    # 3. 检查是否已评论
    history = load_recent_comments(days=7)
    if any(c.target == tweet.author and c.tweet == tweet.text for c in history):
        return False
    
    # 4. 检查语言
    lang = detect_language(tweet.text)
    if lang not in ["zh", "en"]:
        return False
    
    return True
```

### 2.3 政治检测

```python
political_keywords = [
    "特朗普", "拜登", "习近平", "普京",
    "Trump", "Biden", "Putin", "Xi",
    "选举", "election", "投票", "vote",
    "民主党", "共和党", "Democrat", "Republican"
]

war_keywords = [
    "战争", "war", "导弹", "missile",
    "轰炸", "bomb", "伊朗", "Iran",
    "以色列", "Israel", "加沙", "Gaza"
]

def is_political(text):
    return any(kw in text for kw in political_keywords)

def is_war(text):
    return any(kw in text for kw in war_keywords)
```

---

## 3. 语言匹配

### 3.1 语言检测

```python
def detect_language(text):
    # 简单检测
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text)
    
    if chinese_chars / total_chars > 0.3:
        return "zh"
    else:
        return "en"
```

### 3.2 语言匹配规则

| 推文语言 | 评论语言 | 说明 |
|----------|----------|------|
| 中文 | 中文 | 中文评论 |
| 英文 | 英文 | 英文评论 |
| 混合 | 英文 | 默认英文 |
| 其他 | 跳过 | 不评论 |

---

## 4. Persona 风格应用

### 4.1 Persona 内容

**从 `memory/daily/hotspots/personas/[handle].md` 读取：**

```markdown
## 评论风格
- 长度: 1句话
- 特点: 短、有力、用梗
- 示例:
  1. "Facts."
  2. "This is the way."
  3. "Real talk."
```

### 4.2 风格应用

```python
def apply_persona_style(comment, persona):
    # 1. 检查长度
    if len(comment) > persona.max_comment_length:
        comment = shorten(comment, persona.max_comment_length)
    
    # 2. 检查语气
    if persona.tone == "casual":
        comment = make_casual(comment)
    
    # 3. 添加特色
    if persona.use_slang:
        comment = add_slang(comment, persona.common_words)
    
    return comment
```

### 4.3 风格示例

**Persona 1: 短、有力、用梗**

```
推文: "AI will replace all jobs"
评论: "Facts. Adapt or get left behind."
```

**Persona 2: 幽默、自嘲**

```
推文: "今天亏了50%"
评论: "韭菜互帮互助，我昨天亏了60%"
```

**Persona 3: 正式、分析**

```
推文: "市场分析"
评论: "分析到位。补充一点：..."
```

---

## 5. 评论模板

### 5.1 中文模板

**认同类：**
- "确实"
- "有道理"
- "妙啊"
- "太真实了"
- "学到了"

**幽默类：**
- "韭菜互帮互助"
- "扎心了老铁"
- "笑死"
- "真实得让人害怕"

**梗类：**
- "这波啊，这波是..."
- "好家伙"
- "绝了"
- "妙啊妙啊"

**提问类：**
- "哪家店？"
- "什么项目？"
- "怎么做到的？"

### 5.2 英文模板

**Agreement:**
- "Facts."
- "This."
- "Based."
- "Real talk."
- "This is the way."

**Humor:**
- "Lol"
- "Dead"
- "Bro really said that"

**Crypto/Tech:**
- "Wen moon?"
- "Diamond hands"
- "WAGMI"
- "Probably nothing"

**Question:**
- "Source?"
- "Proof?"
- "How?"

---

## 6. 历史检查

### 6.1 检查内容

**1. 重复检查：**
- 最近7天对同一用户说过类似的话吗？
- 相似度 > 80% → 重新生成

**2. 矛盾检查：**
- 与之前的评论矛盾吗？
- 矛盾 → 重新生成

### 6.2 实现代码

```python
def check_history(tweet, proposed):
    issues = []
    
    # 加载最近评论
    recent = load_comments_from_last_n_days(7)
    
    # 检查重复
    for c in recent:
        if c.target == tweet.author:
            if similarity(c.text, proposed) > 0.8:
                issues.append({
                    "type": "duplicate",
                    "previous": c.text
                })
    
    # 检查矛盾
    for c in recent:
        if contradicts(c.text, proposed):
            issues.append({
                "type": "contradiction",
                "previous": c.text
            })
    
    return issues
```

### 6.3 相似度计算

```python
def similarity(text1, text2):
    # Jaccard 相似度
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union)
```

---

## 7. 用户事实检查

### 7.1 检查内容

**从 `memory/daily/hotspots/history/user-facts/` 读取：**

- 用户说过的话
- 用户偏好
- 避免触雷

### 7.2 实现代码

```python
def check_user_facts(proposed):
    issues = []
    
    facts = load_user_facts()
    
    # 检查偏好
    if contains_political_content(proposed):
        if "政治" in facts.avoid_topics:
            issues.append({
                "type": "preference_violation",
                "topic": "政治"
            })
    
    # 检查事件矛盾
    for event in facts.events:
        if event_contradicts(event, proposed):
            issues.append({
                "type": "event_contradiction",
                "event": event.text
            })
    
    return issues
```

### 7.3 矛盾示例

```python
# 用户说过
event = "昨天出去吃饭了"

# 准备评论
proposed = "你最近都在家做饭啊"

# 检测
def event_contradicts(event, comment):
    pairs = [
        (["出去", "外出", "餐厅"], ["在家", "家里"]),
        (["喜欢"], ["不喜欢"]),
        (["买了"], ["没钱"])
    ]
    
    for pos, neg in pairs:
        if any(p in event for p in pos) and any(n in comment for n in neg):
            return True
    
    return False

# 结果: True → 矛盾 → 重新生成
```

---

## 8. 重新生成

### 8.1 重新生成逻辑

```python
def regenerate(tweet, persona, avoid_issues):
    # 根据 issue 类型调整
    for issue in avoid_issues:
        if issue["type"] == "duplicate":
            # 换一种说法
            return generate_different_style(tweet, persona)
        
        elif issue["type"] == "contradiction":
            # 避免矛盾内容
            return generate_avoiding(tweet, persona, issue["previous"])
        
        elif issue["type"] == "preference_violation":
            # 避免偏好违规
            return generate_neutral(tweet, persona)
        
        elif issue["type"] == "event_contradiction":
            # 避免事件矛盾
            return generate_avoiding(tweet, persona, issue["event"])
    
    # 默认重新生成
    return generate_comment(tweet, persona)
```

### 8.2 换一种说法

```python
def generate_different_style(tweet, persona):
    # 尝试不同风格
    styles = ["agreement", "humor", "question", "neutral"]
    
    for style in styles:
        comment = generate_with_style(tweet, persona, style)
        if is_acceptable(comment):
            return comment
    
    # 如果都不行，用简单认同
    return "确实" if detect_language(tweet.text) == "zh" else "Facts."
```

---

## 9. 完整示例

### 9.1 示例 1：正常评论

```
推文: @user1 "今天市场大涨！"
语言: 中文
时间: 1小时前
类型: crypto

流程:
1. ✓ 时间检查通过（< 2小时）
2. ✓ 类型检查通过（非政治）
3. ✓ 历史检查通过（未评论过）
4. 生成评论: "确实，趋势起来了。"
5. ✓ 用户事实检查通过
6. 发表
7. 记录

结果: "确实，趋势起来了。"
```

### 9.2 示例 2：重复评论

```
推文: @user1 "市场分析"
语言: 中文
时间: 30分钟前

历史:
- 昨天 @user1 "市场走势" → "确实，分析到位。"

流程:
1. ✓ 时间检查通过
2. ✓ 类型检查通过
3. ✗ 历史检查：重复（相似度 0.85）
4. 重新生成: "这波分析可以"
5. ✓ 用户事实检查通过
6. 发表
7. 记录

结果: "这波分析可以"
```

### 9.3 示例 3：矛盾评论

```
推文: @user2 "最近都在家做饭"
语言: 中文
时间: 1小时前

用户事实:
- 昨天: "出去吃饭了，海底捞"

流程:
1. ✓ 时间检查通过
2. ✓ 类型检查通过
3. ✓ 历史检查通过
4. 生成评论: "你最近都在家做饭啊"
5. ✗ 用户事实检查：矛盾（用户昨天出去吃饭）
6. 重新生成: "做饭不错，偶尔出去换换口味也好"
7. 发表
8. 记录

结果: "做饭不错，偶尔出去换换口味也好"
```

### 9.4 示例 4：政治内容

```
推文: @user3 "特朗普最新政策"
语言: 中文
时间: 1小时前

流程:
1. ✓ 时间检查通过
2. ✗ 类型检查：政治内容
3. 跳过

结果: 不评论
```

---

## 10. 评论质量检查

### 10.1 质量标准

| 标准 | 说明 |
|------|------|
| 长度 | 1-2句话 |
| 语言 | 匹配推文 |
| 语气 | 符合 persona |
| 内容 | 不矛盾、不重复 |
| 有趣 | lighthearted |

### 10.2 质量检查代码

```python
def quality_check(comment, persona):
    score = 0
    
    # 长度
    if 5 <= len(comment) <= 50:
        score += 20
    
    # 语言
    if matches_language(comment, persona.language):
        score += 20
    
    # 语气
    if matches_tone(comment, persona.tone):
        score += 20
    
    # 有趣
    if is_lighthearted(comment):
        score += 20
    
    # 不矛盾
    if not has_contradictions(comment):
        score += 20
    
    return score
```

---

*文档版本: 1.0*
*更新: 2026-03-02*
