---
name: Fashion Studio
description: 电商服装详情页一站式生成工作流。自动生成模特图、服装搭配图和完整详情页。
---

# Fashion Studio

电商服装详情页一站式生成，从模特选角到完整详情页输出。

## 必需输入

- **模特信息**：年龄、性别、人种、特点、头发等
- **服装图片**：核心单品图片
- **Logo 图片**：品牌标识

## 技术规范

### 图片上传

用户提供的本地图片需先上传到 Catbox 图床获取公开 URL：

```bash
curl -s -F "reqtype=fileupload" -F "fileToUpload=@/path/to/image.png" https://catbox.moe/user/api.php
```

- 返回值：直接返回图片 URL（如 `https://files.catbox.moe/xxxxx.png`）
- 限制：最大 200MB，永久保存
- 无需注册，匿名上传即可

### 图像生成

所有图像通过 MCP 调用 Nano Banana Pro 模型生成：

```
MCP 调用：user-速推AI.submit_task
参数：
  - model_id: "fal-ai/nano-banana-pro"
  - parameters:
      - prompt: 英文提示词
      - image_url: 参考图片 URL（图生图时必填）
      - aspect_ratio: "3:4"（所有生图统一比例）
```

首次使用前调用 `get_model_info` 确认参数要求。

### 用户交互选择

当需要用户做出选择时，**必须**使用 `AskQuestion` 工具提供结构化选项，而非让用户自由输入。

**AskQuestion 工具调用格式：**

```json
{
  "title": "选择标题",
  "questions": [
    {
      "id": "unique_question_id",
      "prompt": "问题描述",
      "options": [
        { "id": "option1", "label": "选项 1 描述" },
        { "id": "option2", "label": "选项 2 描述" }
      ],
      "allow_multiple": false
    }
  ]
}
```

**需要使用 AskQuestion 的场景：**
- 步骤 1：询问用户使用默认模特模板还是自定义
- 步骤 4：生成 3 张模特图后，让用户选择喜欢的方案
- 步骤 7.5：生成 2 套搭配图后，让用户选择最终方案

### 子代理委派

文本生成任务（模特选角、提示词翻译、搭配方案、设计分析、详情页提示词）**必须**使用 Task 工具委派子代理执行。

**Task 工具调用格式：**

```
Task 参数:
- subagent_type: "generalPurpose"
- model: "fast"
- readonly: true
- prompt: 包含以下内容：
  1. 用户需求描述
  2. 图片 URL（如有）
  3. 最佳实践模板路径（让子代理读取）
  4. 要求返回的提示词格式
```

**需要委派子代理的步骤：**
- 步骤 2：生成模特选角方案
- 步骤 3：翻译为英文提示词
- 步骤 6：生成服装搭配方案
- 步骤 8：设计分析
- 步骤 9：生成详情页提示词

### 错误处理

**图像生成失败时：**
1. 检查错误信息，常见原因：提示词过长、图片 URL 无效、余额不足
2. 调整提示词后重试（最多 3 次）
3. 若连续失败，告知用户并询问是否切换备用方案

**用户不满意生成结果时：**
1. 询问具体不满意的方面（构图、色调、风格等）
2. 根据反馈调整提示词重新生成
3. 提供 2-3 个变体供选择
4. 若多次调整仍不满意，建议调整模特/搭配方案从源头修改

## 工作流程

### 第一阶段：模特生成

**步骤 1：收集模特信息**

使用 AskQuestion 询问用户是否使用默认模特模板：

```json
{
  "title": "模特信息设置",
  "questions": [
    {
      "id": "model_info_choice",
      "prompt": "请选择模特信息来源：",
      "options": [
        { "id": "default", "label": "使用默认模板（日系清爽邻家男孩）" },
        { "id": "custom", "label": "我要自定义模特信息" }
      ],
      "allow_multiple": false
    }
  ]
}
```

若用户选择 `default`，使用以下默认模板：

```
默认模特模板：
- 年龄：20-24岁
- 性别：男
- 人种：东亚 (East Asian)
- 特点：干净清爽，皮肤状态好但不是苍白，而是健康的小麦色。手里可能拿着手冲咖啡或露营灯。
- 头发：日系纹理烫 (Permed hair)
- 五官：五官柔和清秀，戴着黑框眼镜或挂在领口，笑容慵懒治愈。
- 穿搭：宽松的大地色系机能马甲，工装短裤，长袜配凉鞋或登山靴。
- 气质：随性、松弛感、潮流、热爱生活的邻家大男孩。
```

若用户选择 `custom`，询问用户提供：年龄、性别、人种、特点、头发、五官、气质等信息。

**步骤 2：生成模特选角方案**

使用 Task 工具委派子代理生成 3 个模特策划方案：

```
Task 参数:
- subagent_type: "generalPurpose"
- model: "fast"
- readonly: true
- prompt: |
    任务：根据用户提供的模特信息，生成 3 个模特策划方案。
    
    用户模特信息：
    {{用户提供的模特信息}}
    
    请先读取最佳实践模板：
    /Users/x013/Desktop/vault/.cursor/skills/服装详情页/references/model-casting-prompt.md
    
    按照模板格式输出 3 个方案（方案 1、方案 2、方案 3）。
```

**步骤 3：翻译为英文提示词**

使用 Task 工具委派子代理将中文方案翻译为英文提示词：

```
Task 参数:
- subagent_type: "generalPurpose"
- model: "fast"
- readonly: true
- prompt: |
    任务：将 3 个中文模特策划方案转化为英文自然语言提示词。
    
    中文策划方案：
    {{步骤 2 生成的 3 个方案}}
    
    请先读取最佳实践模板：
    /Users/x013/Desktop/vault/.cursor/skills/服装详情页/references/prompt-translator.md
    
    按照模板要求，输出 3 段纯文本英文提示词（方案 1 提示词、方案 2 提示词、方案 3 提示词）。
```

