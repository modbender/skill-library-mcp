---
name: safespace-rater
description: Use when users need to audit local OpenClaw skills, generate trust scores, and optionally publish those scores to SafeSpace.
license: MIT
compatibility:
  openclaw: ">=0.0.0"
  runtime: "cli"
---

# SafeSpace Rater（技能安全评分助手）

> EN: Audit local skills, score their security, and optionally publish reputation signals.
>
> 中文：对本地技能做安全审计，生成评分，并可选上传到 SafeSpace 形成公开信誉信号。

---

## 1) What is this? / 这是什么？

**EN**
SafeSpace Rater is a CLI skill for OpenClaw that helps you:
1. Inspect local skills
2. Generate a security/trust score
3. Save concise audit reports
4. Optionally submit ratings to the SafeSpace network

**中文**
SafeSpace Rater 是一个 OpenClaw CLI 技能，帮你：
1. 审查本地 skills
2. 生成安全/信誉分
3. 输出简洁审计报告
4. 可选上传评分到 SafeSpace 公共网络

---

## 2) Why it matters / 有什么价值？

**EN**
Before installing or using a skill, teams often ask: “Is this skill safe enough?”
This skill turns that from subjective feeling into a repeatable process:
- measurable score
- explainable evidence
- shareable reputation

**中文**
团队在安装 skill 前常会问：“这个 skill 靠谱吗？”
这个技能把“主观判断”变成“可复用流程”：
- 有量化分数
- 有证据可追溯
- 有社区信誉可参考

---

## 3) When to use / 何时使用

**EN**
Use this skill when you need to:
- Audit local skills for security risk
- Rate many skills in batch
- Submit skill reputation scores to SafeSpace
- Retry failed uploads from a pending queue
- Merge runtime LLM score + CLI rule score into one final score

**中文**
适用于以下场景：
- 想给本地 skills 做安全审查
- 想批量评分并控制提交节奏
- 想把评分上传到 SafeSpace
- 想重试历史失败上传
- 想把 runtime 模型分 + CLI 规则分融合为最终分

---

## 4) When NOT to use / 不适用场景

**EN**
Do NOT use for:
- Casual chat without audit/score goals
- Tasks unrelated to skill security or reputation
- Server protocol changes (this skill does not modify server API)

**中文**
以下情况不建议使用：
- 只是闲聊，没有审计/评分目标
- 与 skill 安全和信誉无关的任务
- 要改服务端评分协议（本技能不做）

---

## 5) Quick Start (3 steps) / 快速上手（3 步）

### Step 0: Check dependencies / 先检查依赖

```bash
${SKILL_DIR:-.}/scripts/safespace-rater.sh --check
```

> EN: If binary is missing, the wrapper can auto-bootstrap via `go install` (no manual path setup needed).
>
> 中文：若本机缺少二进制，脚本会自动尝试 `go install` 引导安装（无需手动指定路径）。

### Step 1: Register identity once / 注册一次本地身份

```bash
${SKILL_DIR:-.}/scripts/safespace-rater.sh register --agent-id <your-agent-id>
```

### Step 2A: Local audit only (no upload) / 仅本地审计（不上传）

```bash
${SKILL_DIR:-.}/scripts/safespace-rater.sh audit-local \
  --skills-dir ~/.agents/skills \
  --auto \
  --dry-run
```

### Step 2B: Audit + publish / 审计并上传

```bash
${SKILL_DIR:-.}/scripts/safespace-rater.sh audit-local \
  --skills-dir ~/.agents/skills \
  --auto \
  --sample-rate 5 \
  --max-report-runes 500 \
  --max-submit 5
```

---

## 6) Common commands / 常用命令

### A. Single rating / 单个技能评分

```bash
${SKILL_DIR:-.}/scripts/safespace-rater.sh rate \
  --skill-id openclaw/weather@1.0.0 \
  --score 90 \
  --comment "reliable"
```

### B. Discover local skills / 发现本地技能

```bash
${SKILL_DIR:-.}/scripts/safespace-rater.sh discover \
  --skills-dir ~/.agents/skills \
  --auto \
  --source openclaw \
  --version local
```

### C. Batch rating / 批量评分

```bash
${SKILL_DIR:-.}/scripts/safespace-rater.sh rate-local \
  --score 85 \
  --skills-dir ~/.agents/skills \
  --auto
```

### D. Use runtime LLM score file / 使用 runtime 模型分文件

```bash
${SKILL_DIR:-.}/scripts/safespace-rater.sh audit-local \
  --skills-dir ~/.agents/skills \
  --auto \
  --llm-score-file ./runtime-llm-scores.json \
  --sample-rate 5 \
  --max-report-runes 500 \
  --max-submit 5
```

### E. Retry failed uploads / 重试失败上传

```bash
${SKILL_DIR:-.}/scripts/safespace-rater.sh retry-pending --max-submit 20
```

### F. Query result / 查询结果

```bash
${SKILL_DIR:-.}/scripts/safespace-rater.sh summary --skill-id openclaw/weather@1.0.0
${SKILL_DIR:-.}/scripts/safespace-rater.sh top --limit 10 --min-count 1
```

---

## 7) Inputs / 输入参数（简明）

- `skills-dir`：skill 目录（默认 `~/.agents/skills`）
- `identity`：本地 DID 身份文件
- `server`：SafeSpace API 地址
- `llm-score-file`（推荐，可选）：runtime/tool 侧输出的 LLM 分数 JSON
- `sample-rate` / `max-submit` / `max-report-runes`：审计和上传节奏控制

---

## 8) Outputs / 输出结果（简明）

- 提交统计：成功/失败/跳过数量
- 审计摘要：`audit:v2`（包含 source/rule/llm/final/model）
- 本地报告：`~/.safespace/audit-reports/*.md`
- 待重试队列：`~/.safespace/pending-uploads.json`

---

## 9) Scoring behavior / 评分融合逻辑

**EN**
`audit-local` computes client-side hybrid score:
- `final = 0.7 * rule + 0.3 * llm`
- If LLM score is unavailable, it falls back to rule score

**中文**
`audit-local` 客户端融合分：
- `final = 0.7 * rule + 0.3 * llm`
- 若 LLM 分不可用，会自动降级为 rule 分

---

## 10) Recommended environment / 推荐环境变量

```bash
# Optional server override / 可选服务地址覆盖
export SAFESPACE_SERVER=https://skillvet.cc.cd

# Preferred runtime score file / 推荐 runtime 分数文件
export SAFESPACE_LLM_SCORE_FILE=./runtime-llm-scores.json
```

OpenAI-compatible fallback is **optional** and disabled by default:

```bash
export SAFESPACE_LLM_OPENAI_FALLBACK=1
export SAFESPACE_LLM_MODEL=<model>
export SAFESPACE_LLM_API_KEY=<key>
# optional / 可选
export SAFESPACE_LLM_BASE_URL=https://api.openai.com/v1
export SAFESPACE_LLM_TIMEOUT_MS=12000
```

---

## 11) Discovery trigger phrases / 触发短语

- "audit local skills"
- "rate local skills for security"
- "submit skill reputation score"
- "retry pending skill ratings"
- "给本地技能做安全审计并上传评分"
- "批量生成技能信誉分"

---

## 12) Notes / 注意事项

- `skill_id` format: `source/name@version`
- Same DID + same skill within 10 minutes may return `429`
- `rate-local` default max submit is 5 per run (rate-limit friendly)
- Reports/comments are capped and deduplicated via local hash cache
