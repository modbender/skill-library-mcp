---
name: notex-skills
description: 通过工作协同系统 CWork Key，调用 NoteX Skills 将用户素材生成为 8 种 AI 产物（PPT、思维导图、报告、记忆卡片、测验题目、信息图、音频、视频）。支持 Agent 直接调用和脚本两种执行方式，均使用轮询获取结果。
---

# NoteX Skills — 技能说明文档

**版本**: v1.0 | **bizType**: `TRILATERA_SKILLS` | **接入方式**: 轮询（无需回调）

---

## 核心概念

| 名称 | 说明 |
|---|---|
| **CWork Key** | 用户在工作协同系统的 API Key，用于换取 xgToken |
| **xgToken** | 通过 CWork Key 换取的访问令牌，用于后续所有 API 调用 |
| **skill** | 技能类型标识，决定生成的产物形式（见下方路由表） |

---

## 8 种技能路由

| 用户意图 | skill 值 | 预计时间 |
|---|---|---|
| PPT / 演示文稿 / 幻灯片 / 汇报 | `"slide"` | 3~5 分钟 |
| 思维导图 / 脑图 / 知识梳理 | `"mindmap"` | 1~2 分钟 |
| 分析报告 / 总结 / 调研 | `"report"` | 1~3 分钟 |
| 记忆卡片 / 闪卡 / 学习卡 | `"flashcards"` | 1~2 分钟 |
| 测验题目 / 考核 / 练习题 | `"quiz"` | 1~2 分钟 |
| 信息图 / 数据图 / 流程图 | `"infographic"` | 2~4 分钟 |
| 音频 / 播客 / 语音讲解 | `"audio"` | 3~6 分钟 |
| 视频 / 短片 / 介绍视频 | `"video"` | 5~10 分钟 |

> 🛡️ **意图越权（Out of Scope）兜底策略**
> 如果用户要求生成当前**不支持的格式**（如 Excel 表格、Word 文档、PDF 下载等），请明确拒绝并引导转换：
> `Agent："目前 NoteX Skills 仅支持生成演示文稿、思维导图、分析报告等 8 种格式，暂不支持直接生成 [Excel/Word] 文件。您可以考虑将内容生成为『分析报告』或『思维导图』，请问是否需要帮您转换？"`

---

## 完整调用流程

### Step 1：用 CWork Key 换取 xgToken

```http
GET https://cwork-web.mediportal.com.cn/user/login/appkey?appCode=cms_gpt&appKey={CWork Key}
```

**响应**：
```json
{
  "resultCode": 1,
  "data": {
    "xgToken": "bba0ae7b...",
    "userId": "011051631823239433",
    "personId": 11809
  }
}
```

> ✅ 获取到 `xgToken`、`userId`、`personId` 后**缓存到 session**，同一对话中无需再次换取。

---

### Step 2：提交技能生成任务

```http
POST https://notex.aishuo.co/noteX/api/trilateral/autoTask
authorization: BP
personId: {data.personId}
x-user-id: {data.userId}
access-token: {data.xgToken}
Content-Type: application/json
```

```json
{
  "title": "任务标题",
  "bizId": "唯一ID（建议使用时间戳，如：skills_1709000000000）",
  "bizType": "TRILATERA_SKILLS",
  "skills": ["slide"],
  "require": "对生成内容的具体要求（可选，见各技能说明）",
  "sources": [
    {
      "id": "src_001",
      "title": "素材标题",
      "content_text": "用户提供的全部素材内容"
    }
  ]
}
```

> ⚠️ `callbackUrl` 无需传入，TRILATERA_SKILLS 使用轮询方式获取结果。

**成功响应**：
```json
{ "resultCode": 1, "data": { "noteBook_id": "nb-xxx", "taskId": ["task-xxx"] } }
```

---

### Step 3：轮询任务状态

```http
GET https://notex.aishuo.co/noteX/api/trilateral/taskStatus/{taskId}
```

**响应**：
```json
{
  "resultCode": 1,
  "data": {
    "task_id": "task-xxx",
    "task_status": "COMPLETED",
    "url": "https://notex.aishuo.co/?skillsopen=task-xxx"
  }
}
```

- `task_status`：`PENDING`（生成中）/ `COMPLETED`（完成）/ `FAILED`（失败）
- **完成后**：将 URL 追加 `&token={xgToken}` 后返回给用户，即为最终预览链接
- **轮询规则**：每 **1 分钟**轮询一次，最多 **20 次**（**20 分钟超时上限**）
- 未完成时静默等待，不向用户汇报轮询进度

