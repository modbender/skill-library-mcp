## 1. Paper Snapshot

- ArXiv ID: 2601.14027
- Title: Numina-Lean-Agent: An Open and General Agentic Reasoning System for Formal Mathematics
- Authors: Junqi Liu, Zihao Zhou, Zekai Zhu, Marco Dos Santos, Weikun He, Jiawei Liu, Ran Wang, Yunzhou Xie, Junqiao Zhao, Qiufeng Wang, Lihong Zhi, Jia Li, Wenda Li
- Publish date: 2026-01-20
- Primary category: cs.AI
- Reading basis: source (source/source_extract/example_paper.tex)

## 2. Research Objective

本文核心问题是：形式化数学是否可以由“通用编码智能体 + 强工具链”有效完成，而不必依赖窄域定制的专用定理证明模型。作者目标是构建一个开放、模块化、可替换底座模型的系统，让智能体能够在 Lean 反馈回路、语义检索和辅助推理工具支持下稳定推进证明。论文还希望验证这种架构不仅能在竞赛基准上取得领先结果，也能在真实的人机协作形式化项目中长期工作。

## 3. Method Overview

Numina-Lean-Agent 以通用 coding agent 为核心，并围绕 Lean 构建 MCP 工具生态。Lean-LSP-MCP 提供对 Lean 项目的细粒度交互能力，包括目标态、诊断信息、证明执行与策略试探。LeanDex 提供 Lean 生态语义检索，帮助系统复用现有定义和定理。Informal Prover 使用“生成-校验-修正”循环，先构造非形式化证明草稿，再根据反馈迭代提升。Discussion Partner 在主推理路径受阻时提供多模型讨论支持。

对于长程或高难任务，系统采用递归蓝图流程：先分解子目标，再在“形式化尝试 - 根据 Lean 报错修正”的循环中推进。面对瓶颈子问题（文中重点例子为 Putnam A5），系统可引入子智能体分解策略以拓展搜索覆盖，同时在基准评测设置下依然遵守串行执行约束。

## 4. Data and Evaluation

论文包含两条评测主线。

- 基准证明主线：Putnam 2025 形式化题集（12 题），对比 Aristotle、Seed-Prover 1.5、Axiom。
- 协作形式化主线：与数学家和 Lean 专家协作完成 Effective Brascamp-Lieb inequalities 的形式化工作。

Putnam 评测条件被明确限制，以保证可比性。

- 仅允许串行执行，不使用并行求解。
- 解题过程中禁用互联网搜索。
- 题目陈述与 Seed-Prover 设置保持一致。
- 报告预算约束：常规题目单题约 50 美元，困难题（如 A5、B6）预算显著更高。

此外，论文提供了工具组件消融（如去掉 informal prover、去掉 subagent 策略）和效率视角（耗时、代码长度），使读者不仅看到 solve rate，也能看到成本和工程可行性。

## 5. Key Results

在 Putnam 2025 上，Numina-Lean-Agent 达到 12/12 solved，与最强系统持平，并超过若干 solved 数更低的基线。消融结果显示系统性能明显依赖 informal 推理和分解机制：去掉 informal prover 后成绩显著下滑，加入后恢复大部分题目，再加 subagent 策略可补齐最困难题。

论文还用 B4 展示 informal-prover 设计价值：在相近调用预算下，迭代式“批判-重写”流程可在较少轮次内完成，而独立采样策略在更多轮次仍未成功。效率表明，尽管全程串行，系统在部分题目上仍有较好时间表现；代码长度对比也显示在若干题目上比其他 agentic 基线更短，说明证明轨迹在这些案例中更紧凑。

在 Brascamp-Lieb 协作案例中，团队在不足两周的间歇协作中产出超过 8000 行 Lean 代码，智能体贡献了数十个新的形式化对象（定义、引理、定理）。这说明该系统并非只适用于榜单任务，也能支持真实研究型形式化工作。

## 6. Strengths

- 证明了“通用编码智能体 + 工具链”可以在形式化数学基准上达到 SOTA 级别表现。
- 架构模块化明确，底座模型和工具组件可替换，扩展性强。
- 同时给出基准评测与真实协作案例，外部有效性更好。
- 不仅报告 solved 数，还给出消融、时间、预算和代码长度等工程指标。
- 代码与结果开放发布，相比纯闭源系统更有复现实用价值。

## 7. Limitations and Risks

- 生成的 Lean 代码仍可能冗长且不够 idiomatic，后续人工重构成本较高。
- 类型转换与库接口边角问题依然容易成为失败瓶颈，即使高层数学思路正确。
- 基准高分并不等于可直接达到 Mathlib 级工程风格。
- 极难样例的预算和耗时可能显著膨胀，影响规模化落地。
- 多工具编排提高系统复杂度，失败时根因定位也更困难。

## 8. Reproducibility Notes

作者公开了代码与形式化解答，但严格复现仍需要对齐多项条件：Lean 版本、MCP 工具行为、检索索引、提示与运行策略。若要公平对比论文结果，应保持相同评测约束（串行执行、解题期间禁网）及近似预算设置。对于协作案例，流程文档和人机协作协议同样关键，不能只依赖代码产物。

## 9. Practical Takeaways

一个重要实践结论是：形式化证明已可被视作“智能体工程问题”，而不仅是“模型训练问题”。在不专门训练证明器的前提下，强化 Lean 交互回路、检索质量和迭代规划，仍可显著提升最终解题能力。落地时应预留人工审阅和重构环节，以平衡求解能力与代码优雅性。对于强调可扩展性和工具整合的团队，这种架构具有较高现实价值。

## 10. Brief Conclusion

本文提出 Numina-Lean-Agent，通过将通用编码智能体与 Lean 交互工具、语义检索和辅助推理模块组合，构建了一个可扩展的形式化推理系统。在 Putnam 2025 的严格串行与禁网条件下，系统达到 12/12 的解题结果，并通过消融实验证明 informal 推理与 subagent 分解对性能提升具有关键作用。除基准任务外，Brascamp-Lieb 协作案例表明该架构能够支撑持续的人机协作研究级形式化，产出达到多千行规模。整体上，论文为“以工具为中心的通用智能体路线”提供了充分且具有工程意义的实证支持。
