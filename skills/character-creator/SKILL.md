---
name: character-creator
description: 创建AI角色的完整流程，包括生成详细角色描述、文生图肖像和多角度参考图。使用即梦4.5模型。当用户要求创建角色、生成人物立绘、制作角色参考图、或需要多角度人物图时使用此技能。
---

# 角色创建器

使用即梦4.5 (Seedream) 模型创建完整的角色资产，包括详细描述、主肖像图和10个不同角度的参考图。每个阶段生成HTML展示页面。

## 模型配置

| 用途 | 模型ID |
|------|--------|
| 文生图 | `fal-ai/bytedance/seedream/v4.5/text-to-image` |
| 图生图 | `fal-ai/bytedance/seedream/v4.5/text-to-image` + `image_url` 参数 |

## 创建流程

### 第一步：生成详细角色描述

根据用户简短描述，扩展为详细角色描述：

**必须包含要素**：年龄/性别、面部特征、发型发色、体型身高、服装、气质、画风

**描述模板**：
```
[画风]，[年龄][性别]，[体型]，[面部特征]，[发型发色]，[服装]，[气质]，
正面站立，面对镜头，全身像，双手自然下垂，纯白色背景，高清细节
```

### 第二步：生成主肖像图

```
工具: user-sora2-mcp / create_image_task
参数:
  model_id: "fal-ai/bytedance/seedream/v4.5/text-to-image"
  prompt: [详细角色描述]
  aspect_ratio: "3:4"
```

使用 `get_task` 轮询结果，间隔5-10秒。

### 第三步：生成肖像图HTML展示页面

读取模板 `assets/templates/portrait.html`，替换占位符后保存为 `character-portrait.html`，打开浏览器展示。

**占位符说明**：

| 占位符 | 替换内容 |
|--------|----------|
| `{{CHARACTER_NAME}}` | 角色名称（从描述提取或用户指定） |
| `{{CHARACTER_DESCRIPTION}}` | 角色描述文本 |
| `{{PORTRAIT_URL}}` | 生成的肖像图URL |
| `{{GENERATED_TIME}}` | 生成时间 |

### 第四步：生成多角度参考图

使用主肖像图作为参考，批量生成10个角度：

| 序号 | 角度 | Prompt后缀 |
|------|------|-----------|
| 1 | 正面特写 | 正面特写，面部清晰，胸部以上 |
| 2 | 左侧45度 | 左侧45度角，半侧面 |
| 3 | 右侧45度 | 右侧45度角，半侧面 |
| 4 | 左侧面 | 左侧面90度，完整侧脸 |
| 5 | 右侧面 | 右侧面90度，完整侧脸 |
| 6 | 背面 | 背面视角，展示发型和背部 |
| 7 | 俯视 | 俯视角度，从上往下看 |
| 8 | 仰视 | 仰视角度，从下往上看 |
| 9 | 四分之三侧身 | 四分之三侧身 |
| 10 | 动态姿势 | 自然行走或动态姿势 |

```
工具: user-sora2-mcp / create_image_task
参数:
  model_id: "fal-ai/bytedance/seedream/v4.5/text-to-image"
  prompt: "[基础角色描述]，[角度描述]，保持角色一致性，简洁背景"
  aspect_ratio: "1:1"
  image_url: "[主肖像图URL]"
```

可并行创建多个任务。

### 第五步：生成多角度HTML画廊页面

读取模板 `assets/templates/gallery.html`，替换占位符后保存为 `character-gallery.html`，打开浏览器展示。

**占位符说明**：

| 占位符 | 替换内容 |
|--------|----------|
| `{{CHARACTER_NAME}}` | 角色名称 |
| `{{CHARACTER_DESCRIPTION}}` | 角色描述 |
| `{{PORTRAIT_URL}}` | 主肖像图URL |
| `{{GALLERY_ITEMS}}` | 画廊项HTML（见下方格式） |
| `{{GENERATED_TIME}}` | 生成时间 |

**画廊项格式**（为每个角度生成）：
```html
<div class="gallery-item">
    <img src="[角度图URL]" alt="[角度名称]">
    <div class="label">[角度名称] <span>#[序号]</span></div>
</div>
```

## 文件结构

```
~/.cursor/skills/character-creator/
├── SKILL.md
└── assets/
    └── templates/
        ├── portrait.html    # 肖像展示模板
        └── gallery.html     # 多角度画廊模板
```

## 输出文件

| 文件名 | 说明 |
|--------|------|
| `character-portrait.html` | 肖像图展示页面 |
| `character-gallery.html` | 多角度画廊页面 |

## 工作流程

```
用户描述 → 生成详细描述 → 生成肖像图 → 创建portrait.html并展示
                                    ↓
              完成 ← 创建gallery.html并展示 ← 批量生成10张角度图
```

## 注意事项

1. 肖像图完成后立即生成HTML展示，不等角度图
2. 生成多角度时必须传入 `image_url` 参数
3. 轮询间隔5-10秒

## 示例

用户输入："创建一个赛博朋克女黑客"

生成描述：
```
赛博朋克风格，25岁亚洲女性，身材纤细，锐利丹凤眼配荧光蓝虹膜，
高挺鼻梁，不对称短发渐变紫色，黑色皮衣配霓虹装饰，左臂机械义肢，
表情冷峻，正面站立，面对镜头，全身像，双手自然下垂，纯白背景，高清细节
```
