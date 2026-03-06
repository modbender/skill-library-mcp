## 1. Paper Snapshot

- ArXiv ID: 2601.14027
- Title: Numina-Lean-Agent: An Open and General Agentic Reasoning System for Formal Mathematics
- Authors: Junqi Liu, Zihao Zhou, Zekai Zhu, Marco Dos Santos, Weikun He, Jiawei Liu, Ran Wang, Yunzhou Xie, Junqiao Zhao, Qiufeng Wang, Lihong Zhi, Jia Li, Wenda Li
- Publish date: 2026-01-20
- Primary category: cs.AI
- Reading basis: source (source/source_extract/example_paper.tex)

## 2. Research Objective

The paper asks whether formal mathematics can be solved effectively by a general coding agent with strong tools, instead of by a narrowly specialized theorem-proving model. The authors aim to build an open, modular system that can use Lean feedback loops, retrieval, and auxiliary reasoning tools while keeping the model backbone replaceable. They also want to test whether this design can handle both benchmark competition tasks and long-horizon collaborative formalization with humans.

## 3. Method Overview

Numina-Lean-Agent combines a coding-agent core with a Lean-centered MCP tool ecosystem. Lean-LSP-MCP provides fine-grained interaction with Lean projects, including goal states, diagnostics, proof execution, and tactic-level feedback. LeanDex adds semantic retrieval over Lean codebases to help the agent reuse relevant definitions and lemmas. An informal prover module uses a generator-verifier loop to draft, critique, and revise informal proof sketches before or during formal proof construction. A discussion-partner module allows multi-model consultation when the primary trajectory stalls.

For hard, long-horizon problems, the agent follows a recursive blueprint strategy. It first decomposes objectives into subgoals, then alternates between formalization attempts and revision rounds based on Lean errors and missing lemmas. For bottleneck subproblems (for example Putnam A5), the system can invoke subagent decomposition to parallelize reasoning branches conceptually, while still respecting the evaluation setting's sequential execution constraints.

## 4. Data and Evaluation

The paper reports two evaluation tracks.

- Benchmark proving track: Putnam 2025 formalized set (12 problems), compared with Aristotle, Seed-Prover 1.5, and Axiom.
- Collaborative research track: formalization work on Effective Brascamp-Lieb inequalities with a mathematician, a Lean expert, and the agent.

Benchmark conditions are explicitly constrained to reduce confounds.

- Sequential execution only (no parallel runs for solving).
- Internet search disabled during benchmark solving.
- Consistent problem statements aligned with Seed-Prover setup.
- Budget constraints are reported, with typical spend around USD 50 per problem and larger allocations on difficult instances (for example A5 and B6).

The paper also provides ablation studies for tool components (informal prover, subagent strategy) and efficiency views (time and proof code length), which helps separate pure solve-rate gains from practical cost-quality tradeoffs.

## 5. Key Results

On Putnam 2025, Numina-Lean-Agent reaches 12/12 solved, matching the strongest reported system and surpassing other baselines with lower solve counts. Ablation results show substantial dependence on the informal reasoning and decomposition machinery: removing the informal prover drops performance sharply, adding it recovers most tasks, and enabling subagent strategy closes the hardest remaining gaps.

The informal-prover design is further validated on problem B4: iterative critique-and-rewrite solves the task within a small number of rounds, while an independent-sampling baseline fails under comparable call budget. Efficiency tables show competitive wall-clock behavior despite strict sequential operation, including faster completion than some baselines on selected problems. Proof-length comparisons indicate shorter Lean code than other agentic baselines on multiple items, suggesting less redundant or less meandering formal traces in those cases.

In the Brascamp-Lieb collaboration case, the team produces more than 8,000 lines of Lean over less than two weeks of intermittent work, and the agent contributes dozens of new formal objects (definitions, lemmas, theorems). This supports the claim that the system is not only a benchmark solver but also useful in realistic research-style formalization workflows.

## 6. Strengths

- Demonstrates that a tool-rich general coding agent can match state-of-the-art benchmark performance in formal math.
- Provides an explicit modular architecture, making it easier to swap model backbones and extend tool capabilities.
- Includes both benchmark and real collaborative case-study evidence, improving external validity.
- Reports ablations and efficiency metrics (time, budget, code length), not only top-line accuracy.
- Uses open release strategy, which improves reproducibility compared with closed, purely proprietary stacks.

## 7. Limitations and Risks

- The generated Lean scripts can still be verbose and stylistically non-idiomatic, increasing downstream cleanup cost.
- Type-conversion and library-interface edge cases remain brittle failure points even when high-level math is correct.
- Strong benchmark performance does not automatically guarantee maintainable Mathlib-quality code style.
- Hard instances can require disproportionately high budget and runtime, which may limit practical scalability.
- Multi-tool orchestration increases system complexity and can make error attribution harder when failures occur.

## 8. Reproducibility Notes

The authors provide code and formal solutions, but faithful reproduction still requires matching several moving parts: Lean environment versions, MCP tool behavior, retrieval indices, and prompting/runtime policies. To compare fairly with reported results, benchmark replication should preserve the same constraints (sequential execution and no internet during solving) and similar budget regimes. For collaborative case-study reproduction, process-level documentation and human-in-the-loop protocols matter as much as code artifacts.

## 9. Practical Takeaways

A strong practical takeaway is that formal theorem proving can now be approached as an agent-engineering problem, not only as a model-training problem. Investing in robust Lean interaction loops, retrieval quality, and iterative planning can produce large gains without retraining specialized provers. In deployment, teams should expect a tradeoff between solve power and code elegance, and should budget for human review/refactor passes on difficult outputs. The architecture is especially suitable where extensibility and tooling integration are priorities.

## 10. Brief Conclusion

This paper presents Numina-Lean-Agent, a modular formal reasoning system that combines a general coding agent with Lean interaction tools, retrieval, and auxiliary reasoning modules. Under strict Putnam 2025 evaluation constraints, it achieves 12/12 solved and shows through ablations that informal reasoning and subagent decomposition are key contributors to performance. Beyond benchmark tasks, the Brascamp-Lieb case study shows the same architecture can support sustained, research-oriented human-agent formalization at multi-thousand-line scale. Overall, the results suggest that tool-centric agent design is a credible and practical alternative to narrowly specialized theorem-prover training pipelines.
