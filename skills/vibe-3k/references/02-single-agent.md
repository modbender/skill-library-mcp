# 02 — 单人开发

## PLAN → ACT 分离（最重要的原则）

**像管理新员工一样管理 AI：你不会让新人第一天就自己实现整个功能。**

### PLAN 阶段

- 使用大上下文 thinking 模型（Gemini / OpenAI / Claude 最新旗舰）
- 让 thinking model 深度推理
- 只分析、读代码、提问，**不写代码**
- 输出：Design Doc

```
PLAN 模式 Prompt：

你现在处于 PLAN 模式。
- 只创建详细计划，不实现代码
- 使用 read_file 和 search_files 收集上下文
- 提出澄清问题确保完全理解需求
- 用 Mermaid 图表可视化架构
- 与我讨论直到计划满意
- 满意后建议切换到 ACT 模式
```

### ACT 阶段

- **新开一个 session**（清空上下文，避免污染）
- 读取 Design Doc → 逐步实现
- 使用快速模型（各厂商轻量级模型）
- 不需要 thinking mode — Plan 阶段已做完

---

## Design Doc 模板

```markdown
# [Feature Name] Design Doc

**Date:** YYYY-MM-DD | **Author:** [你/AI] | **Issue:** [Link]

## 1. Overview — 一句话描述
## 2. Motivation — 为什么做
## 3. Proposed Changes — 改什么
## 4. Technical Design — 架构/数据流/算法
## 5. Files to Touch

| 文件 | 操作 | 说明 |
|------|------|------|

## 6. Testing Plan
## 7. Risks & Open Questions
```

---

## 执行日志（LOG.md）

```markdown
# LOG.md

## [Feature Name] — 执行日志

### Step 1: 创建 XX 组件 ✅
- 文件：src/components/XX.tsx
- 验证：页面显示正常

### Step 2: 添加 API 路由 ✅
- 文件：src/app/api/xx/route.ts
- 验证：curl 测试通过

### Step 3: 数据库集成 ⏳
- 状态：进行中
```

**为什么需要 LOG.md**：上下文溢出恢复、换 session 交接、回退定位。

---

## Prompt 技巧

```
✅ 具体 > 模糊
   ❌ "做一个社交 app"
   ✅ "做一个文字社交 feed：280 字帖子 + 关注 + 时间排序"

✅ 小步迭代 > 一步到位
   ❌ "实现完整用户认证 + 权限 + 社交登录"
   ✅ "先实现 email/password 注册登录，bcrypt + JWT"

✅ 粘贴完整错误 > 描述错误

✅ 正面表述 > 负面表述
   ❌ "不要用 class 组件"
   ✅ "使用函数组件 + hooks"

✅ 指定文件范围
   "只修改 src/lib/auth.ts"
```

---

## 上下文管理（防止质量退化）

```
规则 1: 新功能 = 新 session
规则 2: 精确指向文件，不要 "看整个 src/"
规则 3: Design Doc 是上下文压缩器
规则 4: 对话超过 20 轮 → 开新 session → LOG.md 接力
```
