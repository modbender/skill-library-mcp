---
name: learning-system
description: "AI 领域系统学习体系。管理知识图谱、深度学习笔记、实战复盘和关联网络。触发场景：学习计划、知识图谱更新、深度研究某个 AI 主题、实战复盘总结、调研后沉淀知识、每周学习回顾。当用户说'学了什么'、'总结一下'、'沉淀知识'、'复盘'、'更新图谱'、'深入研究'、'写笔记'、'学习回顾'、'review what I learned'、'update knowledge map'、'deep dive'、'recap'、'what did I learn' 时使用。当改完代码/读完论文/做完调研后需要提炼和归纳时使用。"
argument-hint: "[--mode deep-dive|recap|review|health] [--topic name] [--quick]"
---

# Learning System

将零散的资讯、调研、代码实战转化为体系化的 AI 领域专业知识。

## 核心理念

**输入不等于学习。** 看了 100 篇推文不代表懂了推理优化。改了 3 个 MCP bug 不代表吃透了 MCP 协议。学习 = 输入 + 加工 + 关联 + 输出。

## 模式选择

根据 `$ARGUMENTS` 或用户意图选择模式：

| 参数 | 模式 | 说明 |
|------|------|------|
| `--mode deep-dive` | 深度研究 | 选题 → 研究 → 写笔记 → 更新图谱 |
| `--mode recap` | 实战复盘 | 分析 PR/改动 → 提炼知识点 → 关联图谱 |
| `--mode review` | 每周回顾 | 汇总本周 → 更新图谱 → 生成周报 |
| `--mode health` | 健康检查 | 运行 `scripts/health_check.py` 输出报告 |
| 无参数 | 自动判断 | 根据上下文推断最合适的模式 |

附加参数：
- `--topic <name>`: 指定主题（deep-dive 模式）
- `--quick`: 跳过确认节点，全自动执行

## 文件结构

```
notes/areas/
├── ai-knowledge-map.md           # 知识图谱（掌握程度标记）
├── deep-dives/                    # 深度学习笔记
│   ├── mcp-tool-call-design.md
│   └── ...
└── weekly-reviews/                # 每周学习回顾
    ├── 2026-W07.md
    └── ...
```

---

## Mode: 深度研究 (deep-dive)

Copy this checklist and check off items as you complete them:

### Deep Dive Progress:
- [ ] Step 1: 选题 ⚠️ REQUIRED
  - [ ] 1.1 如果 `--topic` 已指定，直接使用
  - [ ] 1.2 否则，检查最近 3 天的 memory 日志和 PR 记录
  - [ ] 1.3 问自己：**哪个技术点是我刚接触但还没真正理解的？**
  - [ ] 1.4 问自己：**这个主题能串联哪些已有知识？**（越多越好）
  - [ ] 1.5 确认选题范围不要太宽（"推理优化"太大，"vLLM PagedAttention 实现"刚好）
- [ ] Step 2: 确认选题 ⚠️ REQUIRED (除非 `--quick`)
  - [ ] 向用户确认：选题 + 预计关联的知识点 + 预计产出
- [ ] Step 3: 研究
  - [ ] 3.1 Load `references/deep-dive-template.md` 获取笔记模板
  - [ ] 3.2 查找相关源码、论文、文档
  - [ ] 3.3 如果有对应的 AI/ML skill，按需加载参考
- [ ] Step 4: 写笔记
  - [ ] 4.1 在 `notes/areas/deep-dives/` 创建笔记文件
  - [ ] 4.2 问自己：**我能用自己的话向别人解释清楚吗？** 如果不能，说明还没真正理解
  - [ ] 4.3 建立关联：`→ 关联: [主题](相对路径)`
- [ ] Step 5: 更新知识图谱
  - [ ] 5.1 Load `references/knowledge-map-rules.md` 获取升级标准
  - [ ] 5.2 更新 `notes/areas/ai-knowledge-map.md` 中对应主题的掌握程度
- [ ] Step 6: 交付检查
  - [ ] Load `references/quality-checklist.md` 逐项验证

