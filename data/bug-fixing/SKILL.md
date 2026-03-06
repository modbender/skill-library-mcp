---
name: bug-fixing
description: |
  Zero-regression bug fix workflow with self-evolution: reproduce → root cause → scope →
  impact prediction → fix → regression verify → code review → self-reflect & evolve.

  Use when:
  - Feature broken, incorrect behavior, wrong output, errors/exceptions
  - Console errors/warnings even when "working"
  - Regressions, timeouts, degraded performance
  - "fix bug", "debug", "not working", "error", "broken"

  Output: Bug summary + verification report + code review + self-reflection score.
  Not for: new features (fullstack-developer); pure review (code-review); optimization (performance-optimization)
allowed-tools: [read, write, execute, grep, glob]
metadata:
  display_name_zh: Bug修复专家
  language: en
  last_updated: 2026-02-13
  version: 2.1.0
  enhancement:
    - 新增 Impact Chain Analysis (影响链分析 A→B→C)
    - 新增 Similar Issue Scanning (相似问题扫描)
    - 新增 Comprehensive Regression Testing (全面回归测试)
    - 新增 Rule 13-16 铁律
    - 强化验证门禁 - 改完不是终点，验证通过才是
---

# Bug Fix (Zero-Regression + Self-Evolution)

**Core Promise**: Fix completely. Fix everywhere. Break nothing. **Learn from every fix.**

---

## 🚨 Iron Rules (NEVER Violate)

```
┌─────────────────────────────────────────────────────────────────────┐
│  🔴 Rule 0:  After RCA, MUST check bug-guide.md for fix patterns  │
│  🔴 Rule 1:  Before fix, MUST search bug-records.md (history)     │
│  🔴 Rule 2:  Root cause MUST pass 4 gates before fixing           │
│  🔴 Rule 3:  Scope MUST pass 4 gates before fixing                │
│  🔴 Rule 4:  Before coding, MUST predict side effects (Blueprint) │
│  🔴 Rule 5:  Before coding, MUST check AI Blind Spot Registry     │
│  🔴 Rule 6:  After fix, MUST run regression verification          │
│  🔴 Rule 7:  Before done, MUST output Bug Summary                   │
│  🔴 Rule 8:  Before done, MUST run code-review                    │
│  🔴 Rule 9:  Before done, MUST update bug-records.md              │
│  🔴 Rule 10: Before done, MUST update bug-guide.md (if new)       │
│  🔴 Rule 11: Before done, MUST complete Self-Reflection           │
│  🔴 Rule 12: Framework behavior → read source code first          │
│  🔴 Rule 13: 🔴 MUST trace IMPACT CHAIN (A→B→C) before fixing   │
│  🔴 Rule 14: 🔴 MUST scan SIMILAR ISSUES in ALL files            │
│  🔴 Rule 15: 🔴 MUST test ALL IMPACTED functions after fix       │
│  🔴 Rule 16: 🔴 Fix is NOT done until VERIFICATION passes        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Workflow Overview

```
Phase 0: Triage → Phase 1: Reproduce → Phase 2: Root Cause Analysis
    ↓
Phase 2.5: 🔴 Check bug-guide.md → Phase 2.6: Search bug-records.md
    ↓
Phase 3: Scope Discovery → Phase 3.5: 🔴 Impact Prediction
    ↓
Phase 4: Fix → Phase 5: 🔴 Regression Verify → Code Review
    ↓
