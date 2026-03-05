---
name: fal-llms-txt
description: 获取 fal.ai 模型系列的所有变体及其 llms.txt 链接。当用户提供 fal.ai 模型链接并要求获取 llms.txt、查看模型文档、或查看模型变体时使用此 skill。
category: tool
tags: [fal, llms.txt, 模型文档, 模型变体]
featured: false
---

# Fal 模型 llms.txt 链接获取

输入一个 fal.ai 模型页面链接，自动发现该模型下的所有变体（如 pro/standard、image-to-video/text-to-video），输出每个变体对应的 llms.txt 文档链接。

## 触发场景

- 用户提供 fal.ai 模型链接，要求获取 llms.txt
- 用户想查看某个 fal 模型系列的所有变体
- 用户想获取 fal 模型的 API 文档
- 用户提到 "llms.txt"、"模型文档"、"模型变体" 并涉及 fal.ai 链接

## 前置输入

用户需提供一个 fal.ai 模型页面链接，格式如：

```
https://fal.ai/models/fal-ai/minimax/hailuo-2.3-fast/standard/image-to-video
```

## 核心原理

- fal.ai 模型页面有一个下拉菜单，包含同系列的所有模型变体
- 每个变体有独立的 URL 路径（路径可能不同，如 `hailuo-2.3-fast` vs `hailuo-2.3`）
- 在模型页面 URL 末尾追加 `/llms.txt` 即可获取该变体的 LLM 文档

## 工作流

### 步骤 1：导航到模型页面

使用 `browser_navigate` 打开用户提供的 fal.ai 模型链接。

```
browser_navigate → 用户提供的 URL
```

### 步骤 2：获取页面快照，定位下拉菜单

使用 `browser_snapshot` 获取页面结构。找到下拉菜单按钮，它的特征是：

- `role: button`
- `states: [collapsed]`
- 名称通常包含模型变体描述，如 "Fast Image To Video (standard)"

**注意**：如果页面上没有这样的下拉按钮，说明该模型只有单一变体，直接跳到步骤 6。

### 步骤 3：点击下拉菜单展开

使用 `browser_click` 点击该按钮，展开下拉菜单。

### 步骤 4：读取所有变体

展开后，再次使用 `browser_snapshot`，从中提取所有 `role: menuitem` 元素。每个 menuitem 的 `name` 就是一个模型变体名称。

**示例 snapshot 片段**：

```yaml
- role: menuitem
  name: Fast Image To Video (pro)
  ref: e71
- role: menuitem
  name: Fast Image To Video (standard)
  ref: e72
- role: menuitem
  name: Image To Video (pro)
  ref: e73
- role: menuitem
  name: Text To Video (pro)
  ref: e74
- role: menuitem
  name: Image To Video (standard)
  ref: e75
- role: menuitem
  name: Text To Video (standard)
  ref: e76
```

记录下所有 menuitem 的名称和 ref，形成待处理列表。

### 步骤 5：逐个点击变体获取实际 URL

对每个 menuitem，执行以下操作：

1. **点击 menuitem**：`browser_click` 使用对应的 ref
2. **等待导航**：`browser_wait_for` 等待 2 秒
3. **获取 URL**：`browser_snapshot` 读取 `Page URL` 字段

**关键**：必须通过实际导航获取 URL，不能靠猜测。因为不同变体的路径可能不一致（如 `hailuo-2.3-fast` 和 `hailuo-2.3` 是不同路径）。

4. **记录信息**：保存 { 变体名称, 页面 URL, Model ID }

   - Model ID = URL 中 `/models/` 之后的路径部分
   - 例如 URL `https://fal.ai/models/fal-ai/minimax/hailuo-2.3/pro/text-to-video`
   - Model ID = `fal-ai/minimax/hailuo-2.3/pro/text-to-video`

5. **重新展开下拉菜单**：每次导航后下拉菜单会关闭，需要重新点击展开按钮（ref 为 e6，即页面上的下拉按钮）再点击下一个 menuitem

### 步骤 6：构建 llms.txt 链接

对每个变体的页面 URL，拼接 `/llms.txt` 后缀：

```
llms.txt URL = 页面 URL + "/llms.txt"
```

例如：
```
页面 URL:     https://fal.ai/models/fal-ai/minimax/hailuo-2.3/pro/text-to-video
llms.txt URL: https://fal.ai/models/fal-ai/minimax/hailuo-2.3/pro/text-to-video/llms.txt
```

### 步骤 7：输出结果

以 Markdown 表格输出所有变体信息：

```markdown
| 序号 | 变体名称 | Model ID | llms.txt 链接 |
|------|---------|----------|--------------|
| 1 | Fast Image To Video (pro) | fal-ai/minimax/hailuo-2.3-fast/pro/image-to-video | https://fal.ai/models/fal-ai/minimax/hailuo-2.3-fast/pro/image-to-video/llms.txt |
| 2 | ... | ... | ... |
```

### 步骤 8（可选）：验证 llms.txt 可访问

使用 `WebFetch` 工具请求每个 llms.txt 链接，确认返回内容正常。重点检查：

- 是否返回有效的 Markdown 内容
- Model ID 字段是否与预期一致
- 定价信息是否存在

## 完整示例

### 输入

```
https://fal.ai/models/fal-ai/minimax/hailuo-2.3-fast/standard/image-to-video
```

### 输出

| 序号 | 变体名称 | Model ID | llms.txt 链接 |
|------|---------|----------|--------------|
| 1 | Fast Image To Video (pro) | `fal-ai/minimax/hailuo-2.3-fast/pro/image-to-video` | https://fal.ai/models/fal-ai/minimax/hailuo-2.3-fast/pro/image-to-video/llms.txt |
| 2 | Fast Image To Video (standard) | `fal-ai/minimax/hailuo-2.3-fast/standard/image-to-video` | https://fal.ai/models/fal-ai/minimax/hailuo-2.3-fast/standard/image-to-video/llms.txt |
| 3 | Image To Video (pro) | `fal-ai/minimax/hailuo-2.3/pro/image-to-video` | https://fal.ai/models/fal-ai/minimax/hailuo-2.3/pro/image-to-video/llms.txt |
| 4 | Image To Video (standard) | `fal-ai/minimax/hailuo-2.3/standard/image-to-video` | https://fal.ai/models/fal-ai/minimax/hailuo-2.3/standard/image-to-video/llms.txt |
| 5 | Text To Video (pro) | `fal-ai/minimax/hailuo-2.3/pro/text-to-video` | https://fal.ai/models/fal-ai/minimax/hailuo-2.3/pro/text-to-video/llms.txt |
| 6 | Text To Video (standard) | `fal-ai/minimax/hailuo-2.3/standard/text-to-video` | https://fal.ai/models/fal-ai/minimax/hailuo-2.3/standard/text-to-video/llms.txt |

## 常见问题

### Q: 模型页面没有下拉菜单怎么办？

说明该模型只有单一变体。直接使用当前页面 URL 拼接 `/llms.txt` 即可。

### Q: 点击 menuitem 后页面没有跳转？

等待时间可能不够。增加 `browser_wait_for` 的等待时间到 3-5 秒，再用 `browser_snapshot` 检查 URL 是否变化。

### Q: 某个 llms.txt 链接返回 404？

该变体可能尚未提供 llms.txt 文档。在输出表格中标记为"不可用"即可。

## 定价

**免费** - 此 skill 仅使用浏览器操作，不消耗任何积分。
