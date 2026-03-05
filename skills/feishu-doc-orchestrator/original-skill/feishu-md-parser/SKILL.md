---
name: feishu-md-parser
description: Markdown解析子技能 - 将Markdown文件解析为飞书文档块格式，输出JSON文件，支持25种块类型映射，**现在支持图片上传**。
---

# Markdown 解析子技能

## 职责
将 Markdown 文件解析为飞书文档块格式，输出 JSON 文件。

## 输入
- Markdown 文件路径（命令行参数或配置文件）

## 输出
- `output/blocks.json` - 解析后的块数据
- `output/metadata.json` - 解析元数据（块数量、表格数量等）

## 工作流程

### 第一步：读取 Markdown 文件
从指定路径读取 Markdown 文件内容。

### 第二步：解析 Markdown 内容
- 解析标题（# - ######）
- 解析列表（无序、有序）
- 解析表格
- 解析代码块
- 解析引用块
- 解析粗体/斜体
- 解析分割线
- **解析图片** ⭐ 新增功能 ⭐

### 第三步：清理内容
- 移除零宽字符（`\u200b`, `\u200c`, `\u200d`, `\ufeff`）
- 清理表格单元格内容
- 清理粗体标记

### 第四步：输出 JSON 文件
将解析结果保存到 `output/blocks.json`。

## 数据格式

### blocks.json 格式
```json
{
  "blocks": [
    {
      "block_type": 2,
      "text": {
        "elements": [{"text_run": {"content": "文本内容"}}],
        "style": {}
      }
    },
    {
      "block_type": 27,
      "image": {
        "token": "D:/path/to/image.png",
        "width": 0,
        "height": 0
      },
      "local_path": "D:\\00-work_study\\path\\to\\image.png"
    }
  }
  ],
  "metadata": {
    "total_blocks": 50,
    "heading_count": 10,
    "table_count": 5,
    "list_count": 3,
    "code_count": 0,
    "callout_count": 0,
    "image_count": 1
  }
}
```

## 使用方式

### 命令行
```bash
python scripts/md_parser.py input.md output/blocks.json
```

### 作为子技能被调用
```python
result = call_skill("feishu-md-parser", {
    "input_file": "path/to/markdown.md",
    "output_dir": "workflow/step1_parse"
})
# 返回: {"blocks_file": "workflow/step1_parse/blocks.json"}
```

## 图片上传支持说明

### Markdown 图片语法支持
支持两种图片格式：

1. **本地图片路径**（将上传到飞书）：
   ```markdown
   ![alt text](D:/absolute/path/to/image.png)
   ```

2. **网络图片 URL**（仅显示链接，不上传）：
   ```markdown
   ![alt text](https://example.com/image.png)
   ```

### 解析实现细节
- 检测 `![alt](url)` 语法
- 提取 `local_path` 字段：`D:\\00-work_study\\AIsthdy\\test-claude\\test_upload.png`
- 如果是本地路径且文件存在，则保存到 `local_path` 字段
- 支持的图片格式：`.png`, `.jpg`, `.jpeg`, `.gif`

### 块类型参考
| block_type | 名称 | 说明 |
|------------|------|------|
| 2 | text | ✅ | 普通文本 |
| 3-8 | heading1-6 | ✅ | 一到六级标题 |
| 12 | bullet | ✅ | 无序列表 |
| 13 | ordered | ✅ | 有序列表 |
| 14 | code | ✅ | 代码块 |
| 15 | quote | ✅ | 引用块 |
| 17 | todo | ✅ | 待办事项 |
| 19 | callout | ✅ 高亮块 |
| 22 | divider | ✅ | 分割线 |
| 27 | image | ✅ | 图片块（**支持本地图片上传**） |
| 31 | table | ✅ 表格（特殊处理） |

## 图片上传流程（由 feishu-block-adder 实现）
图片块创建 → 上传文件 → 设置 token，三步自动完成