---

## 各技能的 `require` 字段说明

> 核心输入是 `sources[].content_text`（素材内容）。`require` 是补充的风格/格式要求，按各技能需要填写：

| skill | require 必要程度 | 典型 require 内容 |
|---|---|---|
| `slide` | ⚠️ 风格必填 | `"商务简约风格，蓝白配色，约10页"` |
| `mindmap` | 可不填 | `"按场景分类展开"` 或留空 |
| `report` | 可选 | `"市场竞争分析，约2000字"` |
| `flashcards` | 可选 | `"生成20张，问答形式"` |
| `quiz` | 可选 | `"15道题，单选10道，判断5道"` |
| `infographic` | ⚠️ 风格必填 | `"数据对比形式，蓝白科技感配色"` |
| `audio` | 可选 | `"轻松科普风格，约3分钟，普通话"` |
| `video` | 可选 | `"专业科普风格，约1分30秒，普通话旁白"` |

---

## 各技能用户引导脚本

### slide — 演示文稿（PPT）

**需要收集**：素材内容（必须）+ 风格描述（必须）

```
首次使用：
Agent："请提供您的工作协同 Key，并描述 PPT 的主题与内容要点，以及风格要求（如：商务简约、科技感、学术等）。"

再次使用：
Agent："请描述 PPT 的主题与内容要点，以及希望的风格（如：商务简约蓝白、清新绿色等）。"

如果用户未提供风格，追问一次：
Agent："请问 PPT 您希望是什么风格？（如：商务简约、科技感、学术严谨、活泼清新等）"
```

---

### mindmap — 思维导图

**需要收集**：素材内容（必须），无需追问其他

```
首次使用：
Agent："请提供您的工作协同 Key，以及需要梳理的内容素材。"

再次使用：
Agent："请提供需要梳理为思维导图的内容素材。"
```

> 系统会自动按内容结构生成导图，无需用户额外说明分类方式。

---

### report — 分析报告

**需要收集**：素材内容（必须）+ 报告类型（可选，用户通常会自然说明）

```
首次使用：
Agent："请提供您的工作协同 Key，以及报告的素材内容。您可以说明报告类型（如：市场分析、竞争分析、季度总结等），若无特别要求系统会自动判断。"

再次使用：
Agent："请提供报告的素材内容，以及报告类型（可选）。"
```

---

### flashcards — 记忆卡片

**需要收集**：素材内容（必须）+ 数量（可选）

```
首次使用：
Agent："请提供您的工作协同 Key，以及需要制作成记忆卡片的学习内容。您可以说明期望的卡片数量（如：20张），若未说明系统会自动判断。"

再次使用：
Agent："请提供需要制作成记忆卡片的内容，以及期望卡片数量（可选）。"
```

---

### quiz — 测验题目

**需要收集**：素材内容（必须）+ 题目数量/题型（可选）

```
首次使用：
Agent："请提供您的工作协同 Key，以及考核的内容素材。您可以说明题目数量和题型（如：15道，单选10道、判断5道），若未说明系统会自动分配。"

再次使用：
Agent："请提供考核内容素材，以及题目数量和题型要求（可选）。"
```

---

### infographic — 信息图

**需要收集**：素材内容（必须）+ 视觉风格（必须）

```
首次使用：
Agent："请提供您的工作协同 Key，以及需要可视化的数据或内容，以及希望的图表风格（如：蓝白科技感、清新渐变等）。"

再次使用：
Agent："请提供需要可视化的内容，以及图表风格偏好。"

如果用户未提供风格，追问一次：
Agent："请问您希望信息图是什么配色风格？（如：蓝白科技感、橙色活力、绿色清新等）"
```

---

### audio — 音频播客

**需要收集**：素材内容（必须）+ 风格/时长（可选，有默认值）

```
首次使用：
Agent："请提供您的工作协同 Key，以及需要转为音频的内容素材。您可以说明讲解风格（正式/轻松科普）和期望时长，若未说明默认采用轻松科普风格。"

再次使用：
Agent："请提供音频的内容素材，以及讲解风格和时长要求（可选，默认轻松科普）。"
```

---

### video — 视频

**需要收集**：素材内容（必须）+ 风格/时长（可选，有默认值）

```
首次使用：
Agent："请提供您的工作协同 Key，以及需要制作成视频的内容素材。您可以说明视频风格（专业/轻松/科普）和期望时长，若未说明系统会自动处理。"

再次使用：
Agent："请提供视频的内容素材，以及风格和时长要求（可选）。"
```

