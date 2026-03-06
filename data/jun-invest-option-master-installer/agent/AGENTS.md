# AGENTS.md — jun-invest-option-master

这是 **jun-invest-option-master** 的独立工作区（isolated agent workspace）。

## 核心约定（重要）

### 1) “升级/更新”口令（用户只说一句就执行）

当用户在本 agent 的对话里说以下任意表达：
- “升级 agent”
- “升级投研 agent / 升级投资 agent”
- “更新到最新”
- “安装/升级 jun-invest-option-master”

一律视为同一操作：**升级/同步 jun-invest-option-master（这个投研 agent 的工作区资产）到最新版本**。

⚠️ 重要：这条口令 **不等于** 升级 OpenClaw 程序本体。
- 不要执行 `openclaw update` / `npm update openclaw` / `update.run` 这类“升级 OpenClaw 本体”的动作。
- 只做“installer → workspace 同步”的升级。

执行固定步骤（无需再反问用户“升级哪一种”）：
1. `clawhub update jun-invest-option-master-installer --force`
2. 运行 installer 的 `scripts/install.sh` 同步资产到：
   `/Users/lijunsheng/.openclaw/workspace-jun-invest-option-master`
3. `openclaw agents add jun-invest-option-master --non-interactive --workspace /Users/lijunsheng/.openclaw/workspace-jun-invest-option-master`
   - 已存在则跳过（不要报错打断）
4. 仅当需要让配置/路由生效时才重启 gateway（通常不强制）

升级完成后：
- 回复当前 installer 版本号 + 本次变更摘要
- 然后再询问用户：是否需要绑定 channel/bot（绑定作为下一步单独处理）

### 2) “改功能并发布”默认闭环（模式 B）

用户通过对话提出功能升级时：
- 默认在 `jun-invest-option-master-repo` 修改 → git commit → 发布 `jun-invest-option-master-installer` 新版本（semver）
- 然后自动执行一次上述“升级/同步”让当前运行环境立刻生效

### 3) Secrets
- 任何 token/账号/密钥不得打包进 installer skill
- 仅通过环境变量/本机配置引导用户设置
