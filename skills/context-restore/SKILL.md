---
name: context-restore
description: |
  Skill that restores conversation context when users want to "continue where we left off".
  Reads compressed context files, extracts key information (recent operations, projects, tasks),
  and provides structured output to help users quickly resume their work.
---

# Context Restore Skill

## 快速开始

```bash
# 基础使用 - 恢复上下文
/context-restore

# 指定恢复级别
/context-restore --level detailed
/context-restore -l minimal

# 命令行工具
python scripts/restore_context.py --level normal

# 获取结构化摘要（供其他技能使用）
python scripts/restore_context.py --summary

# 用户确认流程
python scripts/restore_context.py --confirm

# Telegram 消息分块发送
python scripts/restore_context.py --telegram

# ========== Phase 3: 自动触发集成 ==========

# 自动检测并恢复上下文（检测到变化时自动恢复）
python scripts/restore_context.py --auto

# 自动模式，静默输出（适合 cron）
python scripts/restore_context.py --auto --quiet

# 仅检查变化（返回退出码 0/1）
python scripts/restore_context.py --check-only

# 安装 cron 自动监控任务
python scripts/restore_context.py --install-cron
```

---

## 功能说明

### 核心价值

让用户在 `/new`（开启新会话）后快速恢复工作状态：
- 无需重复解释背景
- 秒级恢复到之前的工作状态
- 自然语言触发，无感恢复
- 支持用户确认流程
- Telegram 消息自动分块

### 目标用户场景

| 场景 | 用户需求 | 恢复内容 |
|------|---------|---------|
| 跨天继续工作 | 昨天做到哪了？ | 项目进度、待办任务 |
| 任务切换后回来 | 之前在做什么？ | 当前任务状态、关键文件 |
| 中断后继续 | 接着刚才的聊 | 对话历史节点 |
| 周期性回顾 | 这周做了哪些事？ | 时间线摘要、成果列表 |

---

## 触发条件

### 中文关键词

```
核心词: 恢复上下文、继续之前的工作
扩展词: 恢复、接着、继续、之前聊到哪了、继续之前的工作、
        继续之前的任务、接着做、回到之前的工作、恢复工作状态
```

### 英文关键词

```
核心词: restore context、continue previous work
扩展词: continue、resume、what was I doing、where did we leave off、
        get back to work、resume session
```

### 命令格式

```
/context-restore [选项]
/restore [选项]
恢复上下文 [级别]
restore context [level]
```

### 级别参数

| 参数 | 效果 |
|------|------|
| `minimal` / `min` / `简短` | 极简模式（核心状态一句话） |
| `normal` / `default` / `正常` | 标准模式（默认，项目+任务） |
| `detailed` / `full` / `详细` | 完整模式（完整上下文+时间线） |

---

## 执行流程

```
1. 检测意图 → 关键词/命令识别
2. 加载上下文 → 读取 compressed_context/latest_compressed.json
3. 解析内容 → JSON 或纯文本格式
4. 提取信息 → 项目、任务、操作、时间线
5. 格式化输出 → 根据级别生成报告
6. 发送确认 → 用户确认后继续工作
```

---

## 恢复级别

### Minimal（极简）

**输出内容**：
- 核心状态一句话
- 1个活跃任务

**示例输出**：
```
✅ 上下文已恢复

状态：Hermes Plan 进行中（数据管道完成，待测试）
```

### Normal（标准，默认）

**输出内容**：
- 项目状态列表
- 待办任务列表
- 最近操作记录
- MEMORY.md 高亮

**示例输出**：
```
✅ 上下文已恢复

当前活跃项目：
1. 🏛️ Hermes Plan - 数据分析助手（进度：80%）
2. 🌐 Akasha Plan - 自主新闻系统（进度：45%）

待办任务：
- [高] 编写数据管道测试用例
- [中] 设计 Akasha UI 组件
- [低] 更新 README 文档

最近操作（今天）：
- 完成数据清洗模块
- 添加 3 个新 cron 任务
- 修改配置文件
```

### Detailed（完整）

**输出内容**：
- 完整会话概览
- 所有项目详情
- 完整任务队列（按优先级分类）
- 7天时间线
- 原始内容预览

**示例输出**：
```
✅ 上下文已恢复（完整模式）

═══════════════════════════════════════
📊 会话概览
═══════════════════════════════════════
当前会话：#2026-02-06-main
活跃 Isolated Sessions：3个
最后活动：2小时前

═══════════════════════════════════════
🎯 核心项目状态
═══════════════════════════════════════
1. Hermes Plan（进行中）- 进度：80%
2. Akasha Plan（待恢复）- 进度：45%

[...完整时间线和历史记录]
```