Phase 6: Knowledge Deposit → Phase 6.5: 🔴 Self-Reflection
```

| Phase | Core Action | Gate | Guide |
|-------|-----------|------|---------|
| 0 Triage | Classify (fault/noise) | - | `references/rca-guide.md` |
| 1 Reproduce | Repro steps + evidence | Must have evidence | `references/output-templates.md` |
| 2 RCA | Hypothesis ladder → 5 Whys → evidence | **Root Cause Gate** | `references/rca-guide.md` |
| 2.5 🔴 Patterns | Search bug-guide.md | Must output result | `references/bug-guide.md` |
| 2.6 History | Search bug-records.md | Must output result | `references/bug-records-lookup-protocol.md` |
| 3 Scope | Consumer list → contracts → invariants | **Scope Gate** | `references/scope-accuracy-protocol.md` |
| 3.5 🔴 **Predict** | **Side effect prediction + blind spots** | **Impact Gate** | `references/pre-fix-impact-prediction.md` |
| 4 Fix | Minimal change + regression matrix | ≤50 LOC | `references/output-templates.md` |
| 5 🔴 **Verify** | **Regression test + review** | **Zero new failures** | `references/review-loop.md` |
| 6 Knowledge | 🔴 Update records + guide | Must dual-update | `references/knowledge-extraction-guide.md` |
| 6.5 🔴 **Reflect** | **Self-score + blind spots + evolve** | **Must reflect** | `references/self-reflection-protocol.md` |

---

## 🔴 Root Cause Gate

> **⛔ Root cause is only "confirmed" when ALL 4 conditions are met.**

| Gate | Meaning |
|------|---------|
| **Reproducible** | Can reproduce symptom in controlled scenario |
| **Causal** | Minimal change makes bug disappear |
| **Reversible** | Reverting the change makes bug reappear |
| **Mechanistic** | Can point to exact code path / state transition |

**If any condition fails, keep iterating the hypothesis ladder.**

→ Hypothesis templates + evidence bundle: `references/rca-guide.md`
→ System-level: `references/system-rca-track.md`

### 🔴 Framework Assumption Audit (Rule 12)

When fix involves third-party framework/library behavior:
1. List all framework behavior assumptions
2. Read source code in venv/node_modules to verify
3. Document verified semantics in code comments

→ Detail: `references/framework-assumption-audit.md`

---

## 🔴 Phase 2.7: 🔴 IMPACT CHAIN ANALYSIS (NEW - Rule 13)

> **⛔ 必须完成！影响链要层层递进，不能只看到直接影响的文件**

### 影响链追踪 (A → B → C 链条)

```
发现 Bug 文件 A
    ↓
直接影响: 调用 A 的文件 B (L1)
    ↓
间接影响: 调用 B 的文件 C (L2)
    ↓
间接影响: 调用 C 的文件 D (L3)
    ↓
... 继续追踪直到用户层
```

### 输出模板

```markdown
## 🔴 Impact Chain Analysis

### L0: 原始 Bug 文件
- 文件: [path]
- 问题: [描述]

### L1: 直接影响 (调用 L0 的文件)
| 文件 | 函数 | 影响描述 | 需要修改? |
|------|------|---------|-----------|

### L2: 间接影响 (调用 L1 的文件)
| 文件 | 函数 | 影响描述 | 需要修改? |
|------|------|---------|-----------|

### L3: 深层影响 (调用 L2 的文件)
| 文件 | 函数 | 影响描述 | 需要修改? |
|------|------|---------|-----------|

### 🔴 修复决策
- L1 修改: [是/否] → 原因: [..]
- L2 修改: [是/否] → 原因: [..]
- L3 修改: [是/否] → 原因: [..]
```

---

## 🔴 Phase 2.8: 🔴 SIMILAR ISSUE SCANNING (NEW - Rule 14)

> **⛔ 必须完成！不能只修复当前文件，要检查所有文件是否有相同问题**

### 扫描模式

| 问题类型 | 扫描关键词 | 扫描范围 |
|----------|-----------|----------|
| 缺少 import | `import`, `require`, `from` | 所有同类型文件 |
| 空指针风险 | `null`, `undefined`, `None` | 相关模块 |
| 资源泄漏 | `open()`, `connect()`, `new` | 同类资源 |
| 硬编码 | `hardcode`, `API_KEY`, `password` | 全项目 |
| 类型错误 | `any`, `as`, `cast` | 同模块 |

### 输出模板

```markdown
## 🔴 Similar Issue Scan Results