---

## Mode: 实战复盘 (recap)

### Recap Progress:
- [ ] Step 1: 识别改动 ⚠️ REQUIRED
  - [ ] 1.1 确认要复盘的 PR/Issue/改动
  - [ ] 1.2 问自己：**这次改动中，哪个技术点是我之前不知道的？**
  - [ ] 1.3 问自己：**如果下次遇到类似问题，我能直接解决吗？**
- [ ] Step 2: 提炼知识点
  - [ ] 2.1 Load `references/recap-template.md` 获取复盘模板
  - [ ] 2.2 每个知识点关联到知识图谱的具体领域
  - [ ] 2.3 问自己：**两个请求同时打到这段代码会怎样？**（如果涉及并发）
  - [ ] 2.4 问自己：**在检查权限和实际操作之间，状态有没有可能被改变？**（如果涉及安全）
- [ ] Step 3: 写入日志
  - [ ] 在当天的 `memory/YYYY-MM-DD.md` 中增加复盘 section
- [ ] Step 4: 更新图谱（条件）
  - [ ] 如果有知识点升级，Load `references/knowledge-map-rules.md` 并更新

---

## Mode: 每周回顾 (review)

### Weekly Review Progress:
- [ ] Step 1: 收集本周输入 ⚠️ REQUIRED
  - [ ] 1.1 读取本周的 memory 日志（最近 7 天）
  - [ ] 1.2 检查本周新增/修改的深度笔记
  - [ ] 1.3 检查本周的 PR 和代码改动
- [ ] Step 2: 评估学习深度
  - [ ] 2.1 Load `references/knowledge-map-rules.md`
  - [ ] 2.2 对每个输入项判断：只是看了？理解了原理？有实战经验？
  - [ ] 2.3 问自己：**这周我在 AI 领域变强了吗？哪里变强了？**
  - [ ] 2.4 问自己：**哪些输入转化成了真正的知识？**
- [ ] Step 3: 更新知识图谱
  - [ ] 确认变更列表 ⚠️ REQUIRED (除非 `--quick`)
  - [ ] 更新 `notes/areas/ai-knowledge-map.md`
- [ ] Step 4: 生成周报
  - [ ] Load `references/weekly-review-template.md`
  - [ ] 写入 `notes/areas/weekly-reviews/2026-Wxx.md`
- [ ] Step 5: 发送摘要
  - [ ] 通过飞书发送给用户

---

## Mode: 健康检查 (health)

```bash
python3 scripts/health_check.py
```

输出知识图谱统计、深度笔记状态、本周活动量、改进建议。

---

## Mode: Mastery Score (mastery)

```bash
python3 scripts/mastery_score.py          # 表格报告
python3 scripts/mastery_score.py --json   # 附加 JSON 输出
```

自动计算每个知识图谱主题的掌握分数，基于：
- **Recency（时间衰减）**: 指数衰减，半衰期 30 天。今天接触 = 1.0，30 天前 = 0.5，60 天前 = 0.25
- **Repetition（重复次数）**: 跨不同日期的接触次数累加
- **Depth（深度权重）**: deep-dive 笔记 ×3.0，PR/复盘 ×2.0，普通提及 ×1.0

输出包含：分数排名、建议升降级、衰减警告（60 天未接触）。

---

## 关联网络

在深度笔记和复盘中主动建立关联。格式：`→ 关联: [主题](相对路径)`

| 关联类型 | 示例 |
|----------|------|
| 技术关联 | vLLM → PagedAttention → KV Cache 管理 |
| 实战关联 | gemini-cli OAuth PR → OAuth 2.1 协议 |
| 对比关联 | Flash Attention vs PagedAttention |

## 与其他 skill 的关系

- **para-second-brain**: 学习笔记存在 PARA 的 areas/ 下，自动被 memory_search 索引
- **85 个 AI/ML skills**: 作为参考资料，深度学习时按需加载对应 skill
- **openclaw-feeds / news-summary**: 资讯输入源，但不等于学习——需要加工和关联
