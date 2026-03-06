# sec-daily-digest

英文主文档请见 [README.md](README.md)。

`sec-daily-digest` 从 CyberSecurityRSS 的 OPML 源抓取最新文章，进行 AI 优先（失败可回退规则）的评分筛选，聚合漏洞事件，并生成面向网络空间安全研究员的中英混合日报。

## 五步流水线

`RSS 抓取 -> 时间过滤 -> AI 评分+分类 -> AI 摘要+翻译 -> 趋势总结`

## 主要特性

- TypeScript + Bun 运行时
- 每次运行前强制检查 OPML 更新
  - 默认：`tiny.opml`
  - 可选：`CyberSecurityRSS.opml`（`--opml full`）
  - 远端检查失败时：继续执行并使用本地缓存 OPML
- 显式 Provider 选择：
  - `--provider openai|gemini|claude|ollama`
  - 默认 `openai`
- 排序权重：安全 50% + AI 50%
- AI 阶段解耦：
  - 第 3 步评分输出结构化字段（分数 + 分类 + 关键词）
  - 第 4 步摘要输出翻译标题 + 4-6 句摘要 + 推荐理由
  - 第 5 步输出 3-5 句宏观趋势总结
- 漏洞聚合策略：
  - 优先按 `CVE-YYYY-NNNN...` 精确合并
  - 无 CVE 的重大漏洞按语义聚类合并
  - 合并后罗列所有参考链接
- 输出格式：
  - `## 📝 今日趋势`
  - 中文标题 + 中文摘要 + 推荐理由
  - 保留英文原标题链接

## 配置与状态（YAML）

持久化目录：

- `~/.sec-daily-digest/`

关键文件：

- `~/.sec-daily-digest/config.yaml`
- `~/.sec-daily-digest/opml/tiny.opml`
- `~/.sec-daily-digest/opml/CyberSecurityRSS.opml`

## 快速开始（CLI）

```bash
cd /Users/z3r0yu/z3dev/Skills/sec-daily-digest
~/.bun/bin/bun install
~/.bun/bin/bun scripts/sec-digest.ts \
  --provider openai \
  --opml tiny \
  --hours 48 \
  --top-n 20 \
  --output ./output/sec-digest-$(date +%Y%m%d).md
```

## 参数

- `--provider <openai|gemini|claude|ollama>`
- `--opml <tiny|full>`
- `--hours <n>`
- `--top-n <n>`
- `--output <path>`
- `--dry-run`（仅规则评分，不调用外部 AI）

## 环境变量

OpenAI（默认）：

- `OPENAI_API_KEY`
- `OPENAI_API_BASE`（可选）
- `OPENAI_MODEL`（可选）

Gemini：

- `GEMINI_API_KEY`
- `GEMINI_MODEL`（可选）

Claude：

- `ANTHROPIC_API_KEY`
- `CLAUDE_MODEL`（可选）
- `CLAUDE_API_BASE`（可选）

Ollama：

- `OLLAMA_API_BASE`（可选，默认 `http://127.0.0.1:11434`）
- `OLLAMA_MODEL`（可选）

## Skill 安装方式

先设置本地 skill 路径：

```bash
SKILL_SRC="~/z3dev/Skills/sec-daily-digest"
```

### OpenClaw

OpenClaw 支持 `~/.openclaw/skills`（用户级）和 `./skills`（工作区级）。

用户级安装：

```bash
mkdir -p ~/.openclaw/skills
ln -sfn "$SKILL_SRC" ~/.openclaw/skills/sec-daily-digest
```

工作区级安装：

```bash
mkdir -p ./skills
ln -sfn "$SKILL_SRC" ./skills/sec-daily-digest
```

### Claude Code

个人技能安装：

```bash
mkdir -p ~/.claude/skills
ln -sfn "$SKILL_SRC" ~/.claude/skills/sec-daily-digest
```

项目级安装：

```bash
mkdir -p ./.claude/skills
ln -sfn "$SKILL_SRC" ./.claude/skills/sec-daily-digest
```

### Codex

Codex 从 `~/.agents/skills` 加载技能：

```bash
mkdir -p ~/.agents/skills
ln -sfn "$SKILL_SRC" ~/.agents/skills/sec-daily-digest
```

### OpenCode

OpenCode 支持 `~/.config/opencode/skills`（用户级）和 `./.opencode/skills`（项目级）。

用户级安装：

```bash
mkdir -p ~/.config/opencode/skills
ln -sfn "$SKILL_SRC" ~/.config/opencode/skills/sec-daily-digest
```

项目级安装：

```bash
mkdir -p ./.opencode/skills
ln -sfn "$SKILL_SRC" ./.opencode/skills/sec-daily-digest
```

## 作为 Skill 触发

触发命令：

```text
/sec-digest
```

## 测试

```bash
~/.bun/bin/bun test
```
