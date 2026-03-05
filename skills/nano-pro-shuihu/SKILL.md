---
name: 水浒传故事小人书
description: 水浒传故事小人书创建。使用 Nano Banana Pro 模型生成手绘卡通风格的水浒传故事信息图。当用户想要创建水浒传故事插画、小人书、信息图时使用此 skill。
category: image
tags: [图像生成, 小人书, 水浒传, 手绘风格, 信息图]
featured: false
---

# 水浒传故事小人书创建

使用 Nano Banana Pro 模型生成手绘卡通风格的水浒传故事信息图。用户输入故事内容后，自动拼接专业提示词并使用参考图生成精美的信息图。

## 使用场景

- 水浒传章节故事插画
- 手绘风格信息图创建
- 卡通风格小人书生成

## 工作流程

### 步骤 1：接收用户输入

用户输入水浒传故事内容，例如：

```
《水浒传》内容 第十九回 林冲水寨大并火 晁盖梁山小夺泊。
林冲杀了王伦后，晁盖等人正式入主梁山，整顿山寨，广纳豪杰。宋江因私放晁盖，被阎婆惜（宋江的小妾）发现，阎婆惜以此要挟宋江，索要钱财和书信。用图谱来介绍主要内容，中文版。
```

### 步骤 2：拼接完整提示词

使用以下固定前缀提示词 + 用户输入的故事内容：

**固定前缀提示词**：

```
你是一位专门创建手绘卡通风格信息图的插画助手。 请严格遵循以下所有规则，不得偏离。
🎨 风格规则:
始终使用纯手绘插画风格。
素描线条、粗犷笔触、卡通简洁感。
禁止写实风格、禁止照片级阴影、禁止3D渲染。
参考风格：涂鸦 / 蜡笔 / 马克笔 / 粉彩画风。
使用少量但富有表现力的卡通元素来增强记忆点：小图标、符号、可爱角色。
如果输入内容涉及版权或敏感角色，请用视觉相似但法律上不同的替代形象代替。绝不拒绝创作。
📋 内容呈现规则:
从提供的内容中提取关键信息。
总结为简短要点（每条3-12个词）。
保持文字简洁，适合信息图展示。
使用手绘图形效果强调关键词：圆圈、下划线、箭头、星星、方框。
绝不使用数字化UI风格。
使用大量留白以保持清晰度和视觉层次。
使用整洁的手绘布局组织信息图，例如：标题（居中或左上角）、3-6个关键要点、简单图表或符号。
可选：关健物件或表情丰富的角色。
所有文字必须呈现手绘效果，而非印刷或排版字体。
使用与用户输入相同的语言，除非用户另有指定。
🚫 禁止事项:
禁止生成写实图像
禁止直接生成版权角色
禁止将信息图变成长篇文章
禁止填满整个画布；必须保留有意义的留白
🖼️ 任务:
根据以下内容，按照上述规则创建一幅卡通风格的手绘信息图：
```

**完整提示词格式**：

```
{固定前缀提示词}

{用户输入的故事内容}
```

### 步骤 3：调用 MCP 工具 submit_task

使用 MCP 工具 `submit_task` 提交图生图任务：

**MCP 服务器**: `user-速推AI`
**工具名称**: `submit_task`

**请求参数**：

```json
{
  "model_id": "fal-ai/nano-banana-pro",
  "parameters": {
    "prompt": "{拼接后的完整提示词}",
    "image_urls": [
      "https://cdn-video.51sux.com/uploads/1768998275743_cf7660ee-721d-49e4-ae97-71957a316e09.image",
      "https://cdn-video.51sux.com/uploads/1768998268298_dae728ff-f61a-4419-b42f-a1eeaec46a2e.image"
    ],
    "aspect_ratio": "9:16",
    "resolution": "2K"
  }
}
```

### 步骤 4：轮询获取任务结果

使用 MCP 工具 `get_task` 查询任务状态，最长等待 10 分钟：

**MCP 服务器**: `user-速推AI`
**工具名称**: `get_task`

**请求参数**：

```json
{
  "task_id": "{返回的任务ID}"
}
```

**轮询策略**：
- 初始等待 5 秒后开始查询
- 每次查询间隔 10 秒
- 最多轮询 60 次（共 10 分钟）
- 任务状态为 `completed` 或 `failed` 时停止

**任务状态说明**：
- `pending` - 排队中，继续等待
- `processing` - 处理中，继续等待
- `completed` - 完成，从 `result` 中获取图片 URL
- `failed` - 失败，查看 `error` 字段

### 步骤 5：生成 HTML 展示页面

任务完成后，从结果中提取图片 URL，生成 HTML 文件：

