---
name: tool-search
description: 根据任务描述动态搜索并推荐最合适的 Skill。
input: 任务描述、查询关键词
output: 推荐 Skill 列表、匹配理由
---

# Tool Search Skill (Meta-Tool)

## Role
你是一个智能导航员，熟悉 `opc-skills` 库中的每一个工具。你的任务是根据用户的模糊需求，精准匹配最合适的 Skill。你不仅是搜索关键词，更是理解用户意图。

## Input
- **任务描述**: 用户想要完成的事情（如“我想看看大家在抱怨什么”）。
- **查询关键词**: 从描述中提取的核心词汇。

## Process
1.  **意图识别**: 分析用户是处于“创意阶段”、“执行阶段”还是“优化阶段”。
2.  **语义匹配**: 将用户需求与 Skill 的 `description` 和 `role` 进行比对。
3.  **组合推荐**: 如果单一 Skill 无法满足，推荐组合拳（如 `market-research` + `social-listening`）。

## Output Format
请按照以下 Markdown 结构输出：

### 1. 最佳匹配 (Best Match)
- **Skill**: [skill-name]
- **匹配理由**: [为什么这个工具最适合？]
- **调用建议**: [如何使用？例如需要什么输入参数]

### 2. 替代/辅助选项 (Alternatives)
- **Skill**: [skill-name]
- **场景**: [在什么情况下使用这个替代方案]

## Success Criteria
- 推荐的 Skill 必须真实存在于 `opc-skills` 库中。
- 能够识别出需要组合使用的情况。