### 扫描类型: [import缺失/空指针/...]
### 关键词: [关键词列表]
### 扫描范围: [范围]

### 发现相似问题
| 文件 | 行号 | 问题描述 | 严重程度 |
|------|------|---------|---------|

### 🔴 决策
- 一起修复: [是/否]
- 原因: [..]
- 影响文件数: [N]
```

---

## 🔴 Scope Gate

> **⛔ Scope is only "accurate" when ALL 4 conditions are met.**

| Gate | Meaning |
|------|---------|
| **Consumer List** | All consumers (callers/dependents) listed |
| **Contract List** | Modified contracts/interfaces/behaviors listed |
| **Invariant Check** | Must-hold invariants listed |
| **Call Site Enum** | All call sites enumerated and classified |

→ Protocol: `references/scope-accuracy-protocol.md`
→ Caller impact: `references/caller-impact-protocol.md`
→ Cross-surface: `references/cross-surface-regression.md`

---

## 🔴 Phase 3.5: Impact Prediction (Rule 4 & 5)

> **⛔ MUST complete BEFORE writing ANY fix code.**

1. **Change Blueprint** — Document exactly what you plan to change
2. **Impact Ripple Analysis** — Trace ripple from L0 (code) to L4 (user-facing)
3. **Side Effect Prediction** — List what COULD go wrong + edge cases
4. **🔴 Blind Spot Check** — Review `references/ai-blind-spots.md` active list
5. **Go/No-Go Decision** — Confirm safe to proceed

For simple bugs (≤5 LOC, 1 file): use the Quick Impact Check.

→ Full protocol: `references/pre-fix-impact-prediction.md`

**If Go/No-Go fails → adjust approach, do NOT proceed.**

---

## 🔴 Phase 5: Regression Verify + Code Review

```
Fix → 🔴 Regression Verify → Bug Summary → Code Review → P0/P1/P2?
                                                              ↓
                                                   Yes → Fix → Regression Autopsy
                                                   No  → Phase 6
```

### Phase 5.1: 🔴 COMPREHENSIVE REGRESSION VERIFICATION (MANDATORY - Rule 15)

> **⛔ 修复后必须测试影响范围内的所有功能，不能只测试当前 bug！**

#### 测试矩阵 (基于 Impact Chain)

```
影响链层级 → 必须测试的内容
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
L0 (原始文件)    → 原始 bug 修复验证
L1 (直接影响)   → L1 所有函数/接口
L2 (间接影响)    → L2 所有函数/接口
L3 (深层影响)    → L3 关键函数/接口
```

#### 必须执行的测试类型

| 测试类型 | 执行条件 | 工具 |
|----------|----------|------|
| **单元测试** | 影响范围内的函数有单元测试 | pytest, jest |
| **集成测试** | 有集成测试用例 | 测试框架 |
| **API 测试** | 影响 API 接口 | curl, postman, httpx |
| **E2E 测试** | 有 UI 变更 | playwright |
| **手动测试** | 无自动化覆盖 | 手动验证 |

#### 输出模板

```markdown
## 🔴 Regression Test Report

### 测试范围 (基于 Impact Chain)
- L0 测试: [文件] - [测试项]
- L1 测试: [文件列表] - [测试项]
- L2 测试: [文件列表] - [测试项]
- L3 测试: [文件列表] - [测试项]

### 测试执行结果
| 测试类型 | 测试项 | 结果 | 证据 |
|----------|-------|------|------|
| 单元 | test_xxx | PASS/FAIL | [output] |
| 集成 | test_xxx | PASS/FAIL | [output] |
| API | POST /api/xxx | PASS/FAIL | [response] |

