---
name: self-upgrade
description: OpenClaw 自我迭代升级技能。使用场景：配置自动修复、技能更新、依赖安装、版本检查、问题预防性修复。支持安全模式（需用户确认）和自动模式（低风险操作自动执行）。
---

# Self-Upgrade 技能

OpenClaw 系统的自我维护和升级能力。

## 核心原则

### 安全分级

| 风险等级 | 操作类型 | 执行策略 |
|----------|----------|----------|
| **低风险** | 日志清理、状态检查、配置格式化 | 自动执行 |
| **中风险** | 配置字段更新、技能包安装 | 需用户确认 |
| **高风险** | 服务重启、文件删除、版本升级 | 必须用户明确授权 |

### 升级策略

1. **向后兼容优先**: 保留旧配置字段（标记 deprecated）而非直接删除
2. **可回滚**: 重大变更前自动备份
3. **渐进式**: 分步执行，每步验证后再继续

---

## 核心流程

### 1. 版本检查

```powershell
# 检查当前版本
openclaw --version

# 检查配置版本
$config = Get-Content ~\.openclaw\openclaw.json | ConvertFrom-Json
$config.meta.lastTouchedVersion
```

### 2. 配置迁移

检测并迁移废弃字段：

```powershell
# 示例：authToken → auth.token
if ($config.gateway.authToken) {
    $config.gateway.auth = @{ token = $config.gateway.authToken }
    $config.gateway.PSObject.Properties.Remove('authToken')
}
```

### 3. 依赖检查

```powershell
# 检查必要技能
$requiredSkills = @('healthcheck', 'skill-creator', 'auto-diagnostic')
foreach ($skill in $requiredSkills) {
    if (-not (Test-Path "skills\$skill\SKILL.md")) {
        Write-Host "[MISSING] Skill: $skill"
    }
}

# 检查 npm 包版本
npm list -g openclaw
```

### 4. 自动修复

运行内置诊断：

```powershell
openclaw doctor --fix
```

### 5. 备份与回滚

```powershell
# 备份配置
$backupPath = "~\.openclaw\backups\openclaw-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
Copy-Item ~\.openclaw\openclaw.json $backupPath

# 回滚命令
Copy-Item $backupPath ~\.openclaw\openclaw.json
```

---

## 脚本工具

### scripts/self-upgrade.ps1

```powershell
param(
    [switch]$Auto,      # 自动模式（低风险操作）
    [switch]$DryRun,    # 仅预览，不执行
    [string]$BackupDir = "~\.openclaw\backups"
)

$ErrorActionPreference = "Stop"
$ConfigPath = "~\.openclaw\openclaw.json"

# 1. 创建备份
if (-not $DryRun) {
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }
    $backupPath = Join-Path $BackupDir "openclaw-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    Copy-Item $ConfigPath $backupPath
    Write-Host "[OK] Backup created: $backupPath" -ForegroundColor Green
}

# 2. 检查配置
try {
    $config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
    Write-Host "[OK] Config is valid JSON" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Config is invalid: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 3. 迁移废弃字段
$migrated = $false

if ($config.gateway.authToken) {
    Write-Host "[MIGRATE] gateway.authToken → gateway.auth.token" -ForegroundColor Yellow
    if (-not $DryRun) {
        $config.gateway.auth = @{ token = $config.gateway.authToken }
        $config.gateway.PSObject.Properties.Remove('authToken')
        $migrated = $true
    }
}

# 4. 保存变更
if ($migrated -and -not $DryRun) {
    $config | ConvertTo-Json -Depth 10 | Set-Content $ConfigPath
    Write-Host "[OK] Config updated" -ForegroundColor Green
    
    # 验证
    openclaw doctor --fix
}

# 5. 检查技能
$skillsPath = "D:\workspace\openclaw_ceo\skills"
if (Test-Path $skillsPath) {
    $skills = Get-ChildItem $skillsPath -Directory | Select-Object -ExpandProperty Name
    Write-Host "[OK] Found $($skills.Count) skills: $($skills -join ', ')" -ForegroundColor Green
}
```

---

## 参考文档

### references/upgrade-history.md

记录每次升级的详细信息，用于追溯和回滚。

### references/config-schema.md

配置文件的 schema 定义，用于验证迁移正确性。

---

## 触发条件

以下情况应触发本技能：

- 用户执行 `openclaw doctor --fix`
- 检测到配置字段已废弃（如 `authToken`）
- 版本升级后首次启动
- 技能加载失败（缺失或格式错误）
- 定期维护（如每周一次健康检查）

---

## 输出格式

升级报告应包含：

1. **升级摘要**: 执行了哪些变更
2. **备份位置**: 回滚所需信息
3. **验证结果**: 升级后状态检查
4. **后续建议**: 需要用户注意的事项

示例：

```
【升级报告】
时间：2026-02-26 21:30:00
模式：自动（低风险）

【执行变更】
✅ 迁移 gateway.authToken → gateway.auth.token
✅ 格式化配置文件
✅ 清理过期日志（>7 天）

【备份位置】
~\.openclaw\backups\openclaw-20260226-213000.json

【验证结果】
✅ 配置验证通过
✅ 网关运行正常
✅ 技能加载正常

【后续建议】
无需用户操作
```

---

## 安全约束

### 禁止自动执行的操作

- ❌ 删除用户数据文件
- ❌ 修改 API 密钥/令牌（除非明确授权迁移）
- ❌ 卸载已安装的技能
- ❌ 更改网络配置（端口、绑定地址）

### 必须备份的操作

- ✅ 配置文件修改
- ✅ 技能包安装/更新
- ✅ 依赖包升级

### 回滚机制

所有自动变更必须支持回滚：

```powershell
# 回滚到指定备份
.\self-upgrade.ps1 -RollbackTo "20260226-213000"
```
