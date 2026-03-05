---
name: sec-daily-digest
description: "Fetches latest articles from CyberSecurityRSS OPML feeds, applies AI/rule-based scoring, merges CVE and major vulnerability events, and generates a bilingual daily digest for cybersecurity researchers. Trigger command: /sec-digest."
---

# Sec Daily Digest

从 CyberSecurityRSS 的 OPML 链接抓取最新文章，结合 AI 多维评分与规则回退，生成面向网络空间安全研究员的每日精选日报。

## 命令

### `/sec-digest`

启动 sec-daily-digest 流水线。

## 目录与脚本

- 主脚本：`scripts/sec-digest.ts`
- 主编排：`src/pipeline/run.ts`

## 配置与状态（YAML）

配置根目录固定为：

- `~/.sec-daily-digest/`

关键文件：

- `~/.sec-daily-digest/config.yaml`
- `~/.sec-daily-digest/opml/tiny.opml`
- `~/.sec-daily-digest/opml/CyberSecurityRSS.opml`

默认配置示例：

```yaml
provider: openai
opml_profile: tiny
time_range_hours: 48
top_n: 20
output_language: bilingual_zh_en
weights:
  security: 0.5
  ai: 0.5
```

## 关键行为约束

1. 每次运行前检查 OPML 更新
- 默认检查 `tiny.opml`
- 可配置切换 `CyberSecurityRSS.opml`
- 更新检查失败时继续执行，并使用本地缓存 OPML

2. Provider 选择策略
- `--provider openai|gemini|claude|ollama`
- 显式参数优先
- 未指定时默认 `openai`

3. 目标受众和排序
- 面向网络空间安全研究员
- 排序主策略：安全 50% + AI 50%

4. 漏洞合并策略
- 优先按 CVE-ID 合并
- 无 CVE 的重大漏洞按标题+摘要语义聚类合并
- 合并事件下罗列全部参考链接

## 运行参数

```bash
bun scripts/sec-digest.ts \
  --provider openai \
  --opml tiny \
  --hours 48 \
  --top-n 20 \
  --output ./output/sec-digest-$(date +%Y%m%d).md
```

可选参数：

- `--provider <openai|gemini|claude|ollama>`
- `--opml <tiny|full>`
- `--hours <n>`
- `--top-n <n>`
- `--output <path>`
- `--dry-run`

## 环境变量

OpenAI 格式（默认）：

- `OPENAI_API_KEY`（必填，若启用 openai）
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

## 成功输出

终端应显示：

- provider
- 是否使用 OPML 缓存回退
- 输出文件路径
- 统计信息（feeds/articles/recent/selected/vuln_events）

日报内容应包含：

- `AI发展`
- `安全动态`
- `漏洞专报`
