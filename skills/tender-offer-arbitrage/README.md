# 🔍 Tender Offer Arbitrage Scanner

AI Agent Skill，自动扫描市场上的要约收购(Tender Offer)套利机会。

## 这是什么？

这是一个 **Agent-Native** 的 AI 技能文件。它不是一个独立运行的程序，而是教 AI Agent 如何像专业并购套利分析师一样工作的指令集。

Agent 会自动完成：
1. 🔍 搜索 SEC EDGAR、金融新闻网站，发现活跃的 Tender Offer
2. 📄 查阅官方 SEC 文件，验证要约价格、截止日、Odd-Lot 优先权等关键条款
3. 💰 获取实时股价，计算价差和预期收益
4. ⚠️ 评估每笔交易的风险（proration、条件、时间等）
5. 📊 按 Odd-Lot 投资者视角排名，生成完整的分析报告

## 使用方法

把这个目录放到你的 AI Agent 的 skill 目录中，然后告诉 Agent：

> "扫描当前市场上的要约收购套利机会"

### 兼容平台

| 平台 | Skill 目录 |
|------|-----------|
| Claude Code | `.claude/skills/` |
| Gemini | 项目根目录或 skill 目录 |
| OpenClaw | `~/.openclaw/skills/` |
| 其他 Agent | 任何支持读文件 + 网络搜索的 Agent |

## 文件结构

```
├── SKILL.md              ← 核心：Agent 工作流指令
├── _meta.json            ← Skill 元数据
├── config/
│   └── config.example.json
└── results/              ← Agent 生成的报告保存在这里
```

## 核心概念

- **Tender Offer** — 公司或第三方以溢价向股东公开收购股份
- **Odd-Lot 优先权** — 持有 <100 股的小股东可免受按比例缩减(proration)，100% 被接受
- **套利逻辑** — 以当前市价买入 ≤99 股，提交 tender 以要约价卖出，赚取确定性价差

## 报告示例

报告包含每笔交易的详细分析：

| 排名 | 股票 | 要约价 | 当前价 | 价差 | 收益测算(99股) | Odd-Lot | 推荐度 |
|------|------|--------|--------|------|--------------|---------|--------|
| ⭐1 | DCBO | $20.40 | $17.70 | 15.3% | ~$267 | ✅ | ⭐⭐⭐⭐⭐ |
| ⭐2 | YEXT | $5.75-$6.50 | $5.68 | 1.2%-14.4% | $7~$81 | ✅ | ⭐⭐⭐⭐ |

## 前置要求

- AI Agent 需要**网络搜索能力**

## License

MIT
