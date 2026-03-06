---
name: mineru
description: 用 MinerU API 解析 PDF/Word/PPT/图片为 Markdown，支持公式、表格、OCR。适用于论文解析、文档提取。
---

# 📄 MinerU - 文档解析神器

**OpenDataLab 出品**

> PDF/Word/PPT/图片 → 结构化 Markdown，公式表格全保留！

---

## 🔗 资源链接

| 资源 | 链接 |
|------|------|
| **官网** | https://mineru.net/ |
| **API 文档** | https://mineru.net/apiManage/docs |
| **GitHub** | https://github.com/opendatalab/MinerU |

---

## 🎯 功能

### 支持的文件类型

| 类型 | 格式 |
|------|------|
| 📕 **PDF** | 论文、书籍、扫描件 |
| 📝 **Word** | .docx |
| 📊 **PPT** | .pptx |
| 🖼️ **图片** | .jpg, .png (OCR) |

### 核心优势

1. **公式完美保留** - LaTeX 格式输出
2. **表格结构识别** - 复杂表格也能搞定
3. **多语言 OCR** - 中英文混排无压力
4. **版面分析** - 多栏、图文混排自动处理

---

## 🚀 API 使用 (v4)

### 认证

```bash
# Header 认证
Authorization: Bearer {YOUR_API_KEY}
```

### 单文件解析

```bash
# 1. 提交任务
curl -X POST "https://mineru.net/api/v4/extract/task" \
  -H "Authorization: Bearer $MINERU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://arxiv.org/pdf/2410.17247",
    "enable_formula": true,
    "enable_table": true,
    "layout_model": "doclayout_yolo",
    "language": "en"
  }'

# 返回: {"task_id": "xxx", "status": "pending"}

# 2. 轮询结果
curl "https://mineru.net/api/v4/extract/task/{task_id}" \
  -H "Authorization: Bearer $MINERU_TOKEN"

# 返回: {"status": "done", "result": {...}}
```

### 批量解析

```bash
# 1. 获取上传 URL
curl -X POST "https://mineru.net/api/v4/file-urls/batch" \
  -H "Authorization: Bearer $MINERU_TOKEN" \
  -d '{"file_names": ["paper1.pdf", "paper2.pdf"]}'

# 2. 上传文件到返回的 presigned URLs

# 3. 批量提交任务
curl -X POST "https://mineru.net/api/v4/extract/task/batch" \
  -H "Authorization: Bearer $MINERU_TOKEN" \
  -d '{"files": [{"url": "...", "name": "paper1.pdf"}, ...]}'
```

---

## ⚙️ 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `url` | string | 文件 URL (支持 http/https) |
| `enable_formula` | bool | 启用公式识别 (默认 true) |
| `enable_table` | bool | 启用表格识别 (默认 true) |
| `layout_model` | string | `doclayout_yolo` (快) / `layoutlmv3` (准) |
| `language` | string | `en` / `ch` / `auto` |
| `model_version` | string | `pipeline` / `vlm` / `MinerU-HTML` |

### 模型版本对比

| 版本 | 速度 | 准确度 | 适用场景 |
|------|------|--------|----------|
| `pipeline` | ⚡ 快 | 高 | 常规文档 |
| `vlm` | 🐢 慢 | 最高 | 复杂版面 |
| `MinerU-HTML` | ⚡ 快 | 高 | 网页样式输出 |

---

## 📂 输出结构

解析完成后下载的 ZIP 包含：

```
output/
├── full.md           # 完整 Markdown
├── content_list.json # 结构化内容
├── images/           # 提取的图片
└── layout.json       # 版面分析结果
```

---

## 🔧 OpenClaw 集成工作流

### 论文解析流程

```bash
# 1. 创建论文目录
mkdir -p "./paper-reading/[CVPR 2025] NewPaper"
cd "./paper-reading/[CVPR 2025] NewPaper"

# 2. 提交解析任务
TASK_ID=$(curl -s -X POST "https://mineru.net/api/v4/extract/task" \
  -H "Authorization: Bearer $MINERU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://arxiv.org/pdf/XXXX.XXXXX"}' | jq -r '.task_id')

# 3. 等待完成 & 下载
# (轮询 status 直到 done，然后下载 result.zip)

# 4. 解压
unzip result.zip -d .
```

### 环境变量

在 `~/.bashrc` 或 OpenClaw config 中设置：

```bash
export MINERU_TOKEN="your_api_key_here"
```

---

## ⚠️ 限制

| 限制 | 数值 |
|------|------|
| 单文件大小 | 200 MB |
| 单文件页数 | 600 页 |
| 并发任务数 | 根据套餐 |

---

## 💡 使用技巧

1. **arXiv 论文直接用 URL**
   ```
   https://arxiv.org/pdf/2410.17247
   ```

2. **中文论文用 `language: ch`**

3. **复杂表格用 `vlm` 模型**

4. **批量处理省 quota**
   - 一次提交多个文件，比单个提交更高效

---

## 📚 相关资源

- [Paper Banana Skill](https://clawhub.com/skills/paper-banana) - 论文配图生成

---

*论文解析不再手动复制粘贴！📖*
