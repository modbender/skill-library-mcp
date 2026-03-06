# 04 — 紧急故障处理

## 故障分级

| 级别 | 症状 | 处理 |
|------|------|------|
| 🟢 **小 Bug** | 单个功能异常，错误信息清晰 | 粘贴错误 → AI 修 |
| 🟡 **循环修复** | 修了 A 坏了 B，修了 B 坏了 C | 停止！回退 → 换策略 |
| 🔴 **架构崩塌** | 多处报错，AI 越修越乱 | 回退到最近稳定版本 |
| ⚫ **上下文崩溃** | AI 重复、遗忘、答非所问 | 关闭 session，全新开始 |

---

## 紧急处理 SOP

### 🟢 小 Bug
复制完整 stack trace + 上下文 → AI 修 → 验证

### 🟡 循环修复 — STOP, ROLLBACK, RETHINK
识别信号：来回改同一文件 3+ 次，修复越来越"随机"

1. 🛑 立即停止
2. ⏪ `git stash` 或 `git checkout .`
3. 🤔 换模型 / 换 session / 换角度 / 手动分析根因
4. 📝 LOG.md 记录失败方案

### 🔴 架构崩塌
```bash
git log --oneline -20
git reset --hard <stable-commit>
```
更新 DESIGN.md → 重新 Plan

### ⚫ 上下文崩溃
1. 当前状态写入 LOG.md
2. 关闭 session → 新 session
3. 读取 CLAUDE.md + DESIGN.md + LOG.md → 从断点继续

---

## OODA Loop 调试法

```
Observe（观察）→ 完整错误信息 + 复现步骤
Orient（定位）→ 错误在哪一层（前端/后端/DB/网络）
Decide（决定）→ AI 修 / 手动修 / 回退
Act（执行）→ 修复 → 验证 → 失败则回到 Observe
```

---

## Git 是你的安全网

```bash
# 黄金规则：每个功能完成 → 立即 commit
git checkout -b feature/xxx
# ... 实现 Step 1 ...
git add -A && git commit -m "feat: step 1"
# ... 出问题 ...
git reset --hard HEAD~1            # 只回退 Step 2
```

> **Note**: git 命令在 Bash 和 PowerShell 中语法基本一致（`git add -A; git commit ...`）。PowerShell 5.x 不支持 `&&`，用 `;` 代替即可。

---

## 多 Agent 并行灾难恢复

### 故障分级（多 Agent）

| 级别 | 症状 | 恢复时间 |
|------|------|---------|
| 🟡 单 Agent 挂掉 | 1 个 session 断开 | 5 分钟 |
| 🟠 Orchestrator 挂掉 | 全部 Agent 失去协调 | 15 分钟 |
| 🔴 系统宕机 | 所有 session 丢失 | 30 分钟 |
| ⚫ 数据损坏 | Git 状态不一致 | 1 小时 |

### 🟡 单 Agent 挂掉 — 热恢复
检查 worktree + LOG.md → 新 session 从断点继续 → 其他 Agent 无需暂停

### 🟠 Orchestrator 挂掉 — 暖恢复
收集所有 LOG.md → 新建 Lead session → 传入 PLAN.md + 进度汇总 → 重建协调

### 🔴 系统宕机 — 冷恢复
1. 检查 Git 状态（分支、worktree）
2. 逐个检查分支进度
3. 决策：有 commit → 从最后 commit 继续；未 commit → stash 评估
4. 重建 Agent 团队

### ⚫ 数据损坏 — 灾难恢复
```bash
git fsck              # 检查仓库完整性
git reflog            # 最后的安全网
# Worktree 损坏 → 强制删除 + 重建
# 核弹选项 → git clone from remote + cherry-pick
```

### 恢复决策树

```
系统恢复后
  ├─ git worktree list 正常？
  │   ├─ ✅ → 检查 git status → 读 LOG.md → 从断点继续
  │   └─ ❌ → git worktree repair → 失败则重建
  ├─ git fsck 正常？
  │   ├─ ✅ → 按上面恢复
  │   └─ ❌ → git clone from remote
  └─ remote 有推送？
      ├─ ✅ → 只丢最后一次 push 后的改动
      └─ ❌ → 从 reflog 恢复
```

