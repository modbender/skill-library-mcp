---
name: peter-code-review
description: 提交前质量闸门。快速完成本地测试、静态检查和风险审查，判断“是否可提交”。
version: 1.5.0
---

# Peter Code Review

## 30 秒简介
用于“提交前最后一关”。

它会基于当前改动，执行最小但有效的验证闭环：
1. 识别改动范围
2. 运行基础检查（lint/type/test）
3. 对 UI、配置、依赖变更做附加检查
4. 输出可提交结论与修复清单

## 适用场景
- 用户提到“提交前检查”“测试一下再 commit”“pre-commit review”
- 准备开 PR 前，希望先清理明显问题

## 使用前提
- 在仓库根目录运行。
- 默认审查“当前工作区改动”；如果工作区为空，则回退审查 `HEAD` 最近一次提交，并在报告中明确标注。

## 执行步骤
### 1) 识别改动范围
```bash
git status -s
git diff --stat
git diff --name-only
```

若 `git status -s` 为空，执行：
```bash
git show --name-only --stat --pretty="" HEAD
```
并在报告中标注“基于 HEAD 审查，非工作区审查”。

### 2) 运行基础质量检查（按技术栈选择）
- Node/TS：
  - 必跑：`npm run lint`、`npx tsc --noEmit`
  - 优先执行非端到端测试（如 `npm run test:unit`、`npm run test:integration`）
  - 若仓库测试入口仅为端到端测试，则跳过测试并记录“未执行原因 + 影响范围”
- Python：`ruff check .`、`pytest`
- Go：`go test ./...`
- Rust：`cargo test`

如果命令不存在或环境缺失，必须明确记录“未执行原因 + 影响范围”。

### 3) 条件触发附加检查
- 构建配置/依赖变更时执行 build。
- 推荐触发模式：
  - `package.json`、`pnpm-lock.yaml`、`yarn.lock`
  - `next.config.*`、`vite.config.*`、`webpack*.js`
  - `prisma/`、`src/app/api/`、CI/构建脚本目录
- 当命中上述触发模式时，按顺序附加执行：
  1. `npm run workflow:check`（若命令存在）
  2. `npm run build`
  3. `npm run gate:db`（若命令存在）
- 若 `workflow:check` / `gate:db` 命令不存在或执行环境缺失，必须记录“未执行原因 + 影响范围”，且不得标记为通过。
- 若 `gate:db` 输出包含 `GATE_DB_UNREACHABLE`（或等价 DB 不可达证据，如 `P1001`）：
  - 标记为 `High` 风险，禁止标记为“通过”
  - 总结论允许为 `可提交（高风险）`
  - 必须附带“PR 阶段需强制复核（建议立刻执行 `peter-ci-gate`）”

### 4) UI 改动验证策略
检测 UI 改动：
```bash
git diff --name-only \
  | grep -E '\.(tsx|jsx|css|scss)$|^src/components/|^src/app/' \
  | grep -Ev '^src/app/api/'
```

- 若存在 UI 改动，优先执行“可运行的最小验证”：`lint`、`typecheck`、相关模块单元/集成测试（非端到端）。
- UI 质量验证以手工冒烟为主，建议至少覆盖：
  - 关键页面可打开且无明显报错
  - 关键交互可触发且无阻塞
  - 关键文案/布局无明显回归
- 结论判定要求：
  - 未完成手工 UI 验证时，不得把 UI 项标记为“通过”；应标记为“未执行（有风险）”。
  - 总结论可给出“可提交（含 UI 未验证风险）”或“需修复后提交”，由改动风险决定。

### 5) 安全与实现质量审查
至少覆盖以下检查点：
- 输入校验与错误处理
- SQL/查询安全、SSRF、XSS 风险
- 敏感信息泄露（token/key/连接串）
- 类型安全、重复代码、性能回归、可维护性

### 6) 需求完成度核对
对照用户需求逐条标注：
- 已完成
- 部分完成
- 未完成
并给出对应文件位置。

## 输出格式（固定）
1. `## 代码审查报告`
2. `### 提交标准检查清单`（lint / typecheck / test / workflow-check(如执行) / gate:db(如执行) / build(如执行) / 安全 / 需求 / UI(通过/未执行)）
3. `### Git 改动摘要`（文件数、关键文件）
4. `### 执行结果`（每条命令是否通过，失败摘录）
5. `### 问题列表`（Critical / High / Medium / Low，含文件:行号、原因、修复建议）
6. `### 结论`（`可提交` / `可提交（高风险）` / `需修复后提交`）

## 护栏
- 默认不直接修改业务代码，只做审查与建议。
- 本技能默认不执行端到端 UI 自动化测试。
- 当 UI 改动且未做手工验证时，必须记录“未执行原因 + 影响范围 + 建议补救”。
- 任何失败命令都要明确记录原因。
- 没有证据时，禁止将对应检查项标记为“通过”。
- `GATE_DB_UNREACHABLE` 只能判定为“高风险（可提交但需复核）”，不得写成“通过”。
