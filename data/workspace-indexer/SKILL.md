---
name: Workspace Indexer
description: 自动维护 workspace 目录索引。
---

# Workspace Indexer

自动维护 workspace 目录索引。

## 触发条件
- 用户说"更新 workspace 索引"
- 定期维护（建议在 HEARTBEAT.md 中配置每天检查一次）

## 工作流程

### 1. 搜索记忆
首先使用 `memory_search` 搜索每个目录的相关记忆，了解目录用途和历史。

### 2. 扫描目录
使用 `exec` 工具扫描 workspace 目录结构。

### 3. 智能递归
- **容器目录**（projects/、research/、skills/）：进入查看子目录
- **项目根目录**（包含 .git、package.json、README 等标志文件）：停止递归，直接索引
- **普通目录**：直接索引

### 4. 收集信息
对每个目录：
- 读取 README 或注释（如果有）
- 检查是否有运行中的服务或容器
- 不要深入分析项目内部文件

### 5. 生成索引
写入 `WORKSPACE_INDEX.md`，格式参考以下示例：

---

- `skills/my-custom-skill/`
- 自定义技能，用于处理特定任务。包含 SKILL.md 和相关脚本。相关记忆：2026-01-15.md，搜索关键词：custom skill

---

- `projects/web-app/`
- Web 应用项目，使用 Node.js + React 构建。当前运行中，端口 3000。相关记忆：2026-02-01.md，搜索关键词：web app project

---

- `research/experiment-a/`
- 实验性项目，用于测试新技术方案。包含 Docker 容器，容器 ID abc123，端口 8080。相关记忆：2026-02-10.md，搜索关键词：experiment a

---

- `old-project/`
- 旧项目目录，已不再使用。包含 .git 仓库（50MB），总大小 200MB。状态：待清理

---

- `memory/`
- 每日记忆目录，按日期存储原始对话日志（YYYY-MM-DD.md 格式）。MEMORY.md 是从这些日志中提炼的长期记忆

---

- `tmp/`
- 临时文件目录，存放测试脚本和临时数据

---

## 注意事项
- 只索引目录级别，不深入项目内部
- 描述要详细但精炼，包含：用途、运行状态、相关记忆文件、搜索关键词
- 标记废弃或待清理的项目

## 定期维护
建议在 `HEARTBEAT.md` 添加每天检查任务：
```
## Workspace 索引维护
每天检查 workspace 目录变化，如有新增或变更则更新索引
```
