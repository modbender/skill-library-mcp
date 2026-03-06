---
name: file-manager
description: OpenClaw自动化文件管理助手，用于批量文件操作、智能分类、重复文件清理、文件重命名、目录同步等任务。当用户需要整理文件、批量重命名、清理重复文件、同步目录或自动化文件工作流时使用此技能。
---

# File Manager - OpenClaw 自动化文件管理

## 核心功能

### 1. 智能文件分类 (`organize`)
按文件类型、日期、大小或自定义规则自动分类文件。

```bash
# 按文件类型分类
python scripts/organize.py <source_dir> --by-type

# 按日期分类 (年/月/日)
python scripts/organize.py <source_dir> --by-date --date-format year/month

# 按文件大小分类
python scripts/organize.py <source_dir> --by-size --size-ranges "10MB,100MB,1GB"
```

### 2. 批量重命名 (`batch_rename`)
支持正则表达式、序列号、日期等模式的重命名。

```bash
# 添加前缀/后缀
python scripts/batch_rename.py <pattern> --prefix "IMG_" --suffix "_2024"

# 使用正则替换
python scripts/batch_rename.py "IMG_(\d+)" --replace "Photo_\1"

# 序列号重命名
python scripts/batch_rename.py "*.jpg" --sequence --start 1 --pad 4
```

### 3. 重复文件清理 (`deduplicate`)
基于内容哈希检测并处理重复文件。

```bash
# 扫描并列出重复文件
python scripts/deduplicate.py <directory> --scan-only

# 删除重复文件（保留最旧/最新）
python scripts/deduplicate.py <directory> --keep oldest --action delete

# 移动重复文件到隔离目录
python scripts/deduplicate.py <directory> --action move --to <quarantine_dir>
```

### 4. 目录同步 (`sync`)
双向或单向目录同步，支持排除模式和增量同步。

```bash
# 单向同步 (源 → 目标)
python scripts/sync.py <source> <target> --mirror

# 双向同步
python scripts/sync.py <dir1> <dir2> --bidirectional

# 排除特定文件
python scripts/sync.py <source> <target> --exclude "*.tmp,*.log,.git"
```

### 5. 文件监控 (`watch`)
监控目录变化并触发动作。

```bash
# 监控并记录变化
python scripts/watch.py <directory> --log changes.log

# 监控并自动执行命令
python scripts/watch.py <directory> --on-change "python scripts/organize.py {path}"
```

## 使用模式

### 常见场景

**场景1: 整理下载文件夹**
```python
# 自动分类下载的文件
python scripts/organize.py ~/Downloads --by-type --move
```

**场景2: 清理重复照片**
```python
# 找出并删除重复照片，保留高质量版本
python scripts/deduplicate.py ~/Pictures --compare-resolution --keep best
```

**场景3: 批量整理项目文件**
```python
# 按日期整理并按类型分类
python scripts/organize.py ./projects --by-date --by-type --date-format year/month
```

**场景4: 自动备份工作目录**
```python
# 同步到备份目录，排除临时文件
python scripts/sync.py ~/Work ~/Backups/Work --exclude "node_modules,.git,*.tmp"
```

## 工作流

### 文件整理工作流
1. 分析目录结构和文件分布
2. 选择分类策略 (类型/日期/大小/自定义)
3. 执行整理 (dry-run 预览 → 确认 → 执行)
4. 验证结果

### 清理工作流
1. 扫描重复/过期/大文件
2. 生成报告并预览
3. 用户确认或自动处理
4. 移动到回收站/隔离区/直接删除

### 同步工作流
1. 分析源和目标差异
2. 处理冲突 (保留新/保留旧/保留两者)
3. 执行同步
4. 生成同步报告

## 安全原则

- **预览优先**: 所有修改操作默认执行 dry-run，确认后再执行
- **备份保护**: 删除操作优先移动到隔离区而非永久删除
- **递归警告**: 递归操作需要显式确认
- **日志记录**: 所有操作记录到日志文件便于审计

## ⚙️ 依赖安装与环境初始化

### 依赖安装

本 skill 依赖以下 Python 包：

```bash
pip install tqdm colorama
```

或使用 requirements.txt（如果存在）：
```bash
pip install -r requirements.txt
```

### 环境要求

- Python 3.8+
- tqdm >= 4.60.0 (进度条)
- colorama >= 0.4.4 (Windows 彩色输出)

---

## 脚本参数说明

直接查看脚本帮助获取详细参数:
```bash
python scripts/<script>.py --help
```
