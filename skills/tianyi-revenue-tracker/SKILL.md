---
clawdbot:
  name: revenue-tracker
  version: 1.0.0
  requires.env: []
  files: ["scripts/*"]
  homepage: https://github.com/openclaw_ceo/skills/revenue-tracker
---

# Revenue Tracker - 收益追踪与定价系统

> 完整的收益管理和任务定价系统，与 survival-manager 协同工作


# Revenue Tracker 技能

完整的收益管理和任务定价系统。

---

## 核心功能

### 1. 收入追踪

**渠道**:
- Fiverr (平台费 20%)
- 直接客户 (无平台费)
- 自动化服务 (被动收入)
- 其他

**追踪字段**:
| 字段 | 说明 |
|------|------|
| 日期 | 交易日期 |
| 来源 | 客户/订单描述 |
| 金额 | 净收入 (扣除平台费) |
| 渠道 | fiverr/direct/automation |
| 状态 | pending/completed/cancelled |
| 备注 | 额外说明 |

---

### 2. 支出追踪

**类别**:
- API 调用 (模型使用)
- 服务器 (VPS/云主机)
- 软件订阅 (工具/服务)
- 其他

**预算控制**:
| 周期 | 预算 | 警告线 |
|------|------|--------|
| 每日 | ¥50 | 80% (¥40) |
| 每月 | ¥500 | 80% (¥400) |

---

### 3. 任务定价系统

**定价公式**:
```
基础价格 = (预估时间 × 时薪) + 模型成本 + 平台费

时薪建议:
- 简单任务：¥50/h
- 中等任务：¥100/h
- 复杂任务：¥200/h
- 专家级：¥500/h

模型成本估算:
- qwen3.5-flash: ¥0.002/次
- qwen3.5-plus: ¥0.01/次
- qwen3.5-397b: ¥0.10/次

平台费:
- Fiverr: 20%
- 直接客户：0%
```

**定价模板**:

| 服务类型 | 基础价 | 建议报价 |
|----------|--------|----------|
| OpenClaw 安装 | ¥100 | ¥150-200 |
| Telegram 机器人 | ¥200 | ¥300-500 |
| 自动化脚本 | ¥150 | ¥200-400 |
| 数据采集 | ¥100 | ¥150-300 |
| 内容创作 | ¥80 | ¥100-200 |

---

### 4. 财务报表

**日报** (每日 23:00 生成):
- 今日收入
- 今日支出
- 净利润
- 订单数量
- 目标完成度

**周报** (每周日生成):
- 本周总收入
- 本周总支出
- 本周净利润
- 收入渠道分布
- 趋势分析

**月报** (每月 1 日生成):
- 月度总收入
- 月度总支出
- 月度净利润
- 客户分析
- 下月目标

---

## 脚本工具

### scripts/add-transaction.ps1

添加交易记录：

```powershell
# 收入
.\add-transaction.ps1 -Type income -Amount 100 -Source "Fiverr Order #123" -Channel fiverr

# 支出
.\add-transaction.ps1 -Type expense -Amount 10 -Category "API" -Description "Model calls"
```

### scripts/generate-report.ps1

生成财务报表：

```powershell
# 日报
.\generate-report.ps1 -Period daily

# 周报
.\generate-report.ps1 -Period weekly

# 月报
.\generate-report.ps1 -Period monthly
```

### scripts/calculate-price.ps1

计算任务价格：

```powershell
.\calculate-price.ps1 -Hours 2 -Complexity medium -Platform fiverr
```

---

## 触发条件

- 收入/支出发生时
- 用户请求报价
- 定时生成报表
- 预算警告触发

---

## 输出格式

### 收入确认

```
【收入确认】2026-02-26

来源：Fiverr Order #12345
金额：¥100 (平台费¥20, 净收入¥80)
渠道：fiverr
新余额：¥80

生存等级：normal (→ lowCompute in ¥20)
```

### 定价建议

```
【定价建议】

任务：OpenClaw 安装配置
预估时间：2 小时
复杂度：中等
模型成本：¥0.50

成本计算:
- 人工：2h × ¥100/h = ¥200
- 模型：¥0.50
- 平台费 (20%): ¥40

建议报价：¥250-300
最低价：¥200 (保本)
```

---

## 与 survival-manager 集成

- 收入更新 → 触发余额检查 → 可能升级生存等级
- 支出更新 → 触发预算检查 → 可能警告
- 定价建议 → 参考当前生存等级 (lowCompute 时优先便宜模型)

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
- ✅ **财务数据本地存储** - 不上传到任何云服务

### Model Invocation Note

本技能通过 OpenClaw 调用 AI 模型进行：
- 定价建议计算
- 财务报表分析
- 收入趋势预测

模型调用是自主运行的标准行为，可在 OpenClaw 配置中设置 `autoInvoke: false` 禁用。

### Trust Statement

**By using this skill:**
- 所有财务数据保留在您的本地机器
- 无数据发送到第三方服务
- 脚本代码完全透明，可审计
- 高风险操作需您手动授权

**仅当您信任 OpenClaw 生态系统和本技能代码时安装。**

---

*Inspired by Automaton's value creation principle*
