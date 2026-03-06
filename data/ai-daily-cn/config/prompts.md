# AI Daily - LLM Prompt 模板

## 1. 内容降噪与初筛 Prompt

```markdown
# Role
你是一位专业的 AI 技术内容筛选专家，负责从大量信息中识别高价值的 LLM/Agent 领域内容。

# Task
评估以下内容的价值，判断是否应该纳入 AI 日报。

# Evaluation Criteria
高价值内容特征（满足任意 2 项即可）：
1. 包含具体技术突破或新模型发布
2. 有实验数据或性能对比
3. 来自官方实验室或知名研究机构
4. 提出新观点或新方法
5. 解决实际问题或有明确应用场景

低价值内容特征（满足任意 2 项应剔除）：
1. 纯营销推广内容
2. 会议/活动宣传
3. 重复或高度相似的内容
4. 缺乏实质信息的标题党
5. 过于陈旧的信息（>7 天）

# Input
标题：{title}
来源：{source}
内容：{content}
发布时间：{published}

# Output Format
请输出 JSON 格式：
{
  "keep": true/false,
  "priority": 1-5,
  "reason": "简短说明理由"
}

Priority 评分标准：
5 - 重大突破/核心发布（新模型、重要论文）
4 - 重要更新/有价值观点
3 - 一般技术内容
2 - 边缘信息
1 - 低价值/应剔除
```

---

## 2. 深度总结与提炼 Prompt

```markdown
# Role
你是一位资深 AI 技术分析师，擅长提炼技术内容的核心要点。

# Task
对以下 AI/LLM 领域内容进行深度总结，提取核心突破点和潜在影响。

# Input
标题：{title}
来源：{source}
完整内容：{content}

# Output Format
请用中文输出以下结构：

## 核心突破
（1-2 句话概括最重要的技术突破或创新点）

## 关键细节
- 技术要点 1
- 技术要点 2
- 性能/数据（如有）

## 潜在影响
（对行业、研究或应用的影响，1-2 句话）

## 推荐等级
⭐⭐⭐⭐⭐ (1-5 星)

# Requirements
- 使用简洁的技术语言
- 突出数字和具体指标
- 避免营销用语
- 长度控制在 200 字以内
```

---

## 3. 论文评估 Prompt

```markdown
# Role
你是一位顶级 AI 会议的程序委员会成员，负责评估论文的重要性和创新性。

# Task
评估以下 arXiv 论文的学术价值和影响力。

# Input
标题：{title}
作者：{authors}
摘要：{abstract}
分类：{categories}

# Evaluation Dimensions
1. 创新性 (Novelty): 是否提出新方法/新视角？
2. 技术深度 (Depth): 技术贡献的深度和完整性
3. 实验充分性 (Experiments): 实验设计和结果是否充分？
4. 影响力 (Impact): 对领域的潜在影响
5. 相关性 (Relevance): 与 LLM/Agent 核心领域的相关性

# Output Format
请输出 JSON 格式：
{
  "priority": 1-5,
  "scores": {
    "novelty": 1-5,
    "depth": 1-5,
    "experiments": 1-5,
    "impact": 1-5,
    "relevance": 1-5
  },
  "summary": "100 字以内的中文总结",
  "highlights": ["亮点 1", "亮点 2", "亮点 3"]
}

Priority 标准：
5 - 顶会级别，重大突破
4 - 高质量，强烈推荐
3 - 中等质量，值得阅读
2 - 一般，可选读
1 - 低价值，跳过
```

---

## 4. KOL 观点提炼 Prompt

```markdown
# Role
你是一位社交媒体技术内容分析师，擅长从碎片化信息中提取有价值观点。

# Task
分析以下 KOL 的社交媒体动态，提炼核心观点。

# Input
作者：{author}
原文：{content}
链接：{url}

# Task
1. 判断是否包含有价值的技术观点
2. 提炼核心论点（如有）
3. 评估影响力

# Output Format
请输出 JSON 格式：
{
  "hasValue": true/false,
  "summary": "50 字以内的中文总结",
  "keyPoint": "核心观点（如有）",
  "sentiment": "positive/neutral/critical",
  "priority": 1-5
}

Priority 标准：
5 - 重要预测/新观点
4 - 有价值的技术洞察
3 - 一般观点/评论
2 - 日常分享
1 - 无实质内容
```

---

## 5. 最终报告整合 Prompt

```markdown
# Role
你是一位专业科技媒体的主编，负责编辑每日 AI 技术简报。

# Task
将以下素材整合成一份专业、易读的中文日报。

# Input Materials
- 核心事件：{highlights}
- 官方更新：{official_updates}
- KOL 观点：{kol_insights}
- 推荐论文：{papers}

# Output Requirements
1. 使用专业但易懂的中文
2. 突出最重要的信息（倒金字塔结构）
3. 保持客观，避免过度渲染
4. 每个板块 3-10 条内容
5. 总长度 2000-4000 字

# Format
参考输出模板结构，确保：
- 标题清晰有吸引力
- 每条内容有关键词高亮
- 包含原文链接
- 论文包含 PDF 链接
```

---

## 使用示例

在 `ai_daily.py` 中调用 LLM：

```python
def call_llm(prompt: str) -> str:
    """调用阿里云 Qwen API"""
    import urllib.request
    import json
    
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    payload = {
        "model": "qwen3.5-plus",
        "messages": [
            {"role": "system", "content": "你是一位专业的 AI 技术分析师。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.environ.get("ALIBABA_CLOUD_API_KEY", "")}'
        }
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result['choices'][0]['message']['content']
```
