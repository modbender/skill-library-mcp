# learning-system-skill

AI 领域系统学习体系 Skill，适用于 [OpenClaw](https://github.com/openclaw/openclaw) Agent。

将零散的资讯、调研、代码实战转化为体系化的 AI 领域专业知识。

## 核心理念

**输入不等于学习。** 看了 100 篇推文不代表懂了推理优化。改了 3 个 MCP bug 不代表吃透了 MCP 协议。

学习 = 输入 + 加工 + 关联 + 输出。

## 功能

- 📊 **AI 知识图谱** — 6 大领域、31+ 主题，三级掌握程度标记（🔴入门 🟡熟悉 🟢精通）
- 📝 **深度学习笔记** — 基于实战的主题深入研究，含标准化模板
- 🔄 **实战复盘** — 每次 PR/问题解决后提炼学习点
- 🔗 **关联网络** — 技术关联、实战关联、对比关联
- ⏰ **每周学习回顾** — 自动化周期性知识管理
- 🔧 **健康检查** — 分析知识图谱健康度，给出改进建议
- 🧮 **Mastery Score** — 基于 recency × repetition × depth 的自动掌握程度评分

## 4 种模式

| 命令 | 模式 | 说明 |
|------|------|------|
| `--mode deep-dive` | 深度研究 | 选题 → 研究 → 写笔记 → 更新图谱 |
| `--mode recap` | 实战复盘 | 分析 PR/改动 → 提炼知识点 → 关联图谱 |
| `--mode review` | 每周回顾 | 汇总本周 → 更新图谱 → 生成周报 |
| `--mode health` | 健康检查 | 运行脚本输出报告 |

附加参数：`--topic <name>`（指定主题）、`--quick`（跳过确认）

## Mastery Score 算法

自动扫描 memory 日志和深度笔记，计算每个主题的掌握分数：

```
score = Σ (weight × e^(-days_ago × ln2 / 30))
```

| 因子 | 说明 |
|------|------|
| **Recency** | 指数衰减，半衰期 30 天。今天 = 1.0，30 天前 = 0.5 |
| **Repetition** | 跨不同日期的接触次数累加 |
| **Depth** | deep-dive ×3.0，PR/复盘 ×2.0，普通提及 ×1.0 |

分数阈值：≥8.0 建议 🟢，≥3.0 建议 🟡，<3.0 建议 🔴

```bash
python3 scripts/mastery_score.py          # 表格报告
python3 scripts/mastery_score.py --json   # 附加 JSON 输出
```

输出示例：

```
| 主题              | 当前 | Score | 建议 | 接触次数 | 最近 | 变更 |
|-------------------|------|-------|------|----------|------|------|
| MCP 协议          | 🟢  |  6.32 | 🟡  |        4 |   4d | ⬇️ 考虑降级 |
| Agent 可观测性     | 🔴  |  3.76 | 🟡  |        4 |   0d | ⬆️ 建议升级 |
```

## 文件结构

```
learning-system/
├── SKILL.md                              # Skill 定义（工作流 checklist）
├── README.md
├── scripts/
│   ├── health_check.py                   # 健康检查
│   └── mastery_score.py                  # Mastery Score 计算
└── references/
    ├── deep-dive-template.md             # 深度笔记模板
    ├── recap-template.md                 # 实战复盘模板
    ├── knowledge-map-rules.md            # 图谱升级规则
    ├── quality-checklist.md              # 交付质量检查
    ├── weekly-review-template.md         # 周报模板
    └── weekly-review-guide.md            # 每周回顾指南
```

配合使用的笔记目录（需自行创建）：

```
notes/areas/
├── ai-knowledge-map.md               # 知识图谱
├── deep-dives/                        # 深度笔记
└── weekly-reviews/                    # 每周回顾
```

## 使用方式

### 1. 安装

```bash
cp -r learning-system ~/.openclaw/workspace/skills/
```

### 2. 初始化笔记目录

```bash
mkdir -p ~/.openclaw/workspace/notes/areas/{deep-dives,weekly-reviews}
```

### 3. 运行

```bash
# 健康检查
python3 scripts/health_check.py

# Mastery Score
python3 scripts/mastery_score.py
```

### 4. 配置每周回顾 Cron

在 OpenClaw 中配置 cron job，每周日晚自动触发学习回顾。

## 掌握程度标记

| 等级 | 标记 | 标准 |
|------|------|------|
| 入门 | 🔴 | 听说过，知道是什么 |
| 熟悉 | 🟡 | 读过源码或论文，能解释原理 |
| 精通 | 🟢 | 有实战经验，能独立设计和排错 |

## License

MIT