### 预防措施

**Bash 版：**
```bash
# 强制频繁 commit（写入 Agent 规则）
"每完成一个逻辑步骤立即 git commit。不要积累超过 30 分钟的未提交改动。"

# post-commit hook 自动推送
echo '#!/bin/bash
git push origin HEAD 2>/dev/null || true' > .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

**PowerShell 版（Win11 适配）：**
```powershell
# post-commit hook（Windows 下 .git/hooks/post-commit 仍用 bash 语法，Git for Windows 自带 bash）
# 如果需要纯 PowerShell 定时快照：
$timer = New-Object System.Timers.Timer(600000)  # 10 分钟
Register-ObjectEvent $timer Elapsed -Action {
    Get-ChildItem worktree\feature-* -Directory | ForEach-Object {
        Push-Location $_.FullName
        git add -A
        $diff = git diff --cached --quiet 2>&1
        if ($LASTEXITCODE -ne 0) {
            git commit -m "auto-snapshot $(Get-Date -Format 'HH:mm')"
        }
        Pop-Location
    }
}
$timer.Start()
```

**恢复检查脚本 — PowerShell 版：**
```powershell
# scripts/check-agents.ps1
Write-Host "=== Agent Health Check ===" -ForegroundColor Cyan
Get-ChildItem worktree\feature-* -Directory | ForEach-Object {
    $branch = $_.Name
    Push-Location $_.FullName
    $status = (git status --porcelain | Measure-Object).Count
    $lastCommit = git log -1 --format="%ar - %s"
    if ($status -gt 0) {
        Write-Host "⚠️  $branch : $status uncommitted files" -ForegroundColor Yellow
    } else {
        Write-Host "✅ $branch : clean" -ForegroundColor Green
    }
    Write-Host "   Last: $lastCommit"
    Pop-Location
}
```

---

## 长时间任务管理（>24h）

大工程或受网络/硬件等非开发因素影响时，任务可能超过 24 小时。需要特殊标注和管理。

### 长任务标注规范

在 LOG.md 和 status 文件中使用以下标记：

```markdown
### [2026-02-28T10:00:00Z] Step 4: 模型训练 ⏳🕐
- 预估耗时: **48h**（GPU 训练）
- 实际开始: 2026-02-28T10:00:00Z
- 预计完成: 2026-03-02T10:00:00Z
- 类型: long-running (>24h)
- 阻塞因素: GPU 资源 / 网络传输
- 检查点: 每 6h 检查一次 loss 曲线
- 中断恢复: 从最近 checkpoint 恢复（output/checkpoint-xxx/）

### [2026-03-01T08:00:00Z] Step 4 检查点 #1
- 已运行: 22h / 48h (46%)
- 当前 loss: 0.45 (持续下降 ✅)
- GPU 利用率: 98%
- 预估完成时间: 维持原预估

### [2026-03-02T12:30:00Z] Step 4: 模型训练 ✅
- 实际耗时: **50.5h**（比预估多 2.5h，因网络抖动导致 data loader 重试）
- 最终 loss: 0.12
```

### Status 文件扩展字段

```yaml
# status/training.status
agent: training
status: in_progress
type: long_running          # 标记为长任务
started_at: 2026-02-28T10:00:00Z
estimated_duration_h: 48    # 预估小时数
next_checkpoint: 2026-02-28T16:00:00Z  # 下次检查时间
checkpoint_interval_h: 6    # 检查间隔
blocking_factors:           # 阻塞/风险因素
  - GPU 满载，无法加速
  - 训练数据需从远程下载
recovery_strategy: "从最近 checkpoint 恢复，配置在 output/ 目录"
```

### 长任务管理规则

```
1. 预估 >4h 的任务必须标注 type: long_running
2. 设置 checkpoint_interval（建议 ≤6h）
3. 每个 checkpoint 记录进度百分比 + 关键指标
4. 标注阻塞因素和恢复策略
5. 网络/硬件导致的延迟单独记录原因
6. 超过预估 20% 时主动上报给 Leader/人类
7. Orchestrator 不要因为长任务超时就判定为 failed
```