### 🔴 决策
- 全部通过: [是/否]
- 失败测试: [列表]
- 处理方式: [修复/跳过/接受]
```

**⛔ If ANY verification fails → return to fix, do NOT proceed.**

### Phase 5.2: Bug Summary + Code Review

Only after regression verification passes:
1. Output Bug Summary (standard format)
2. Run `code-review`
3. If review finds bugs → fix → **Regression Autopsy** → loop back

**Stop condition**: Code review clean + regression verification all ✅ + original bug fixed.

→ Loop rules: `references/review-loop.md`
→ Verification matrix: `references/verification-gates.md`
→ Zero-regression: `references/zero-regression-matrix.md`

---

## API Bug Special Check

For CRUD API bugs:
1. Trace full data flow: Frontend → API → Schema → Service → Database
2. Check Update/Create Schema field completeness
3. Compare request params vs response output consistency

→ Detail: `references/backend-common-issues.md`

---

## System-Level Bug Special Check

For cross-layer/cross-process bugs:
1. Draw end-to-end chain (all participants)
2. Define "handshake correct" evidence for each edge
3. Insert probes to collect evidence BEFORE modifying behavior

→ Detail: `references/system-rca-track.md`

---

## 🔴 Phase 6: Knowledge Deposit (Dual Update)

### 6.1 Update bug-records.md (Project Record)
- Location: `references/bug-records.md`
- Content: BUG-XXX title/date/severity/root cause/fix/files

### 6.2 Update bug-guide.md (Universal Pattern Library)
- Location: `references/bug-guide.md`
- **When**: New pattern / new fix strategy / new root cause
- **How**: Add row to category table or create new category

→ Full guide: `references/knowledge-extraction-guide.md`

---

## 🔴 Phase 6.5: Self-Reflection & Evolution (Rule 11)

> **⛔ MUST complete BEFORE declaring fix done.**

### Mandatory Output:

```markdown
## 🪞 Self-Reflection

### Fix Quality Score
| Dimension | Score (1-5) | Evidence |
|-----------|------------|----------|
| First-time correctness | [1-5] | [notes] |
| Scope accuracy | [1-5] | [notes] |
| Minimal change | [1-5] | [notes] |
| Side effect prediction | [1-5] | [notes] |
| Root cause depth | [1-5] | [notes] |
| **Total** | [/25] | |

### What Went Wrong
| Issue | What Happened | Why I Missed It | Prevention |
|-------|--------------|-----------------|------------|

