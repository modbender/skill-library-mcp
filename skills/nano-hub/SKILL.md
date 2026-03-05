---
name: Nano Hub
description: |
  Nano Banana Pro 提示词模板集合，一站式图像生成中心。
  触发场景：
  - 用户请求生成信息图、角色设计表、电商详情页图
  - 用户提到"香蕉"、"banana"、"nano banana"、"nano hub"
  - 用户需要手绘风格信息图、角色参考图、产品详情页
  - 用户上传图片要求编辑或基于图片生成
---

# Nano Hub

Nano Banana Pro 提示词模板中心，支持文生图和图像编辑。

## 模型信息

- **模型 ID**: `fal-ai/nano-banana-pro`
- **MCP 服务**: `user-速推AI`
- **能力**: 文生图、图像编辑（提供图片时自动切换）

## 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| prompt | string | ✓ | 图像生成/编辑提示词 |
| image_urls | array | - | 输入图片 URL 列表（提供后切换为编辑模式） |
| aspect_ratio | string | - | 宽高比，默认 1:1 |
| resolution | string | - | 分辨率：1K/2K/4K，默认 1K |
| num_images | int | - | 生成数量 1-4，默认 1 |

**宽高比选项**: `21:9`, `16:9`, `3:2`, `4:3`, `5:4`, `1:1`, `4:5`, `3:4`, `2:3`, `9:16`

## 工作流程

### 0. 询问用户需求

当触发此 skill 时，**必须**首先使用 `AskQuestion` 工具询问用户需要生成什么类型的图像：

```json
{
  "title": "图像生成类型选择",
  "questions": [
    {
      "id": "image_type",
      "prompt": "你想生成什么类型的图像？",
      "options": [
        { "id": "infographic", "label": "手绘信息图" },
        { "id": "character", "label": "角色信息图" },
        { "id": "ecommerce", "label": "电商详情页" },
        { "id": "ukiyo-e", "label": "浮世绘闪卡" },
        { "id": "polaroid", "label": "拍立得" },
        { "id": "lego", "label": "乐高小人" },
        { "id": "minimal", "label": "极简线条图" },
        { "id": "pixel", "label": "8位像素" },
        { "id": "beauty", "label": "美妆分镜" },
        { "id": "custom", "label": "自由创作" }
      ],
      "allow_multiple": false
    }
  ]
}
```

根据用户选择，加载对应的提示词模板并继续下一步。

若用户选择 `custom`（自由创作），跳过模板加载，直接询问用户描述具体需求。

### 1. 确定模板和参数

根据用户在 AskQuestion 中的选择 ID，确定对应的提示词模板：

| 选择 ID | 需求类型 | 模板路径 | 宽高比 |
|---------|----------|----------|--------|
| infographic | 手绘信息图 | `references/stacks/infographic.md` | 16:9 |
| character | 角色信息图 | `references/stacks/character-sheet.md` | 16:9 |
| ecommerce | 电商详情页 | `references/stacks/ecommerce.md` | 9:16 |
| ukiyo-e | 浮世绘闪卡 | `references/stacks/ukiyo-e-card.md` | 9:16 |
| polaroid | 拍立得 | `references/stacks/polaroid.md` | 3:4 |
| lego | 乐高小人 | `references/stacks/lego.md` | 3:4 |
| minimal | 极简线条图 | `references/stacks/minimal-comic.md` | 16:9 |
| pixel | 8位像素 | `references/stacks/pixel-art.md` | 1:1 |
| beauty | 美妆分镜 | `references/stacks/beauty-storyboard.md` | 1:1 |
| custom | 自由创作 | 无模板，自由发挥 | 按需 |

查看 `references/Prompt-Menu.md` 获取提示词模板概览。

### 2. 准备图片（如有）

用户上传图片时，使用 catbox.moe 上传获取公开 URL：

```bash
curl -s -F "reqtype=fileupload" -F "fileToUpload=@图片路径" https://catbox.moe/user/api.php
```

**说明**：
- catbox.moe 是免费图床，无需注册
- curl 直接从本地读取文件上传，不受字符限制
- 返回永久可访问的图片 URL（如 `https://files.catbox.moe/xxx.png`）

### 3. 生成提示词

根据 `references/Prompt-Menu.md` 中"子代理"列的标注决定：
- **✓**：委派子代理生成提示词（隔离上下文，提高质量）
- **-**：直接填写模板占位符，无需子代理

**需要子代理时**，使用 Task 工具委派 `generalPurpose` 子代理，提供以下信息：

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

**子代理 prompt 模板**：

```
你是图像生成提示词专家。请根据以下信息生成高质量的生图提示词。

## 用户需求
{用户的具体需求描述}

## 参考图片（如有）
{图片 URL 或"无"}

## 最佳实践模板
请阅读以下文件获取提示词模板和规范：
{模板文件的完整路径，如 /Users/.../references/stacks/infographic.md}

## 输出要求
1. 阅读最佳实践模板，理解提示词结构和规范
2. 结合用户需求，生成完整的生图提示词
3. 如果是批量生成（如电商12张图），返回所有提示词列表
4. 直接返回可用于 API 调用的提示词，无需额外解释
```

**子代理返回格式**：
- 单张图：直接返回提示词字符串
- 批量图：返回编号列表，如 `【第1张】...【第2张】...`

### 4. 生成图像

使用子代理返回的提示词，调用 `submit_task` 提交生图任务：

```json
{
  "model_id": "fal-ai/nano-banana-pro",
  "parameters": {
    "prompt": "子代理生成的提示词",
    "aspect_ratio": "16:9",
    "resolution": "2K"
  }
}
```

图像编辑模式（提供图片时）：

```json
{
  "model_id": "fal-ai/nano-banana-pro",
  "parameters": {
    "prompt": "子代理生成的提示词",
    "image_urls": ["图片URL"],
    "aspect_ratio": "16:9"
  }
}
```

### 5. 获取结果

使用返回的 `task_id` 轮询查询结果，每 **20 秒**查询一次，直到任务完成：

```
1. 调用 get_task 查询状态
2. 如果状态为 pending/processing，等待 20 秒后重试
3. 如果状态为 completed，提取图片 URL
4. 如果状态为 failed，告知用户错误信息
```

### 6. 展示结果

将生成的图片以 markdown 格式展示给用户：`![图片](url)`