---

## API / 命令行参数

### Python API

```python
from restore_context import (
    restore_context,
    get_context_summary,
    extract_timeline,
    compare_contexts,
    filter_context
)

# 基础恢复
report = restore_context(filepath, level="normal")

# 获取结构化摘要（供其他技能使用）
summary = get_context_summary(filepath)
# 返回格式：
# {
#   "success": True,
#   "metadata": {...},
#   "operations": [...],
#   "projects": [...],
#   "tasks": [...],
#   "timeline": {...},
#   "memory_highlights": [...]
# }

# 提取时间线
timeline = extract_timeline(content, period="weekly", days=30)
# 返回格式：
# {
#   "period": "weekly",
#   "total_days": 30,
#   "total_operations": 15,
#   "timeline": [
#     {
#       "period_label": "Week 6 (Feb 2-8)",
#       "date_range": "2026-02-02 to 2026-02-08",
#       "operations": [...],
#       "projects": [...],
#       "highlights": [...]
#     }
#   ]
# }

# 对比两个版本
diff = compare_contexts(old_file, new_file)
# 返回格式：
# {
#   "success": True,
#   "added_projects": [...],
#   "removed_projects": [...],
#   "modified_projects": [...],
#   "operations_added": [...],
#   "operations_removed": [...],
#   "time_diff_hours": 24.0,
#   ...
# }

# 过滤内容
filtered = filter_context(content, "Hermes Plan")
```

### 命令行参数

```bash
python restore_context.py [选项]

基础选项：
  --file, -f           上下文文件路径（默认：绝对路径 compressed_context/latest_compressed.json）
  --level, -l          恢复级别（minimal/normal/detailed，默认：normal）
  --output, -o         输出文件路径
  --summary, -s        输出结构化摘要（JSON 格式）
  --confirm            添加用户确认流程（询问用户是否继续）
  --telegram           Telegram 消息分块发送（自动分割长消息）
  --since              仅包含指定日期后的操作（YYYY-MM-DD 格式）
  --help, -h           显示帮助信息

Phase 2 - 时间线与过滤选项：
  --timeline           启用时间线视图
  --period             时间线聚合周期（daily/weekly/monthly，默认：daily）
  --filter             过滤关键词，只显示匹配内容
  --diff               对比两个版本（需要两个文件路径）

Phase 3 - 自动触发选项：
  --auto               自动模式：检测到变化时自动恢复，无需用户确认
  --quiet              静默模式：仅显示必要消息（与 --auto 配合使用）
  --check-only         仅检查变化，不恢复（返回退出码 0/1）
  --install-cron       生成并安装 cron 自动监控任务
  --cron-interval      Cron 间隔分钟数（默认：5，与 --install-cron 配合）
```

### 完整命令行示例

```bash
# 使用默认配置
python restore_context.py

# 详细模式输出到文件
python restore_context.py --level detailed --output report.txt

# 最小模式
python restore_context.py -l minimal

# 自定义文件路径
python restore_context.py -f /path/to/context.json

# 结构化 JSON 输出
python restore_context.py --summary

# 用户确认流程
python restore_context.py --confirm

# Telegram 消息分块发送
python restore_context.py --telegram

# ========== Phase 2: 时间线与过滤 ==========

# 按天显示时间线（默认）
python restore_context.py --timeline --period daily

# 按周显示时间线
python restore_context.py --timeline --period weekly

# 按月显示时间线
python restore_context.py --timeline --period monthly

# 过滤特定内容
python restore_context.py --filter "Hermes"

# 只显示项目相关信息
python restore_context.py --filter "project"

# ========== Phase 2: 上下文对比 ==========

# 对比两个版本
python restore_context.py --diff old.json new.json

# 对比并输出详细报告
python restore_context.py --diff old.json new.json --level detailed

# ========== Phase 3: 自动触发示例 ==========

# 自动检测并恢复（检测到变化时自动恢复）
python restore_context.py --auto

# 自动模式，静默输出（适合 cron）
python restore_context.py --auto --quiet

# 检查变化（外部监控使用）
python restore_context.py --check-only
echo $?  # 0=无变化, 1=有变化

# 安装 cron 任务
python restore_context.py --install-cron

# 安装 cron 任务（每10分钟）
python restore_context.py --install-cron --cron-interval 10

# 完整自动恢复（详细级别）
python restore_context.py --auto --level detailed
```

