# Markdown Output Format

This document defines the standard markdown output format for AI Daily news.

---

## Template

```markdown
# AI Daily · {年}年{月}月{日}日

> {一句话核心摘要}

## 核心摘要

{3-5条核心要点，每条一句话}

## {分类名称}

### [{标题}](链接)

{详细摘要}

**关键信息**: {相关标签}

---

数据来源: smol.ai
生成时间: {YYYY-MM-DD HH:MM}
```

---

## Complete Example

```markdown
# AI Daily · 2026年1月13日

> Anthropic 整合 Agent 产品线，Google 发布医疗 AI 模型，LangChain 推出 Agent 构建工具

## 核心摘要

- Anthropic 发布 Cowork 统一 Agent 平台，整合 Claude Code 和 MCP
- Google 开源 MedGemma 1.5 医疗多模态模型，支持 3D 影像分析
- LangChain Agent Builder 正式发布，支持内存和人工审核循环
- 社区讨论"Vibe Coding"定义，强调工程师验证的重要性
- 开源项目快速复制 Cowork 功能，Agent 技术商品化加速

## 模型发布

### [MedGemma 1.5](https://news.smol.ai/issues/26-01-13-not-much/)

Google 发布 4B 参数医疗多模态模型 MedGemma 1.5，专为离线医疗场景设计。支持 3D 体积（CT/MRI）处理、纵向对比和解剖定位。声称在 EHR 理解上达到 89.6% 准确率（+22%），X 光定位达到 38% IoU。

**关键信息**: Google, MedGemma, 医疗AI, 多模态, 3D影像

### [Open 复现 Cowork](https://news.smol.ai/issues/26-01-13-not-much/)

开发者使用 QEMU + bubblewrap + seccomp 构建了跨平台类 Cowork VM 环境。这表明 Agent shell 技术正在快速商品化，成为基础设施而非产品护城河。

**关键信息**: 开源, QEMU, Agent, 虚拟化

## 产品动态

### [Cowork 品牌整合](https://news.smol.ai/issues/26-01-13-not-much/)

Anthropic 将其 AI agent 产品统一到 Cowork 品牌，整合了之前的 Claude Code、Claude for Chrome 等工具。使用 Apple 的虚拟化技术和 bubblewrap 实现安全沙箱。

**关键信息**: Anthropic, Cowork, Claude Code, MCP

### [LangChain Agent Builder GA](https://news.smol.ai/issues/26-01-13-not-much/)

LangChain 宣布 Agent Builder 正式发布（GA），提供无代码但强大的 agent 编排功能：内存、触发器、人工审核循环和 agent 收件箱。

**关键信息**: LangChain, Agent Builder, 编排, 工具链

## 研究方向

### [MemRL: 记忆即强化学习](https://news.smol.ai/issues/26-01-13-not-much/)

DAIR AI 强调 MemRL 方法，将记忆检索视为强化学习问题。保持基础模型冻结，学习情节记忆的 Q 值（意图-经验-效用），两阶段检索：语义过滤 + 效用排序。

**关键信息**: MemRL, 强化学习, 记忆检索, DAIR AI

### [递归语言模型 (RLMs)](/root/ai-daily-skill/docs/2026-01-12.html)

Omar Khattab 等人指出大多数"子 agent"实现错过了核心思想：需要类似指针的符号访问提示词来递归遍历。这可以实现超过 1000 万 tokens 的上下文而无需重新训练。

**关键信息**: RLMs, 递归模型, 长上下文, 符号访问

## 工具框架

### [Diffusers 统一注意力后端](https://news.smol.ai/issues/26-01-13-not-much/)

Hugging Face Diffusers 发布统一注意力后端，结合了 Ring 和 Ulysses 的属性。这是持续推动注意力内核/后端可互换和性能可移植化的一部分。

**关键信息**: Hugging Face, Diffusers, 注意力机制

### [量化的注意事项](https://news.smol.ai/issues/26-01-13-not-much/)

TensorPro 报告称 MXFP4 量化的注意力可能破坏因果建模，发布了诊断和修复"泄漏量化"行为的方法。对于从业者："以 FP8/4 位训练"日益可行，但数值边缘情况仍是活跃的研究/运维问题。

**关键信息**: 量化, FP8, MXFP4, 数值稳定性

## 关键词

#Anthropic #Google #MedGemma #LangChain #Agent #MemRL #RLMs #Diffusers #量化

---

数据来源: smol.ai
生成时间: 2026-01-15 10:30
```

---

## Category Names

Use these Chinese category names:

| Category | Chinese Name | Icon |
|----------|--------------|------|
| Model Releases | 模型发布 | 🤖 |
| Product Updates | 产品动态 | 💼 |
| Research | 研究论文 | 📚 |
| Tools & Frameworks | 工具框架 | 🛠️ |
| Funding & M&A | 融资并购 | 💰 |
| Industry Events | 行业事件 | 🏆 |

---

## Output Guidelines

1. **Title format**: `# AI Daily · {年}年{月}月{日}日`
2. **Summary**: 3-5 bullet points, one sentence each
3. **Categories**: Use category sections above
4. **Links**: Include original smol.ai links
5. **Keywords**: 5-10 hashtags, comma separated
6. **Footer**: Source and generation time
