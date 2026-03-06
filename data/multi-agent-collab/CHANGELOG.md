# 变更记录

> **维护规则**：只保留最近 2 周。旧记录移到 `archive/CHANGELOG-YYYY-MM.md`

## 格式
```
- [类型] 描述（一句话）- by {model}@{session前6位} #标签
```

**类型**：`✨新增` `🐛修复` `♻️重构` `📝文档` `⚡️性能` `🔧配置` `🗑️清理`

**常用标签**：`#运维` `#开发` `#文档` `#skill开发` `#调试` `#部署` `#设计`

---

## 2026-02-14

### v2.0 Initial Release
- [✨ feat] MACS v2 refactor: model-tiered cowork + document-driven sync - by sonnet #design
- [✨ feat] WEEKLY-REPORT.md template with pattern discovery section - by sonnet #skill
- [🐛 fix] init.sh sed cross-platform compatibility (macOS/Linux) - by sonnet #dev
- [🐛 fix] CHANGELOG template with initial entry placeholder - by sonnet #dev
- [🐛 fix] Remove incorrect `brew install qmd` from BEST-PRACTICES - by sonnet #docs
- [📝 docs] Complete README + SKILL.md + BEST-PRACTICES - by sonnet #docs

### v2.1 Universal & Bilingual
- [♻️ refactor] Platform-agnostic design (works with any multi-agent system) - by sonnet #design
- [📝 docs] Bilingual documentation (English/Chinese) for user-facing files - by sonnet #docs
- [📝 docs] Platform support list (Claude Code/Cursor/OpenAI/LangChain/OpenClaw) - by sonnet #docs
- [♻️ refactor] Templates pure English (agent-facing, token-efficient) - by sonnet #design