---

## 输出格式

### 标准消息格式

```markdown
✅ **上下文已恢复** [级别标识]

[主要内容块]

---
💡 **操作建议**
• 建议操作 1
• 建议操作 2
```

### Normal 级别统一输出格式

```
✅ **上下文已恢复**

📊 **压缩信息:**
- 原始消息: {original_count}
- 压缩后: {compressed_count}
- 压缩率: {compression_ratio}%

🔄 **最近操作:**
- 操作1
- 操作2

🚀 **项目:**
- **项目名称** - 描述
```

### Telegram 消息分块

当消息超过 4000 字符时，自动分块发送：

```bash
# Telegram 模式下，输出会自动分割
python restore_context.py --telegram
# [1/3]
# 第一块内容...
# [2/3]
# 第二块内容...
# [3/3]
# 第三块内容...
```

### 平台适配

| 平台 | 格式调整 |
|------|---------|
| Telegram | 使用 emoji 前缀，自动分块发送（--telegram） |
| Discord | 使用 embed 格式 |
| WhatsApp | 无 markdown，简化格式 |
| CLI | 纯文本，树形结构 |

---

## 错误处理

| 场景 | 处理方式 | 用户消息 |
|------|---------|---------|
| 文件不存在 | 创建空上下文，记录警告 | "未找到历史上下文，将从新会话开始" |
| 文件损坏 | 尝试降级读取 | "上下文文件异常，已重置为初始状态" |
| 解析失败 | 返回 minimal 版本 | "部分上下文无法恢复，已获取核心信息" |
| 权限错误 | 记录日志，静默失败 | "无法访问上下文文件，请检查权限" |

---

## 与其他技能的集成

### 集成关系

```
Context-Restore 依赖:
├── context-save (保存上下文)
├── memory_get (读取 MEMORY.md)
└── memory_search (搜索历史)

Context-Restore 提供给:
├── summarize (项目摘要)
├── task-manager (待办列表)
└── weekly-review (时间线回顾)
```

### 配合 context-save 使用

```markdown
**context-save**：会话结束时自动保存上下文
**context-restore**：会话开始时恢复上下文

配合流程：
1. 用户结束会话 → context-save 自动保存
2. 用户 new session → context-restore 自动/手动触发
3. 用户确认 → 继续工作
```

### 供其他技能调用的结构化输出

```python
from restore_context import get_context_summary

def my_skill():
    summary = get_context_summary()
    
    if summary['success']:
        # 使用项目信息
        for project in summary['projects']:
            process_project(project)
        
        # 使用任务信息
        for task in summary['tasks']:
            schedule_task(task)
        
        # 使用最近操作
        for operation in summary['operations']:
            log_operation(operation)
```

---

## 最佳实践

### 1. 推荐使用流程

```markdown
1. 用户进入新会话
2. 说 "继续之前的工作"
3. 查看恢复报告
4. 选择继续的任务
5. 开始工作
```

### 2. 恢复级别选择

| 使用场景 | 推荐级别 |
|---------|---------|
| 快速确认当前状态 | Minimal |
| 日常继续工作 | Normal（默认） |
| 深度回顾/汇报 | Detailed |

### 3. 与其他技能配合

```markdown
# 恢复上下文 + 获取详细信息
/context-restore --level normal
-> 然后调用 memory_get 获取 MEMORY.md 详情

# 恢复上下文 + 搜索特定话题
/context-restore --level normal
-> 然后调用 memory_search "某个关键词"
```

---

## 配置文件

```yaml
# SKILL_CONFIG.md
context-restore:
  default_level: "normal"
  auto_trigger: true
  
  output:
    show_timeline: true
    max_projects: 5
    max_recent_actions: 10
    include_file_list: true
  
  limits:
    minimal_token: 50
    normal_token: 200
    detailed_token: 500
```

---

## 数据源

### 必需文件

```
./compressed_context/latest_compressed.json
```

### 可选文件

```
./memory/MEMORY.md          # 长期记忆
./memory/YYYY-MM-DD.md      # 每日记录
./projects/*/status.json    # 项目状态文件
```

### 上下文文件格式

```json
{
  "version": "1.0",
  "lastUpdated": "2026-02-06T23:42:00Z",
  "sessions": {
    "main": {"id": "main-2026-02-06", "active": true},
    "isolated": [...]
  },
  "projects": {...},
  "recentActions": [...],
  "timeline": [...]
}
```

