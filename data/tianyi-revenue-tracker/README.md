# Revenue Tracker 技能

[![ClawHub](https://img.shields.io/badge/ClawHub-revenue--tracker-blue)](https://clawhub.com)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://clawhub.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://clawhub.com)

> 💰 完整的收益管理和任务定价系统  
> 与 survival-manager 协同工作

---

## 📋 功能特性

- **收入追踪** - Fiverr/直接客户/自动化服务多渠道追踪
- **支出管理** - API 调用/服务器/软件订阅分类记录
- **利润计算** - 自动计算净利润率（扣除平台费）
- **定价建议** - 基于时间/复杂度/模型成本的智能报价
- **财务报表** - 日/周/月报自动生成
- **生存等级集成** - 收入更新自动触发余额评估

---

## 🚀 安装

```bash
# 通过 ClawHub CLI 安装
clawhub install revenue-tracker
```

---

## 📖 使用说明

### 记录收入

```powershell
# PowerShell
.\scripts\log-income.ps1 `
  -Amount 500 `
  -Source "Fiverr Order #12345" `
  -Channel "fiverr" `
  -Fee 0.20
```

### 记录支出

```powershell
.\scripts\log-expense.ps1 `
  -Amount 50 `
  -Category "API" `
  -Description "OpenClaw model calls"
```

### 获取定价建议

```powershell
.\scripts\calculate-price.ps1 `
  -TaskType "OpenClaw Installation" `
  -EstimatedHours 2 `
  -Complexity "medium"
```

输出示例：
```
【定价建议】

任务：OpenClaw Installation
预估时间：2 小时
复杂度：medium
模型成本：¥0.50

成本计算:
- 人工：2h × ¥100/h = ¥200
- 模型：¥0.50
- 平台费 (20%): ¥40

建议报价：¥250-300
最低价：¥200 (保本)
```

### 生成财务报表

```powershell
.\scripts\generate-report.ps1 -Period "weekly"
```

---

## 📊 收入渠道

| 渠道 | 平台费 | 结算周期 | 风险 |
|------|--------|----------|------|
| **Fiverr** | 20% | 14 天 | 低 |
| **直接客户** | 0% | 即时 | 中 |
| **自动化服务** | 0% | 持续 | 低 |
| **ClawHub 技能** | 10%+$0.50 | 月结 | 低 |

---

## 💡 定价策略

### 三层定价模型

| 层级 | 公式 | 适用场景 |
|------|------|----------|
| **成本价** | 人工 + 模型 + 平台费 | 促销/首单 |
| **标准价** | 成本价 × 1.5 | 常规订单 |
| **溢价款** | 成本价 × 2-3 | 紧急/复杂项目 |

### 时薪参考 (2026 市场)

| 技能水平 | 时薪范围 |
|----------|----------|
| 入门 | ¥50-100/h |
| 中级 | ¥100-300/h |
| 专家 | ¥300-800/h |
| 顶级 | ¥800+/h |

---

## 🔄 与 survival-manager 集成

- ✅ 收入更新 → 触发余额检查 → 可能升级生存等级
- ✅ 支出更新 → 触发预算检查 → 可能警告
- ✅ 定价建议 → 参考当前生存等级

---

## 📁 文件结构

```
finance/
├── income-log.md      # 收入日志
├── expense-log.md     # 支出日志
├── pricing-history.md # 定价历史
└── reports/           # 财务报表
    ├── daily/
    ├── weekly/
    └── monthly/
```

---

## ⚙️ 配置

编辑 `survival-config.json`：

```json
{
  "revenue": {
    "goals": {
      "daily": 100,
      "weekly": 700,
      "monthly": 3000
    },
    "pricing": {
      "hourlyRate": 100,
      "platformFee": 0.20,
      "minMargin": 0.30
    }
  }
}
```

---

## 📝 更新日志

### v1.0.0 (2026-03-01)
- 初始发布
- 收入/支出追踪
- 定价建议系统
- 财务报表生成
- survival-manager 集成

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 🔗 链接

- [ClawHub](https://clawhub.com)
- [OpenClaw 文档](https://docs.openclaw.ai)
- [GitHub Repo](https://github.com/openclaw_ceo/skills/revenue-tracker)
