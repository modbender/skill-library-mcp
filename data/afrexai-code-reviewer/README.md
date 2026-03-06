# AfrexAI Code Reviewer

Enterprise-grade automated code review for your AI agent. Reviews GitHub PRs, local diffs, or pasted code using the **SPEAR framework** — Security, Performance, Error Handling, Architecture, Reliability.

## Install

```bash
clawhub install afrexai-code-reviewer
```

## What You Get

- **SPEAR scoring system** — 5 dimensions, weighted, 0-100 final score with clear verdicts
- **60+ specific patterns** across TypeScript, Python, Go, Java, and SQL
- **4 severity levels** with point deductions that drive the score
- **Structured output template** — every review is consistent and actionable
- **Security review depth levels** — Quick, Standard, Deep, Threat Model
- **Quick checklist mode** for fast reviews
- **GitHub & local git integration** — works with `gh` CLI or raw diffs
- **Heartbeat/cron ready** — auto-review new PRs on a schedule

## Usage

Just tell your agent:

```
Review PR #42 in my-org/my-repo
```

```
Review the staged changes in this repo
```

```
Do a deep security review of src/auth/
```

## vs Other Review Skills

| Feature | Others | AfrexAI |
|---------|--------|---------|
| Scoring system | ❌ | ✅ SPEAR 0-100 |
| Language patterns | 2-3 | 5+ languages, 60+ patterns |
| Security depth levels | ❌ | ✅ 4 levels |
| Architecture review | ❌ | ✅ coupling, layers, complexity |
| Business logic review | ❌ | ✅ spec matching, edge cases |
| Operability review | ❌ | ✅ rollback, monitoring, flags |
| No dependencies | ❌ (needs scripts) | ✅ pure agent skill |

## ⚡ Level Up

Want code review as part of a complete engineering workflow? Check out our **SaaS Context Pack** — includes code review, incident response, deployment checklists, and more.

👉 [Browse Context Packs ($47)](https://afrexai-cto.github.io/context-packs/)

## 🔗 More Free Skills by AfrexAI

- [afrexai-lead-hunter](https://clawhub.com/skill/afrexai-lead-hunter) — ICP-driven lead generation
- [afrexai-seo-content-engine](https://clawhub.com/skill/afrexai-seo-content-engine) — SEO content creation
- [afrexai-budget-tracker](https://clawhub.com/skill/afrexai-budget-tracker) — Financial tracking & insights
- [afrexai-customer-support](https://clawhub.com/skill/afrexai-customer-support) — Support & retention engine
- [afrexai-meeting-mastery](https://clawhub.com/skill/afrexai-meeting-mastery) — Meeting prep & follow-up

[Browse all AfrexAI skills →](https://afrexai-cto.github.io/context-packs/)