> ⚠️ 视频生成含渲染阶段，耗时较长（5~10 分钟），开始时需明确告知用户预计等待时间。

---

## 对话规范（Agent 执行）

⚠️ **核心原则**：Step 1～3 的所有 API 调用必须**后台静默执行**，绝对不向用户汇报中间步骤（不说"正在换取 Token"、"正在提交任务"等），只在开始时通知一次、完成时给出结果。

---

### CWork Key 处理策略

- **首次使用**（session 无缓存）：主动向用户索取 CWork Key
- **再次使用**（session 有缓存）：直接跳过，**绝对不要**重复索要
- **用户主动更新 Key**：更新本地记录，下次请求使用新 Key 换取 Token

---

### 首次使用（无 session 缓存）

```
Agent："请提供您的工作协同 Key（CWork Key），以及您想生成的内容素材和具体要求。"
```

### 再次使用（session 有缓存）

```
Agent："请提供您想生成的内容素材和具体要求。"
```

---

### 等待与完成提示

不同技能的完整示例：

**slide（PPT）**：
```
（开始时）Agent："✅ 已收到请求，演示文稿正在后台生成中，预计 3~5 分钟，请稍等..."
（静默轮询，期间不做任何回复）
（完成后）Agent："🎉 演示文稿已生成！点击以下链接查看与编辑：
{url}&token={xgToken}"
```

**mindmap（思维导图）**：
```
（开始时）Agent："✅ 思维导图正在生成中，预计 1~2 分钟..."
（完成后）Agent："🎉 思维导图已生成！{url}&token={xgToken}"
```

**audio（音频）**：
```
（开始时）Agent："✅ 音频正在生成中（含语音合成），预计 3~6 分钟，请耐心等待..."
（完成后）Agent："🎉 音频已生成！{url}&token={xgToken}"
```

**video（视频）**：
```
（开始时）Agent："✅ 视频正在生成中（含渲染阶段），预计 5~10 分钟，请耐心等待..."
（静默轮询 5 分钟后若仍未完成）
Agent："⏳ 视频渲染比较耗时，AI 仍在努力运算中，请再耐心稍等片刻..."
（完成后）Agent："🎉 视频已生成！{url}&token={xgToken}"
```

---

## 错误处理

| 场景 | 处理方式 |
|---|---|
| CWork Key 换取失败（resultCode≠1） | 提示用户重新提供 Key |
| 任务提交失败 | 提示错误信息，建议检查素材内容后重试 |
| `task_status: FAILED` | 提示生成失败，建议补充内容后重试 |
| 轮询超时（超过 20 分钟/20 次） | 提示稍后重试 |

---

## 测试脚本（支持脚本执行的环境）

脚本路径：`docs/skills/scripts/skills-run.js`

包含完整 3 步流程：获取 xgToken → 提交任务 → 自动轮询直到完成 → 输出预览链接。

**使用方式**：
```bash
node docs/skills/scripts/skills-run.js \
  --skill <技能ID> \
  --key <CWork Key> \
  --title "内容标题" \
  --content "素材内容" \
  [--require "可选的风格要求"]
```

**示例**：
```bash
# 生成 PPT
node docs/skills/scripts/skills-run.js \
  --skill slide \
  --key QBDrI4so***qClt4 \
  --title "口腔行业AI应用趋势" \
  --content "AI诊断准确率93%，预约效率提升40%，种植精度0.3mm" \
  --require "商务简约风格，蓝白配色"

# 生成思维导图
node docs/skills/scripts/skills-run.js \
  --skill mindmap \
  --key QBDrI4so***qClt4 \
  --title "种植牙知识体系" \
  --content "种植牙分为术前准备、手术植入、愈合修复三阶段..."

# 生成视频
node docs/skills/scripts/skills-run.js \
  --skill video \
  --key QBDrI4so***qClt4 \
  --title "种植牙流程介绍" \
  --content "种植牙是目前最接近天然牙的修复方案..." \
  --require "专业科普风格，约1分30秒，普通话旁白"
```

**输出示例**：
```
🎉 演示文稿生成完成！
   查看链接：https://notex.aishuo.co/?skillsopen=task-xxx&token=bba0ae7b...
```

> 不支持脚本执行的环境（如 Agent 对话模式），直接按照上方「完整调用流程」的 Step 1~3 依次调用 HTTP 接口即可，逻辑完全一致。