**步骤 4：生成模特图片**

通过 MCP 调用 Nano Banana Pro 模型（`submit_task`），使用步骤 3 生成的 3 段英文提示词分别生成 3 张模特图片（比例 3:4）。

生成完成后，使用 AskQuestion 让用户选择喜欢的模特方案：

```json
{
  "title": "模特方案选择",
  "questions": [
    {
      "id": "model_choice",
      "prompt": "请选择你喜欢的模特风格：",
      "options": [
        { "id": "scheme1", "label": "方案 1: {{方案1风格名称}} - {{方案1特点}}" },
        { "id": "scheme2", "label": "方案 2: {{方案2风格名称}} - {{方案2特点}}" },
        { "id": "scheme3", "label": "方案 3: {{方案3风格名称}} - {{方案3特点}}" },
        { "id": "regenerate", "label": "都不满意，重新生成" }
      ],
      "allow_multiple": false
    }
  ]
}
```

若用户选择 `regenerate`，询问具体不满意的方面后调整提示词重新生成。若生成失败，按错误处理流程处理。

### 第二阶段：服装搭配

**步骤 5：收集服装素材**

要求用户提供：
- 服装图片（核心单品）
- Logo 图片（品牌标识）

收到图片后，使用 curl 上传到 Catbox 图床获取公开 URL。

**步骤 6：生成服装搭配方案**

使用 Task 工具委派子代理生成 2 套搭配方案：

```
Task 参数:
- subagent_type: "generalPurpose"
- model: "fast"
- readonly: true
- prompt: |
    任务：根据服装图片，生成 2 套完整搭配方案（Look 1、Look 2）。
    
    服装图片 URL：{{服装图片 URL}}
    服装描述：{{对服装的简要描述}}
    
    请先读取最佳实践模板：
    /Users/x013/Desktop/vault/.cursor/skills/服装详情页/references/outfit-generator.md
    
    按照模板格式输出 Look 1 和 Look 2，每个 Look 需包含搭配思路、包含单品、AI绘图提示词。
```

**步骤 7：生成服装搭配图**

提取 Look 1 和 Look 2 的提示词，分别添加后缀：

```
根据 {{look}} 生成衣服，穿在图 1 模特身上，全身照，商业白景棚拍。
```

通过 MCP 调用 `submit_task`，将用户选择的模特图 URL、服装图 URL 和拼接的提示词传入 Nano Banana Pro 模型，生成 2 张服装搭配图（比例 3:4）。若生成失败或不满意，按错误处理流程处理。

**步骤 7.5：用户选择搭配方案**

生成完成后，使用 AskQuestion 让用户选择搭配方案：

```json
{
  "title": "搭配方案选择",
  "questions": [
    {
      "id": "look_choice",
      "prompt": "请选择你喜欢的搭配方案作为详情页主图：",
      "options": [
        { "id": "look1", "label": "Look 1: {{Look1搭配思路简述}}" },
        { "id": "look2", "label": "Look 2: {{Look2搭配思路简述}}" },
        { "id": "regenerate", "label": "都不满意，重新生成搭配方案" }
      ],
      "allow_multiple": false
    }
  ]
}
```

用户选择后，后续步骤仅使用选中的 Look。若用户选择 `regenerate`，询问具体不满意的方面后返回步骤 6 重新生成。

### 第三阶段：详情页生成

**步骤 8：设计分析**

使用 Task 工具委派子代理进行设计分析：

```
Task 参数:
- subagent_type: "generalPurpose"
- model: "fast"
- readonly: true
- prompt: |
    任务：为服装商品设计电商详情页，进行设计分析。
    
    服装图片 URL：{{服装图片 URL}}
    服装搭配图 URL：{{用户选择的 Look URL}}
    
    请先读取最佳实践模板：
    /Users/x013/Desktop/vault/.cursor/skills/服装详情页/references/design-analysis.md
    
    给自己出 10 个问题，再依次解答。输出格式：Q1-Q10 问答形式。
```

**步骤 9：生成详情页提示词**

使用 Task 工具委派子代理生成 7 页详情页提示词：

```
Task 参数:
- subagent_type: "generalPurpose"
- model: "fast"
- readonly: true
- prompt: | 
    设计分析结果：
    {{步骤 8 的 10 个问答}}
    
    素材 URL：
    - 服装图：{{服装图片 URL}}
    - 搭配图：{{用户选择的 Look URL}}
    - Logo 图：{{Logo URL}}
    
    请先读取最佳实践模板：
    /Users/x013/Desktop/vault/.cursor/skills/服装详情页/references/detail-page-generator.md
```

**步骤 10：生成详情页图片**

通过 MCP 调用 `submit_task`，分批生成 8 页详情页（比例 3:4）：

1. **总览详情页**（1张）：
   - 输入：步骤 9 完整提示词 + [detail-page-brief.md](references/detail-page-brief.md) 提示词
   - 素材 URL：服装图、用户选择的搭配图、Logo 图

2. **分页详情页**（7张）：
   - 输入：步骤 9 每页单独提示词 + [single-page-render.md](references/single-page-render.md) 提示词
   - 素材 URL：服装图、用户选择的搭配图、Logo 图
   - 依次生成第 1-7 页

若某页生成失败或不满意，按错误处理流程单独重试该页。

## 输出

- 1 张总览详情页
- 7 张分页详情页

**总计：8 页电商详情页 + 模特/搭配素材图**
