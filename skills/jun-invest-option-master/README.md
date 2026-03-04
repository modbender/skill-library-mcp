# jun-invest-option-master (OpenClaw Agent App)

`jun-invest-option-master` 是一个**全新的** Agent App Repo，用于重建你原先 `invest-master` 的能力：
- 团队型工作流（PM + Data/Regime/Equity/Options/Portfolio/Risk/Execution/Postmortem）
- 输出标准化“审批包”（不自动下单）
- 配置/规则/模板/提示词可版本化、可迁移

> 目标：重装 OpenClaw 后不需要重新“创建/训练”，直接恢复这套工作区与规则体系。

## 目录结构
- `agent/`：Agent 工作区（config / prompts / templates）
- `docs/`：背景文档（例如原 invest-master 的章程说明）
- `scripts/`：安装/自检脚本
- `skills.lock.json`：外部 skills 清单（装最新即可）
- `clawhub-skill/`：可选的 ClawHub 安装器 skill（薄包装）

## 安装到 OpenClaw workspace

```bash
bash scripts/install.sh --workspace "$HOME/.openclaw/workspace"
bash scripts/doctor.sh  --workspace "$HOME/.openclaw/workspace"
```

默认会安装到 `$WORKSPACE/jun_invest_option_master/`（避免覆盖你现有的 `invest_agent/`）。

## 迁移来源（能力继承说明）

当前 `agent/` 内容直接继承自你现有 `invest_agent/`（prompts/config/templates），并把 `INVESTMENT_AGENT.md` 归档到 `docs/` 作为章程说明来源。

下一步我们会做的“Agent App 化”改造（不改变能力，只是工程化）：
- 明确入口/运行方式（如何在 OpenClaw 中拉起团队子 agents 并落盘 logs）
- 增补 `workflows/` 或 runner 脚本（如果你希望标准化产出目录结构）
- 完善对外发布文档（输入输出契约、示例审批包、FAQ）