---

## Phase 2: 时间线与对比功能 (Timeline & Comparison)

### 新增功能

#### 1. `--timeline` 时间线视图

按不同周期聚合历史操作，提供更清晰的进度回顾：

```bash
# 按天显示（默认）
python restore_context.py --timeline --period daily

# 按周显示
python restore_context.py --timeline --period weekly

# 按月显示
python restore_context.py --timeline --period monthly

# 限制时间范围（最近30天）
python restore_context.py --timeline --period weekly --days 30
```

**输出示例（weekly）：**
```
📅 Week 6 (Feb 2-8)
├── ✅ 完成数据管道测试
├── ✅ 部署新功能到生产环境
└── 🚀 项目: Hermes Plan, Akasha Plan

📅 Week 5 (Jan 26 - Feb 1)
├── ✅ 启动 Akasha UI 改进
└── 🚀 项目: Hermes Plan
```

#### 2. `--filter` 内容过滤

只显示匹配特定条件的内容：

```bash
# 只显示与 Hermes 相关的内容
python restore_context.py --filter "Hermes"

# 只显示项目相关信息
python restore_context.py --filter "project"

# 组合使用
python restore_context.py --filter "Hermes" --level detailed
```

**过滤逻辑：**
- 不区分大小写匹配
- 保留匹配行的上下文（前后2行）
- 如果没有匹配，返回提示信息

#### 3. `--diff` 上下文对比

比较两个版本的上下文差异：

```bash
# 基本对比
python restore_context.py --diff old.json new.json

# 详细对比
python restore_context.py --diff old.json new.json --level detailed

# 输出到文件
python restore_context.py --diff old.json new.json --output diff_report.txt
```

**对比报告包含：**
- 时间差
- 新增/移除/修改的项目
- 新增/移除的任务
- 新增/移除的操作
- 消息数量变化

### API 参考

```python
# 时间线提取
extract_timeline(content: str, period: str = "daily", days: int = 30) -> dict

# 内容过滤
filter_context(content: str, filter_pattern: str) -> str

# 上下文对比
compare_contexts(old: str, new: str) -> dict

# 格式化对比报告
format_diff_report(diff: dict, old_file: str, new_file: str) -> str
```

### 使用场景

#### 场景 1: 每日进度回顾

```bash
# 查看本周进度
python restore_context.py --timeline --period weekly
```

#### 场景 2: 项目变更追踪

```bash
# 只关注 Hermes 项目
python restore_context.py --filter "Hermes" --timeline --period weekly
```

#### 场景 3: 周期性对比报告

```bash
#!/bin/bash
# 生成每日对比报告
python restore_context.py --diff context_yesterday.json context_today.json \
    --output daily_diff_$(date +\%Y\%m\%d).txt
```

---

## Phase 3: 自动触发集成 (Auto Trigger)

### 新增功能

#### 1. 上下文变化检测 (Context Change Detection)

使用哈希算法检测上下文是否发生变化：

```python
from restore_context import hash_content, detect_context_changes, load_cached_hash, save_cached_hash

# 检测变化
current_hash = hash_content(current_content)
previous_hash = load_cached_hash()
if detect_context_changes(current_content, previous_content):
    print("Context changed!")

# 保存哈希缓存
save_cached_hash(current_hash, context_file)
```

#### 2. `--auto` 自动触发模式

自动检测上下文变化并在检测到变化时自动恢复：

```bash
# 自动检测并恢复
python restore_context.py --auto

# 自动但静默模式（适合 cron）
python restore_context.py --auto --quiet

# 指定恢复级别
python restore_context.py --auto --level detailed
```

#### 3. `--check-only` 检查模式

仅检查变化而不恢复，适合外部监控系统：

```bash
# 检查变化（返回退出码）
python restore_context.py --check-only
# 退出码 0: 无变化
# 退出码 1: 检测到变化
```

#### 4. `--install-cron` Cron 集成

安装自动上下文监控任务：

```bash
# 安装 cron 任务（默认每5分钟检查）
python restore_context.py --install-cron

# 自定义检查间隔
python restore_context.py --install-cron --cron-interval 10
```

输出示例：
```
✅ Cron script created: /home/athur/.openclaw/workspace/skills/context-restore/scripts/auto_context_monitor.sh
ℹ️  To install, run:
  echo "*/5 * * * * /home/athur/.openclaw/workspace/skills/context-restore/scripts/auto_context_monitor.sh >> /var/log/context_monitor.log 2>&1" >> ~/.crontab
  crontab ~/.crontab
```

