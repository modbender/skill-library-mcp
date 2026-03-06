# TokFlow OpenClaw Skill

本目录为 TokFlow 的 OpenClaw 技能包，供 AI 在对话中查询 Token 消耗、优化建议与提问方式分析。

## 安装

- **从 GitHub 仓库**：将本目录（或整个 tokflow 仓库中的 `integrations/openclaw-skill`）复制到 OpenClaw/clawd 的 `skills/` 下，命名为 `tokflow`。
- **从 ClawHub**：若已发布到 ClawHub，可使用 `npx clawhub add tokflow` 或 OpenClaw 技能市场一键安装。

## 使用

确保 TokFlow 后端在本地 8001 端口运行，然后在 OpenClaw 对话中询问「token 消耗」「本月费用」「优化建议」「渠道余额」「提问方式」等，AI 会调用 `scripts/tokflow_query.py` 查询并回答。

命令详见 [SKILL.md](./SKILL.md)。

## ClawHub 发布

目录已包含 `_meta.json` 与 `.clawhub/origin.json`，符合 ClawHub 规范。

**发布到 ClawHub 的步骤：**

1. **登录（仅需一次）**  
   ```bash
   npx clawhub login
   ```
   按提示在浏览器中用 GitHub 完成授权。无浏览器环境可用：  
   `npx clawhub login --token <token> --no-browser`

2. **在 tokflow 仓库根目录执行**  
   ```bash
   cd /path/to/tokflow
   npx clawhub publish integrations/openclaw-skill --slug tokflow --name "TokFlow" --version 0.5.0 --changelog "v0.5.0 提问方式监控与优化：提问轮次统计、四规则建议、节省预估、prompt-stats 命令"
   ```

版本号与 changelog 随发版更新即可。