### Pattern Recognition
- Similar to previous fix? [Y/N → details]
- Regression introduced? [Y/N → if yes, update blind spots]
- Simpler fix missed? [Y/N → if yes, why]
```

→ Regression Autopsy + Blind Spot Evolution: `references/self-reflection-protocol.md`

---

## Skill Delegation

| Trigger | Delegate To |
|---------|-----------|
| Need new API | `fullstack-developer` |
| UI fix | `frontend-design` |
| Schema change | `database-migrations` |
| 🔴 After fix | `code-review` (mandatory) |

---

## Anti-Patterns (FORBIDDEN)

| ❌ Forbidden | ✅ Correct |
|-------------|-----------|
| Fix without RCA | Hypothesis ladder first |
| Single hypothesis then fix | List 3-5 hypotheses, verify each |
| Root cause without 4 gates | Meet all: reproducible/causal/reversible/mechanistic |
| 🔴 Don't check bug-guide.md | Always check pattern library first |
| Skip consumer list for shared code | Fill consumer list first |
| 🔴 **Code without Impact Prediction** | **Blueprint + ripple analysis first** |
| 🔴 **Skip blind spot check** | **Check ai-blind-spots.md every time** |
| 🔴 **No regression verify before review** | **Verify ALL predicted side effects** |
| Skip code review | Code review is mandatory |
| Don't update bug-records.md | Must update every time |
| 🔴 **Skip self-reflection** | **Must score, analyze, and learn** |
| Trust framework docs blindly | Read source code or run tests (Rule 12) |

---

## 🚨 Final Checklist (Before Declaring Done)

> Full checklist: `references/final-checklist.md`
> User Confirmation: `../skill-expert-skills/references/user-confirmation-protocol.md`

| # | Check | Status |
|---|-------|--------|
| 1 | Root cause passes 4 gates | ☐ |
| 2 | 🔴 Checked bug-guide.md | ☐ |
| 3 | Searched bug-records.md | ☐ |
| 4 | Scope passes 4 gates | ☐ |
| 5 | 🔴 Completed Impact Prediction (Blueprint + Blind Spots) | ☐ |
| 6 | 🔴 **Completed Impact Chain Analysis (A→B→C)** | ☐ |
| 7 | 🔴 **Completed Similar Issue Scan** | ☐ |
| 8 | 🔴 **Fixed ALL Similar Issues Found** | ☐ |
| 9 | 🔴 **Regression verification ALL passed (L0-L3)** | ☐ |
| 10 | Output Bug Summary (standard format) | ☐ |
| 11 | Code review — no P0/P1/P2 | ☐ |
| 12 | Updated `references/bug-records.md` | ☐ |
| 13 | 🔴 Updated `references/bug-guide.md` (if new pattern) | ☐ |
| 14 | 🔴 **Completed Self-Reflection (score + analysis)** | ☐ |
| 15 | 🔴 **User confirmed bug is fixed + no new bugs** | ☐ |

**🔴 VERIFICATION GATE (Rule 16): 改完 bug 不是终点，验证通过才是终点！**
- [ ] 原始 bug 已修复
- [ ] 影响范围内所有测试通过
- [ ] 无新 bug 引入
- [ ] 用户确认

---

## Reference Files (21 files)

### Knowledge Cycle (Check Before / Update After)

| File | Purpose |
|------|---------|
| `references/bug-guide.md` | 🔴 Universal bug pattern library (11 categories) |
| `references/bug-records.md` | 🔴 Project bug history |
| `references/ai-blind-spots.md` | 🔴 AI blind spot registry |

### Core Workflow

| File | Purpose |
|------|---------|
| `references/rca-guide.md` | Root cause analysis (hypothesis ladder, 5 Whys, evidence bundle, code path tracing) |
| `references/output-templates.md` | All output templates (hypothesis/evidence/consumer/summary/bug record) |
| `references/final-checklist.md` | Complete checklist (all gates + all phases) |

### Anti-Regression Protocols

| File | Purpose |
|------|---------|
| `references/scope-accuracy-protocol.md` | Consumer list, contracts, invariants, regression matrix |
| `references/caller-impact-protocol.md` | Caller inventory when modifying shared code |
| `references/cross-surface-regression.md` | Cross-surface invariant checks |
| `references/pre-fix-impact-prediction.md` | Side effect prediction before coding |

### Verification & Review

| File | Purpose |
|------|---------|
| `references/verification-gates.md` | Fix completeness + zero-regression matrix + code review gate |
| `references/review-loop.md` | Fix → verify → summary → code review loop |
| `references/zero-regression-matrix.md` | Complete 34-item regression verification matrix |

### Self-Evolution

| File | Purpose |
|------|---------|
| `references/self-reflection-protocol.md` | Self-reflection, regression autopsy, blind spot evolution |
| `references/knowledge-extraction-guide.md` | Knowledge extraction + lookup protocol + quality standards |
| `references/skill-feedback-loop.md` | When/how to evolve this skill itself |
| `references/bug-records-lookup-protocol.md` | Post-RCA bug records search protocol |

### Domain-Specific

| File | Purpose |
|------|---------|
| `references/backend-common-issues.md` | Backend issues (API, ORM, timeout, LLM integration) |
| `references/frontend-common-issues.md` | Frontend issues (React hooks, race conditions, CORS) |
| `references/system-rca-track.md` | System-level RCA (cross-layer, multi-process bugs) |
| `references/framework-assumption-audit.md` | Framework behavior verification (Rule 12) |