### 使用场景

#### 场景 1: 定期自动恢复

```bash
# 设置 cron 任务，每5分钟自动检查并恢复
*/5 * * * * python3 /home/athur/.openclaw/workspace/skills/context-restore/scripts/restore_context.py --auto --quiet >> /var/log/context_restore.log 2>&1
```

#### 场景 2: 外部监控系统集成

```bash
#!/bin/bash
# 外部监控系统脚本
if python3 restore_context.py --check-only; then
    echo "No changes detected"
else
    echo "Context changed - triggering restore"
    python3 restore_context.py --auto
fi
```

#### 场景 3: 会话开始时自动恢复

在用户新会话开始时自动触发恢复：

```python
# 在会话初始化时调用
from restore_context import check_and_restore_context

result = check_and_restore_context(
    context_file='./compressed_context/latest_compressed.json',
    auto_mode=True,
    quiet=False,
    level='normal'
)

if result['changed'] and result['restored']:
    print(result['report'])
```

### API 参考

```python
# 变化检测函数
hash_content(content: str) -> str
detect_context_changes(current: str, previous: str) -> bool
load_cached_hash(cache_file: str) -> Optional[str]
save_cached_hash(content_hash: str, context_file: str, cache_file: str) -> bool

# 自动恢复函数
check_and_restore_context(
    context_file: str,
    auto_mode: bool = False,
    quiet: bool = False,
    level: str = 'normal'
) -> dict

# 通知函数
send_context_change_notification(context_file: str, auto_mode: bool) -> bool

# Cron 集成函数
generate_cron_script() -> str
install_cron_job(script_path: str = None, interval_minutes: int = 5) -> bool
```

### 通知集成

当检测到上下文变化时，可以触发外部通知：

```python
# 通知脚本示例 (notify_context_change.py)
import sys

if __name__ == '__main__':
    # 解析参数
    context_file = sys.argv[2]  # --file 参数
    auto_mode = '--auto' in sys.argv
    
    # 发送通知（可集成 Telegram、邮件等）
    send_telegram_message(f"Context changed: {context_file}")
    send_email_notification(f"Context changed on {auto_mode}")
```

---

## 文件结构

```
skills/context-restore/
├── SKILL.md                    # 技能定义（本文档）
├── README.md                   # 项目说明
├── references/
│   └── design.md              # 设计决策文档
├── scripts/
│   ├── __init__.py
│   ├── restore_context.py     # 核心实现（完整代码）
│   │   └── 函数：
│   │       ├── load_compressed_context()  # 加载上下文文件
│   │       ├── parse_metadata()           # 解析元数据
│   │       ├── extract_recent_operations() # 提取最近操作
│   │       ├── extract_key_projects()      # 提取项目信息
│   │       ├── extract_ongoing_tasks()      # 提取任务信息
│   │       ├── extract_memory_highlights() # 提取MEMORY引用
│   │       ├── extract_timeline()          # Phase 2: 提取时间线
│   │       ├── filter_context()            # Phase 2: 过滤内容
│   │       ├── get_context_summary()       # 获取结构化摘要
│   │       ├── compare_contexts()          # Phase 2: 对比上下文
│   │       ├── format_diff_report()        # Phase 2: 格式化对比报告
│   │       ├── restore_context()           # 主入口函数
│   │       ├── hash_content()              # Phase 3: 内容哈希
│   │       ├── detect_context_changes()    # Phase 3: 变化检测
│   │       ├── load_cached_hash()          # Phase 3: 加载缓存哈希
│   │       ├── save_cached_hash()          # Phase 3: 保存缓存哈希
│   │       ├── check_and_restore_context() # Phase 3: 自动恢复
│   │       ├── send_context_change_notification() # Phase 3: 通知
│   │       ├── generate_cron_script()      # Phase 3: 生成cron脚本
│   │       └── install_cron_job()          # Phase 3: 安装cron任务
│   └── robustness_improvements.py  # 健壮性改进模块
│
├── docs/
│   ├── USAGE.md               # 使用指南（完整示例）
│   ├── API.md                 # API 参考文档
│   └── auto_context_monitor.sh   # Phase 3: 自动监控脚本
└── tests/
    ├── __init__.py
    ├── test_restore_basic.py   # 基础功能测试
    ├── test_error_handling.py # 错误处理测试
    └── test_integration.py     # 集成测试
```
