# Step 2: 关键词设计

## 目标
基于研究主题生成 5 个英文搜索关键词，最大化 Reddit 搜索覆盖面。

## 前置条件
- Step 1 已完成
- `progress.json` 中 `topic` 和 `topic_en` 已填写

## 关键词覆盖维度

必须生成 5 个关键词，分别覆盖以下维度：

| # | 维度 | 说明 | 示例（主题：Cursor IDE） |
|---|------|------|--------------------------|
| 1 | 🎯 核心词 | **锚定词**，直接匹配主题，**必须保留不可修改** | `Cursor IDE` |
| 2 | 🔄 同义/近义词 | 社区中常用的替代表述 | `Cursor AI editor` |
| 3 | 📚 教程/How-to | 教程、指南类搜索 | `Cursor IDE tutorial setup` |
| 4 | 💡 经验/最佳实践 | 用户分享、经验讨论 | `Cursor IDE tips workflow` |
| 5 | 😫 痛点/问题 | 抱怨、bug、限制等讨论 | `Cursor IDE issues problems` |

## 锚定词规则

> **锚定词**是 `topic_en` 的核心表述，每个关键词中都必须包含锚定词或其明确缩写。
> 例如：主题为 "Machine Learning"，锚定词为 "Machine Learning" 或 "ML"。

## 执行步骤

### 2.1 AI 生成关键词

主 Agent 根据以下 Prompt 模板生成关键词：

```
你是一个 Reddit 搜索关键词专家。

研究主题：{topic}（英文：{topic_en}）
目标受众：{audience}
关注方向：{focus}

请生成 5 个英文搜索关键词，严格覆盖以下 5 个维度：
1. 核心词（锚定词直接匹配）
2. 同义/近义词（社区替代表述）
3. 教程/How-to（学习指南类）
4. 经验/最佳实践（用户分享类）
5. 痛点/问题（抱怨讨论类）

规则：
- 每个关键词必须包含锚定词「{topic_en}」或其公认缩写
- 每个关键词 2-5 个单词
- 使用 Reddit 社区常用的自然表述
- 不使用引号或特殊搜索语法

输出格式（严格 JSON）：
{
  "anchor_word": "锚定词",
  "keywords": [
    { "dimension": "核心词", "keyword": "..." },
    { "dimension": "同义词", "keyword": "..." },
    { "dimension": "教程类", "keyword": "..." },
    { "dimension": "经验类", "keyword": "..." },
    { "dimension": "痛点类", "keyword": "..." }
  ]
}
```

### 2.2 保存关键词

将生成结果保存到 `runs/<slug>/keywords.json`。

### 2.3 更新 progress.json

将 Step 2 标记为 `completed`，`current_step` 设为 `3`。

## 输出文件

`keywords.json` 示例：
```json
{
  "anchor_word": "Cursor IDE",
  "keywords": [
    { "dimension": "核心词", "keyword": "Cursor IDE" },
    { "dimension": "同义词", "keyword": "Cursor AI code editor" },
    { "dimension": "教程类", "keyword": "Cursor IDE tutorial setup guide" },
    { "dimension": "经验类", "keyword": "Cursor IDE tips best practices" },
    { "dimension": "痛点类", "keyword": "Cursor IDE issues limitations" }
  ]
}
```

## 下一步

→ [Step 3: 数据采集](step-3-collect.md)
