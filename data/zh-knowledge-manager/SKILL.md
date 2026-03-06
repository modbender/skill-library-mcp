---
name: zh-knowledge-manager
description: 中文 AI 增强知识管理。PREFIX 确定性分类 + hash/语义去重 + jieba 自动标签 + LLM 对话知识提取。
version: 1.0.0
author: jgpy
tags:
  - knowledge-management
  - chinese
  - productivity
  - memory
metadata:
  openclaw:
    requires:
      bins:
        - node
      env:
        - SILICONFLOW_API_KEY
---

# 中文知识管理（zh-knowledge-manager）

将 agent 的日志自动沉淀为结构化知识库。核心流程由确定性脚本驱动（PREFIX 分类 + hash 去重），可选启用 AI 增强（语义去重 + 自动标签 + 对话知识提取）。

## 触发条件

当以下情况出现时使用本 skill：
- 用户说"同步日志"、"整理知识"、"知识库"、"km sync"
- 用户要求从对话中提取知识
- 用户问知识库的状态或统计
- Heartbeat 定时触发（每日一次 sync）

## 日志格式

写入 `memory/YYYY-MM-DD.md` 时必须使用以下格式：

```
### [PREFIX:Name] Title
正文内容（结论、教训、要点，不超过 3 行）
#tag1 #tag2
```

PREFIX 规范：
- `PROJECT` — 项目进展
- `ISSUE` — 问题/故障
- `INFRA` — 基础设施变更
- `CONFIG` — 配置调整
- `RESEARCH` — 调研/选型
- `KB` — 知识沉淀（老板口述的业务规则等）
- `BOSS` — 老板指令/业务判断（仅 extract 产出使用）

## 命令

### 基础命令（离线可用）

```bash
# 同步最近 N 天日志到知识库
node {baseDir}/km.js sync --days 7

# 预览不写入
node {baseDir}/km.js sync --days 7 --dry-run

# 知识库统计 + 更新索引
node {baseDir}/km.js stats

# 清理失效的去重引用
node {baseDir}/km.js cleanup

# 初始化配置和 kb/ 目录
node {baseDir}/km.js init
```

### AI 增强命令（需要 API Key）

```bash
# 语义去重同步（bge-m3 embedding）
node {baseDir}/km.js sync --days 7 --semantic

# 自动标签补充（jieba 中文分词）
node {baseDir}/km.js sync --days 7 --auto-tag

# 全部 AI 增强
node {baseDir}/km.js sync --days 7 --semantic --auto-tag

# 从对话 dump 提取知识（LLM）
node {baseDir}/km.js extract backups/session-dump.md

# 批量提取最近 3 天的 dump
node {baseDir}/km.js extract backups/ --days 3

# 导入审核后的草稿
node {baseDir}/km.js import output/kb-draft-0227.md

# 知识库摘要（含空白检测）
node {baseDir}/km.js digest

# 推荐标签
node {baseDir}/km.js suggest-tags "pandas 读取大表时需要 chunksize"
```

## 注意事项

- `extract` 的产出放在 `output/kb-draft-*.md`，**必须人工审阅后才能 import**
- `--semantic` 需要配置 `SILICONFLOW_API_KEY` 环境变量
- `--auto-tag` 需要安装 `@node-rs/jieba`（`npm install` 自动安装）
- 核心 `sync` 无需任何 API，完全离线可用
- 每日 Heartbeat 应运行 `node {baseDir}/km.js sync --days 1`
