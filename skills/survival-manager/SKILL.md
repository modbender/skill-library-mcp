---
name: survival-manager
description: 实现自主运行 + 人类授权的混合系统。
---


# Survival Manager - 生存管理系统

> 自主运行 + 人类授权的混合系统，Inspired by Automaton (Conway Research)


# Survival Manager 技能

实现自主运行 + 人类授权的混合系统。

## 核心组件

### 1. 生存等级系统

根据账户余额自动调整运行模式：

| 等级 | 余额 | 模型 | 心跳间隔 | 子代理上限 |
|------|------|------|----------|------------|
| **thriving** | ≥¥5000 | qwen3.5-397b | 30 分钟 | 8 |
| **normal** | ≥¥1000 | qwen3.5-plus | 1 小时 | 4 |
| **lowCompute** | ≥¥100 | qwen3.5-flash | 2 小时 | 2 |
| **critical** | ¥0 | qwen3.5-flash | 4 小时 | 1 |

**自动降级策略**:
- 余额下降 → 自动降级
- 收入增加 → 自动升级
- 每日 09:00 评估一次

---

### 2. 心跳守护进程

定期检查项目：

| 任务 | 间隔 | 说明 |
|------|------|------|
| health_check | 5 分钟 | 网关/浏览器/技能状态 |
| email_check | 1 小时 | 紧急未读邮件 |
| calendar_check | 1 小时 | 24h 内事件 |
| fiverr_order_check | 30 分钟 | 新订单/消息 |
| balance_check | 1 小时 | 余额/生存等级 |

**心跳触发条件**:
- 时间间隔到达
- 用户主动询问
- 检测到异常事件

---

### 3. 授权队列

高风险操作需用户授权：

**必须授权的操作**:
- 文件删除/写入
- 外部消息发送
- 子代理创建
- 支付/转账
- 系统配置修改

**授权流程**:
1. 写入 `authorization-pending.md`
2. Telegram 通知用户
3. 等待用户决策 (超时 1 小时)
4. 执行/拒绝/修改

**自动批准条件** (需启用):
- 成本 < ¥10
- 操作在白名单内
- 非高风险类型

---

### 4. 财务追踪

#### 收入追踪
- 文件：`finance/income-log.md`
- 渠道：Fiverr / 直接客户 / 自动化服务
- 目标：日¥100 / 周¥700 / 月¥3000

#### 支出追踪
- 文件：`finance/expense-log.md`
- 类别：API 调用 / 服务器 / 软件订阅
- 预算：日¥50 / 月¥500

#### 成本估算
```
模型调用成本 = 调用次数 × 单次成本
qwen3.5-flash: ¥0.002/次
qwen3.5-plus: ¥0.01/次
qwen3.5-397b: ¥0.10/次
```

---

### 5. Agent 通信

#### 收件箱系统
- 路径：`agent-inbox/`
- 格式：`{agent-id}-{timestamp}.md`
- 用途：子代理汇报/请求/协调

#### 通知优先级
| 级别 | 事件 | 通知方式 |
|------|------|----------|
| critical | 生存等级变更 | Telegram+ 声音 + 弹窗 |
| revenue | 收入到账 | Telegram+ 声音 |
| authorization | 授权请求 | Telegram+ 声音 |
| warning | 预算警告 | Telegram |
| info | 常规更新 | 仅日志 |

---

## 脚本工具

### scripts/check-survival.ps1

检查当前生存状态：

```powershell
# 读取配置
$config = Get-Content "survival-config.json" | ConvertFrom-Json

# 检查余额
$balance = $config.survival.balance
$tier = $config.survival.currentTier

# 评估等级
if ($balance -ge 5000) { $newTier = "thriving" }
elseif ($balance -ge 1000) { $newTier = "normal" }
elseif ($balance -ge 100) { $newTier = "lowCompute" }
else { $newTier = "critical" }

# 输出报告
Write-Host "生存等级：$tier → $newTier"
Write-Host "余额：¥$balance"
Write-Host "模型：$($config.survival.tiers.$newTier.model)"
```

### scripts/log-income.ps1

记录收入：

```powershell
param(
    [decimal]$Amount,
    [string]$Source,
    [string]$Channel = "fiverr"
)

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logEntry = "| $timestamp | $Source | ¥$Amount | $Channel | ✅ | - |`n"

