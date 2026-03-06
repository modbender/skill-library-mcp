---
name: rust-rebuilder
description: Plan and execute incremental project rewrites to Rust with architecture mapping, parity verification, idiomatic Rust guidance, dependency preflight checks, and GitHub upstream synchronization. Use when users ask to port or rewrite existing systems into Rust, need latest Rust feature checks, want migration pitfall prevention, or need continuous sync with source repository commits and pull requests.
---

# Rust Rebuilder

## Overview

使用“分阶段、可验证、可回滚”的方式重写项目到 Rust。优先确保行为等价和可观测性，再做性能与架构优化。

## Dependency Preflight (Mandatory)

每次执行前先运行：

```bash
python3 scripts/check_dependencies.py
```

自动检测以下依赖是否可用：

- `grok-search` skill，或 `grok-search` MCP。
- `github-helper` skill。

若任一缺失，必须输出安装引导并暂停当前重写任务。安装引导顺序：

1. 优先使用 `$skill-installer` 安装缺失 skill。
2. 若无可用安装器，则给出手动安装地址：
   - grok-search skill: `https://github.com/Frankieli123/grok-skill`
   - grok-search MCP: `https://github.com/GuDaStudio/GrokSearch`
   - github-helper: 当前用户 GitHub 仓库中的 `github-helper` skill 仓库
3. 明确标记“依赖未满足，重写任务暂停”。

## Workflow

1. 定义范围：确认系统边界、关键路径、性能目标、上线约束。
2. 建立映射：将源项目的模块/接口/数据模型映射到 Rust crate 与模块结构。
3. 制定切片：按垂直功能切分迁移批次，每批必须可编译、可测试、可回归。
4. 执行重写：先保行为一致，再替换为更地道的 Rust 设计；若是后端代码，强制套用 `references/rust-backend-guidelines.md`。
5. 校验对齐：运行编译、测试、基准、回归对比，阻断行为漂移。
6. 跟踪上游：若源项目在 GitHub，持续同步 upstream 变更并更新重写 backlog。

## Backend Rust Guardrails

当目标是后端 Rust 代码（例如 API、作业系统、数据库访问、异步任务）时，必须先读取 `references/rust-backend-guidelines.md`，并在输出中显式说明以下检查点：

- 数据结构是否用 `enum`/newtype 表达状态和不变量；
- SQLx 查询是否显式列名且无 `SELECT *`；
- async 代码是否避免阻塞 runtime；
- 错误处理是否统一 `Result` 语义且无库级 `panic`；
- 可见性是否 `pub(crate)` 优先，模块边界是否收敛。

## Mandatory Output Contract

在每次执行中输出以下内容，避免“只给代码不讲迁移依据”：

- Rewrite Scope：本轮重写的模块、接口和非目标范围。
- Equivalence Strategy：行为对齐方式（黄金测试、对拍、协议回放）。
- Rust Design Decisions：所有权、生命周期、错误模型、并发模型选择。
- Risk Register：已识别陷阱、触发条件、监控指标、回退方案。
- Upstream Sync Notes：与原仓库分叉点、增量 commit、对应重写任务。

## Implementation Rules

- 仅做小步重写：每次变更控制在“可独立验证”的粒度。
- 先复制语义再优化：禁止在同一批次同时做行为变更与性能重构。
- 默认显式失败：不要静默吞错或返回伪成功路径。
- 所有外部边界（IO/网络/序列化）必须保留一致的错误语义。
- 为每个迁移批次写清“完成定义”：编译通过 + 用例通过 + 指标不回退。

## Rust Feature and Idiom Strategy

执行时先读取 `references/rust-language-update-playbook.md`，并遵循：

- 先确认当前稳定版 Rust 发布信息，再决定是否采用新特性。
- 同时给出“最新可用方案”和“保守稳定方案”两条路径。
- 说明从源语言惯用法到 Rust 惯用法的映射，不只给语法替换。

## Pitfall Prevention

执行时读取 `references/rewrite-pitfalls-and-antipatterns.md`，至少检查：

- 所有权误判导致过度 `clone`、无效拷贝和性能退化。
- 错误处理从异常迁移到 `Result` 时的语义丢失。
- 并发迁移时把“共享可变状态”硬搬到 Rust 造成锁竞争。
- FFI/协议边界未保持一致，导致线上兼容性问题。

## GitHub Upstream Synchronization

若源项目来自 GitHub，执行时读取 `references/github-upstream-sync.md` 并优先：

1. 用 `github-helper` skill 管理本地克隆与仓库知识快照。
2. 用 `scripts/upstream_sync_report.py` 生成 upstream 差异报告。
3. 将新增 commits/PR 分类映射为 Rust 重写 backlog（行为修复、接口变更、性能变更）。

## Skill Collaboration

- 获取 Rust 最新特性与生态信息：优先使用 `grok-search`（或 grok-search MCP）。
- GitHub 仓库同步与变更追踪：优先联动 `github-helper`。
- 若用户要求自动生成完整迁移执行文档，可联动 `docx`/`xlsx` 生成结构化交付物。

## Resource Map

- `references/rust-language-update-playbook.md`：Rust 版本与特性确认流程、查询模板。
- `references/rust-backend-guidelines.md`：后端 Rust 编码规范与审查清单。
- `references/rewrite-pitfalls-and-antipatterns.md`：重写误区与排雷清单。
- `references/github-upstream-sync.md`：上游仓库同步、commit/PR 映射流程。
- `scripts/check_dependencies.py`：检测并引导安装必需 skill/MCP。
- `scripts/upstream_sync_report.py`：本地仓库 upstream 差异报告工具。

## Quick Start Prompt Pattern

使用以下模板触发技能：

`使用 $rust-rebuilder，把 <源项目/模块> 分三批重写到 Rust；每批给出等价验证方案、风险点和与 upstream 同步策略。`
