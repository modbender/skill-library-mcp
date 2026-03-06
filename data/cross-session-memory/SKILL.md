---
name: cross-session-memory
description: |
  Cross-session memory continuity system. Automatically loads 24h rolling memory and daily memory files for context awareness.
---

# 跨会话记忆连续性

## 功能

- **24 小时滚动记忆**：自动加载最近 24 小时的记忆文件
- **每日记忆加载**：自动读取昨天和今天的 memory 文件
- **上下文恢复**：会话开始时自动恢复之前的对话上下文
- **长期记忆整合**：可选加载 MEMORY.md 长期记忆

## 使用场景

- 跨天对话连续性
- 多会话协作
- 长期项目跟踪
- 上下文不丢失

## 实现逻辑

```powershell
# 伪代码
function Load-CrossSessionMemory {
    param(
        [int]$RollingHours = 24,
        [bool]$LoadLongTerm = $true
    )
    
    $now = Get-Date
    $memoryDir = "$workspace\memory"
    $context = @()
    
    # 1. 加载长期记忆（仅主会话）
    if ($LoadLongTerm -and $IsMainSession) {
        $longTerm = Get-Content "$workspace\MEMORY.md" -Raw
        $context += "## 长期记忆`n$longTerm"
    }
    
    # 2. 计算时间范围
    $startTime = $now.AddHours(-$RollingHours)
    
    # 3. 加载范围内的每日记忆文件
    $date = $startTime.Date
    while ($date -le $now.Date) {
        $file = "$memoryDir\$($date.ToString('yyyy-MM-dd')).md"
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            $context += "## 记忆：$($date.ToString('yyyy-MM-dd'))`n$content"
        }
        $date = $date.AddDays(1)
    }
    
    # 4. 返回整合的上下文
    return $context -join "`n`n"
}
```

## 文件结构

```
workspace/
├── MEMORY.md              # 长期记忆（ curated ）
└── memory/
    ├── 2026-03-02.md      # 每日记忆（raw logs）
    ├── 2026-03-03.md
    └── ...
```

## 使用示例

### 会话开始时自动加载

在 AGENTS.md 中已经定义：

```markdown
## Every Session

Before doing anything else:

1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **If in MAIN SESSION**: Also read `MEMORY.md`
```

### 手动加载

```powershell
# 加载最近 24 小时记忆
$context = Load-CrossSessionMemory -RollingHours 24

# 加载最近 7 天记忆（长期项目）
$context = Load-CrossSessionMemory -RollingHours 168 -LoadLongTerm $false
```

## 记忆文件内容

### 每日记忆文件 (memory/YYYY-MM-DD.md)

```markdown
# 2026-03-03

## 对话摘要
- 11:08 用户询问定时任务状态
- 11:22 确认修复飞书投送配置
- 14:10 要求安装 5 个推荐技能

## 任务状态
- ✅ 定时任务配置修复完成
- ❌ 技能安装失败（无可用 package）
- 🔄 自行实现技能中

## 配置变更
- 修改 jobs.json 添加 delivery.to 字段
- 创建 feishu-message-fallback 技能
```

### 长期记忆 (MEMORY.md)

```markdown
# 长期记忆

## 用户信息
- 姓名：白凤
- 邮箱：2426758093@qq.com
- 位置：北京

## 重要项目
- 新闻自动化系统 ✅
- 数字员工系统 ✅
- 定时任务系统 ✅

## 偏好
- 不喜欢频繁确认
- 喜欢直接简洁的回复
```

## 集成到 OpenClaw

### 方法 1：修改 AGENTS.md（已实现）

在 `Every Session` 部分添加记忆加载步骤。

### 方法 2：Cron 定时加载

```json
{
  "name": "memory-context-loader",
  "schedule": "0 * * * *",
  "payload": {
    "kind": "systemEvent",
    "text": "Load recent memory files and update session context"
  }
}
```

### 方法 3：会话启动 Hook

在 OpenClaw 配置中添加：

```json
{
  "hooks": {
    "sessionStart": {
      "enabled": true,
      "script": "skills/cross-session-memory/load-memory.ps1"
    }
  }
}
```

## 性能优化

### 1. 限制加载文件数量

```powershell
# 只加载最近 N 天的记忆
$maxDays = 7
$files = Get-ChildItem $memoryDir -Filter "*.md" | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First $maxDays
```

### 2. 增量加载

```powershell
# 只加载上次会话后新增的内容
$lastSessionTime = Get-Content "$workspace\.last-session-time"
$files = Get-ChildItem $memoryDir -Filter "*.md" | 
    Where-Object { $_.LastWriteTime -gt $lastSessionTime }
```

### 3. 缓存机制

```powershell
# 缓存加载的记忆内容
$cacheFile = "$workspace\.memory-cache.json"
if (Test-Path $cacheFile) {
    $cache = Get-Content $cacheFile | ConvertFrom-Json
    if ((Get-Date) -lt $cache.expiresAt) {
        return $cache.content
    }
}
```

## 最佳实践

1. **每日记忆**：记录 raw logs，详细但简洁
2. **长期记忆**：只记录重要决策、用户偏好、项目状态
3. **定期整理**：每周回顾，将重要内容从每日记忆迁移到长期记忆
4. **控制大小**：长期记忆不超过 50KB，避免 token 浪费

## 与现有系统集成

当前工作空间已实现：

- ✅ `MEMORY.md` - 长期记忆
- ✅ `memory/YYYY-MM-DD.md` - 每日记忆
- ✅ `AGENTS.md` - 会话启动时加载
- ✅ `auto-logger` 技能 - 自动记录

需要增强：

- 🔄 24 小时滚动窗口自动计算
- 🔄 会话间状态持久化
- 🔄 记忆搜索和检索优化