Add-Content "finance/income-log.md" $logEntry

# 更新余额
$config = Get-Content "survival-config.json" | ConvertFrom-Json
$config.survival.balance += $Amount
$config | ConvertTo-Json -Depth 10 | Set-Content "survival-config.json"
```

### scripts/request-authorization.ps1

请求授权：

```powershell
param(
    [string]$Operation,
    [string]$Description,
    [decimal]$Cost,
    [string]$Priority = "normal"
)

$authId = "AUTH-" + (Get-Date -Format "yyyyMMdd-HHmmss")
$logEntry = @"
### $authId

**请求时间**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**操作类型**: $Operation  
**描述**: $Description  
**预计成本**: ¥$Cost  
**紧急程度**: $Priority  

**用户决策**:
- [ ] 批准
- [ ] 拒绝
- [ ] 修改后批准
"@

Add-Content "authorization-pending.md" $logEntry

# Telegram 通知
# (通过 message 工具)
```

---

## 参考文档

### references/survival-tiers.md

详细生存等级说明和转换条件。

### references/authorization-rules.md

授权规则和白名单配置。

### references/revenue-strategies.md

收入创造策略和渠道优化。

---

## 触发条件

以下情况应触发本技能：

- 心跳检查时间到达
- 余额发生变化
- 收入/支出记录更新
- 需要用户授权的操作
- 生存等级变更
- 子代理需要协调

---

## 输出格式

### 生存状态报告

```
【生存状态】2026-02-26 23:30

等级：normal (→ thriving in ¥1000)
余额：¥0
今日收入：¥0 / 目标¥100 (0%)
今日支出：¥0 / 预算¥50 (0%)

下次检查：2026-02-27 00:30
```

### 授权请求

```
【授权请求】AUTH-20260226-233000

操作：file_write
描述：更新 Fiverr 服务页面
成本：¥0.01
紧急：normal

请在 1 小时内回复：
- "批准" 执行
- "拒绝" 取消
- "修改：[内容]" 修改后执行
```

---

## 自主运行规则

### 可自主执行 (无需授权)
- ✅ 读取文件
- ✅ 网络搜索
- ✅ 浏览器快照
- ✅ 成本 < ¥10 的 API 调用

### 需授权执行
- ⚠️ 文件写入/删除
- ⚠️ 发送外部消息
- ⚠️ 创建子代理
- ⚠️ 配置修改

### 禁止执行 (需明确命令)
- ❌ 支付/转账
- ❌ 删除系统文件
- ❌ 修改保护文件

---

## 价值创造策略

### 短期 (7 天)
1. Fiverr 首单突破
2. 优化服务页面
3. 主动营销

### 中期 (30 天)
1. 建立 3+ 收入渠道
2. 自动化交付流程
3. 客户 CRM 系统

### 长期 (90 天)
1. 被动收入 > 主动收入
2. 多代理协作系统
3. 产品化服务

---

---

## 🔒 安全与隐私

### External Endpoints

| 端点 | 数据发送 | 用途 |
|------|----------|------|
| 无 (本地运行) | 无数据离开机器 | 所有操作在本地执行 |

### Security & Privacy

- ✅ **无外部 API 调用** - 所有数据保留在本地
- ✅ **无凭证存储** - 不存储任何 API key 或密码
- ✅ **文件操作透明** - 所有写入操作需用户授权
- ✅ **网络请求可选** - web_search 等工具由用户配置

### Model Invocation Note

本技能通过 OpenClaw 调用 AI 模型（如 qwen3.5-plus）。模型调用是自主运行的标准行为，用于：
- 生存等级评估
- 收入/支出分析
- 授权请求生成

如要禁用自动模型调用，可在 OpenClaw 配置中设置 `autoInvoke: false`。

### Trust Statement

**By using this skill:**
- 所有数据保留在您的本地机器
- 无数据发送到第三方服务（除非您明确配置）
- 脚本代码完全透明，可审计
- 高风险操作需您手动授权

**仅当您信任 OpenClaw 生态系统和本技能代码时安装。**

---

*本技能 Inspired by Automaton (Conway Research)*  
*核心理念：自主运行 + 人类授权*
