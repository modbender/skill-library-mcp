---
name: 📚 Enterprise Knowledge Retrieval
description: operation platform enterprise knowledge
---

```
---
name: enterprise-knowledge
display_name: 知识库检索
version: "0.2.0"
description: |
  快手企业知识库检索：在业务空间/知识库中搜索企业内部口径、政策、流程、SOP、规范、FAQ，并返回Top结果片段与链接。
metadata: { "openclaw": { "emoji": "📚" } }
triggers:
  - intent: 快手企业知识库检索
    keywords:
      - 知识库
      - 规章制度
      - 政策
      - 口径
      - SOP
      - 流程
      - 指南
      - 规范
      - FAQ
      - 规则
      - 操作手册
      - 内部文档
      - 怎么规定
      - 如何申请
      - 需要哪些材料
    examples: |
      退费规则是什么？（公司内部口径）
      报销流程怎么走？需要什么材料？
      入职流程/转正流程在哪里？
      XXX权限怎么开通？内部SOP是什么？
      在【电商运营空间】的【退费政策库】里查一下：退款多久到账？
      帮我从知识库找一下：客服升级工单的规则
      这个问题公司有没有统一口径/文档？
---

# 📚 Enterprise Knowledge Retrieval

## 什么时候必须用本技能（强规则）

当用户问题属于"企业内部信息/口径"，例如：

- 政策/规则/制度（退费、报销、权限、合规、处罚等）
- 流程/SOP/操作指南（如何申请、怎么开通、怎么处理、工单流转）
- FAQ/统一口径（对外回复话术、客服口径、模板）
- 用户明确说"去知识库查/在某空间某知识库查"

**模型不确定答案是否准确时，也应优先检索再回答。**

## 什么时候不要用

- 纯常识/通用知识（与企业内部无关）
- 用户只想你"主观建议/写作润色"，不需要企业口径支撑
- 用户已经提供了完整的企业文档内容让你总结（这时直接总结即可）

---

# ✅ 固定流程（按顺序执行，任一步失败立刻返回错误）

baseUrl:
http://kwaishop-gateway-manage.internal

## Step 1：获取业务空间列表（用于选择 spaceCode）

POST:
http://kwaishop-gateway-manage.internal/gateway/langbridge/openclaw/querySpaces

Body:
{
"spaceName": "",
"spaceCode": "",
"spaceType": "",
"pageInfo": { "page": "1", "pageSize": "50" },
"operator": "${operator}"
}

从响应 data.businessSpaceInfo[] 提取：

- spaceName
- code（spaceCode）

## Step 2：获取该空间下知识库列表（用于选择 repoCode）

POST:
http://kwaishop-gateway-manage.internal/gateway/langbridge/openclaw/space/knowledge

Body:
{
"businessSpaceCode": "${spaceCode}",
  "knowledgeRepoName": "",
  "pageRequest": { "pageNo": "1", "pageSize": "50" },
  "operator": "${operator}"
}

从响应 data.knowledgeRepoInfo[] 提取：

- name
- code（repoCode）

## Step 3：检索

POST:
http://kwaishop-gateway-manage.internal/gateway/langbridge/knowledge/retrieve/mcp/public

Body:
{
"repoCode": "${repoCode}",
  "query": "${query}",
"operator": "${operator}",
  "businessSpaceBizKey": "${spaceCode}"
}

从响应 data.reference[] 提取：

- content
- documentName
- documentUrl
- score

---

# 🧠 选择与记忆规则（简单、可执行）

## operator

operator 从本地凭证注入（如 ~/.openclaw/username）。

## 默认记忆

缓存：

- last_space_code
- last_repo_code

优先级：

1. 用户本轮明确指定 space/repo → 使用用户指定
2. 否则若缓存存在 → 直接复用缓存
3. 否则：
   - 先让用户选 space（只展示 Top 5 最相近名称）
   - 再让用户选 repo（只展示 Top 5）

## 名称匹配

如果用户输入的是名称而不是 code：

- 对 spaceName / repoName 做模糊匹配（包含、简称、拼音/英文片段）
- 命中多个候选 → 让用户在候选中选一个（列编号）

---

# 🧾 输出格式（统一）

默认 TopK=3，按 score 降序。
若最高 score < 0.2：提示用户"问题可能不够具体"，并给出建议补充点（业务线/场景/对象/时间）。

输出模板：

以下是从知识库检索到的相关片段（Top 3）：

1. 文档：${documentName}
   摘要：${content}
   链接：${documentUrl}
   score：${score}

2. ...

回答策略：

- 先基于片段给出结论/步骤
- 明确引用来自哪些文档
- 如片段冲突，说明冲突并建议以最新/权威文档为准

---

# ❗ 错误处理（必须）

任一步满足以下条件则失败：

- HTTP 非 2xx
- 响应缺少预期字段
- 服务返回错误码/错误信息

失败时：原样返回该步 message / 错误信息（不编造）。
```