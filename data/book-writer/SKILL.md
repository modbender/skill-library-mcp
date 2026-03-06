---
name: book-writer
description: 使用AI辅助写作的OpenClaw技能，可以根据提示词生成书籍大纲并逐级扩写内容，支持添加公式、图表、代码等元素。适用于学术著作、技术书籍、小说等多种类型的创作。
---

# OpenClaw 智能写书技能

这是一个功能完整的AI辅助写作技能，能够根据用户提供的提示词生成书籍大纲，并逐级扩写各章节内容，支持在内容中插入公式、图表、表格和代码等元素。

## 功能特性

### 📚 大纲生成能力
- **智能大纲生成**: 根据提示词自动生成结构化书籍大纲
- **多层级结构**: 支持章节、小节、子小节等多级结构
- **内容规划**: 为每个章节提供内容概要和要点
- **风格适配**: 根据书籍类型调整大纲结构

### ✍️ 内容扩写能力
- **逐级扩写**: 从章节标题逐步扩展到具体内容
- **内容丰富**: 自动添加公式、图表、表格、代码等元素
- **引用管理**: 自动生成并管理文献引用
- **格式规范**: 遵循学术或出版格式规范

### 🧩 多媒体支持
- **数学公式**: LaTeX格式的数学公式插入
- **图表生成**: 根据内容需求生成图表描述
- **代码片段**: 支持多种编程语言的代码插入
- **表格设计**: 结构化表格的创建和填充

### 📖 类型适配
- **学术著作**: 符合学术写作规范
- **技术书籍**: 包含代码示例和技术图表
- **小说创作**: 支持情节发展和人物描写
- **教科书**: 包含练习题和知识点总结

## 快速开始

### 1. 安装技能
```bash
# 进入技能目录
cd book-writer

# 安装依赖
python scripts/install_dependencies.py
```

### 2. 设置API密钥
```bash
# 设置环境变量
export OPENAI_API_KEY="your_openai_api_key"
export GOOGLE_CSE_ID="your_google_cse_id"  # 用于搜索素材
export GOOGLE_API_KEY="your_google_api_key"  # 用于搜索素材
```

### 3. 生成第一本书
```bash
# 生成大纲
python scripts/book_writer.py --action outline --prompt "机器学习入门教程"

# 扩写前三章
python scripts/book_writer.py --action expand --book-path "ml_intro_tutorial" --chapters 1,2,3
```

## 核心组件

### 书籍生成器 (`scripts/book_writer.py`)
主生成模块，负责协调整个书籍生成流程。

**主要功能:**
- 解析用户提示词
- 生成书籍大纲
- 逐级扩写内容
- 管理多媒体元素

**使用方法:**
```python
from scripts.book_writer import BookWriter

writer = BookWriter()

# 生成大纲
outline = writer.generate_outline("深度学习理论与实践")

# 扩写内容
book = writer.expand_book(outline, max_chapters=3)

# 保存书籍
writer.save_book(book, "deep_learning_book")
```

### 内容优化器 (`scripts/content_optimizer.py`)
优化生成的内容质量。

**主要功能:**
- 语法和风格优化
- 引用和参考文献管理
- 公式和代码验证
- 图表描述生成

### 素材搜索器 (`scripts/material_searcher.py`)
从网络搜索相关素材。

**主要功能:**
- 根据内容需求搜索图片
- 查找相关数据和统计信息
- 搜索代码示例
- 获取引用文献

## 配置说明

### 配置文件 (`config.yaml`)
```yaml
# API配置
openai:
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o
  max_tokens: 4000
  temperature: 0.7

# 搜索API配置
google:
  cse_id: ${GOOGLE_CSE_ID}
  api_key: ${GOOGLE_API_KEY}

# 书籍生成默认参数
defaults:
  max_chapters: 10
  max_sections_per_chapter: 5
  content_length: "medium"  # short, medium, long
  include_formulas: true
  include_code: true
  include_figures: true
  include_tables: true

# 存储设置
storage:
  output_dir: "generated_books"
  temp_dir: "temp_files"
  max_storage_gb: 10
```

## 使用示例

### 示例1：生成技术书籍大纲
```bash
python scripts/book_writer.py --action outline --prompt "Python Web开发实战指南" --output my_web_dev_book
```

### 示例2：扩写指定章节
```bash
python scripts/book_writer.py --action expand --book-path my_web_dev_book --chapters 1,2,3 --include-code true
```

### 示例3：生成学术著作
```bash
python scripts/book_writer.py --action full --prompt "量子计算基础理论" --chapters 3 --include-formulas true --citation-style "apa"
```

## 部署到OpenClaw

将整个 `book-writer` 目录复制到 OpenClaw 的技能目录中即可使用。

## 许可证

本技能使用MIT许可证。详见项目根目录的LICENSE文件。