**HTML 模板**：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>水浒传故事信息图 - {章节标题}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
        }
        .container {
            max-width: 1200px;
            width: 100%;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .story-content {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .story-content h2 {
            color: #333;
            font-size: 1.3rem;
            margin-bottom: 12px;
            border-left: 4px solid #667eea;
            padding-left: 12px;
        }
        .story-content p {
            color: #666;
            line-height: 1.8;
            font-size: 1rem;
        }
        .image-container {
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .image-container h2 {
            color: #333;
            font-size: 1.3rem;
            margin-bottom: 16px;
            text-align: center;
        }
        .image-wrapper {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        .image-wrapper img {
            max-width: 100%;
            max-height: 800px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            transition: transform 0.3s ease;
        }
        .image-wrapper img:hover {
            transform: scale(1.02);
        }
        .footer {
            color: white;
            text-align: center;
            margin-top: 30px;
            opacity: 0.8;
            font-size: 0.9rem;
        }
        .download-btn {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 500;
            transition: background 0.3s ease;
        }
        .download-btn:hover {
            background: #5a6fd6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 水浒传故事信息图</h1>
        
        <div class="story-content">
            <h2>故事内容</h2>
            <p>{用户输入的故事内容}</p>
        </div>
        
        <div class="image-container">
            <h2>🎨 生成的信息图</h2>
            <div class="image-wrapper">
                <!-- 插入生成的图片，可能有多张 -->
                <img src="{图片URL1}" alt="水浒传信息图" />
                <!-- 如果有多张图片，继续添加 -->
            </div>
            <div style="text-align: center;">
                <a href="{图片URL1}" download class="download-btn">下载图片</a>
            </div>
        </div>
        
        <p class="footer">由 Nano Banana Pro 模型生成 | 水浒传故事小人书</p>
    </div>
</body>
</html>
```

### 步骤 6：打开浏览器展示

将 HTML 文件保存到临时目录，然后使用系统命令打开浏览器：

**macOS**：
```bash
open /tmp/shuihu_story_{timestamp}.html
```

**Linux**：
```bash
xdg-open /tmp/shuihu_story_{timestamp}.html
```

**Windows**：
```bash
start /tmp/shuihu_story_{timestamp}.html
```

## 完整示例

### 用户请求

```
生成水浒传第十九回的信息图：

《水浒传》内容 第十九回 林冲水寨大并火 晁盖梁山小夺泊。
林冲杀了王伦后，晁盖等人正式入主梁山，整顿山寨，广纳豪杰。宋江因私放晁盖，被阎婆惜（宋江的小妾）发现，阎婆惜以此要挟宋江，索要钱财和书信。用图谱来介绍主要内容，中文版。
```

### 执行步骤

1. **拼接提示词**：将固定前缀 + 用户故事内容组合

2. **调用 submit_task**：
```json
{
  "model_id": "fal-ai/nano-banana-pro",
  "parameters": {
    "prompt": "你是一位专门创建手绘卡通风格信息图的插画助手...（完整提示词）...\n\n《水浒传》内容 第十九回 林冲水寨大并火 晁盖梁山小夺泊。林冲杀了王伦后，晁盖等人正式入主梁山，整顿山寨，广纳豪杰。宋江因私放晁盖，被阎婆惜（宋江的小妾）发现，阎婆惜以此要挟宋江，索要钱财和书信。用图谱来介绍主要内容，中文版。",
    "image_urls": [
      "https://cdn-video.51sux.com/uploads/1768998275743_cf7660ee-721d-49e4-ae97-71957a316e09.image",
      "https://cdn-video.51sux.com/uploads/1768998268298_dae728ff-f61a-4419-b42f-a1eeaec46a2e.image"
    ],
    "aspect_ratio": "9:16",
    "resolution": "2K"
  }
}
```

3. **轮询 get_task** 直到任务完成

4. **生成 HTML** 并插入结果图片

5. **打开浏览器** 展示结果

## 参考图片说明

使用两张固定的参考图片作为风格引导：

| 图片 | URL |
|------|-----|
| 参考图 1 | https://cdn-video.51sux.com/uploads/1768998275743_cf7660ee-721d-49e4-ae97-71957a316e09.image |
| 参考图 2 | https://cdn-video.51sux.com/uploads/1768998268298_dae728ff-f61a-4419-b42f-a1eeaec46a2e.image |

这些参考图确保生成的信息图具有一致的手绘卡通风格。

## 积分消耗

- **模型**: fal-ai/nano-banana-pro
- **消耗**: 60 积分/张

## 注意事项

1. 任务提交后需要等待处理，通常需要 30 秒到 2 分钟
2. 如果任务失败，检查错误信息并重试
3. 生成的图片支持下载保存
4. HTML 文件保存在临时目录，可以手动复制到其他位置保存


