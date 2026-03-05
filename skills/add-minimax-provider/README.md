# add-minimax-provider

> **GitHub**: https://github.com/jooey/openclaw-skill-add-minimax-provider

为 OpenClaw 配置 MiniMax 大模型的 AgentSkill。

## 功能

一键引导 OpenClaw 接入 MiniMax 模型，支持两种接入方式：

| 方式 | Provider 名 | API 协议 | 适用场景 |
|------|-------------|----------|----------|
| API Key 直连 | `minimax` | openai-completions | 付费用户，按量计费 |
| OAuth 门户 | `minimax-portal` | anthropic-messages | 门户用户，平台侧计费 |

## 支持的模型

- **MiniMax-M2.1** — 主力模型，200K context，综合能力强
- **MiniMax-M2.1-lightning** — 轻量快速版（portal 可用）

## 安装

### 方式一：ClawHub（推荐）

```bash
clawhub install add-minimax-provider
```

> 没有 clawhub？先装：`npm i -g clawhub`

### 方式二：从 GitHub 克隆

```bash
# 克隆到你的 agent workspace 的 skills 目录
git clone https://github.com/jooey/openclaw-skill-add-minimax-provider.git \
  ~/.openclaw/workspace/skills/add-minimax-provider
```

### 方式三：手动下载

```bash
# 下载并解压到 skills 目录
cd ~/.openclaw/workspace/skills
curl -L https://github.com/jooey/openclaw-skill-add-minimax-provider/archive/refs/heads/main.tar.gz | tar xz
mv openclaw-skill-add-minimax-provider-main add-minimax-provider
```

安装后**开启新会话**，Agent 即可识别此 skill。对它说"帮我配 MiniMax"就会自动触发。

## 零起步冷启动

还没有任何可用模型？没关系——用免费的 Qwen Coder 冷启动：

1. 先配好 `qwen-portal` provider（免费，OAuth 登录即可，用openclaw config命令配置）
2. 用 Qwen Coder 作为 primary 模型启动 OpenClaw
3. 在聊天中说："帮我配置 MiniMax 模型"
4. Agent 自动加载本 skill，按步骤完成配置
5. `/model Minimax` 切换到 MiniMax 作为主力

> 这就是 OpenClaw 的"自举"——用免费模型启动系统，再让它帮你配更强的模型。

## Skill 覆盖的流程

1. **测试模型可用性** — curl 验证 API 连通性
2. **添加 Provider** — 写入 `openclaw.json`
3. **配置别名** — `/model Minimax` 快速切换
4. **接入 Fallback 链** — 自动容灾
5. **验证** — JSON 校验 → `openclaw doctor` → 重启 → 功能测试
6. **排障** — 常见问题诊断指南

## 🎁 MiniMax 邀请福利

通过邀请链接注册 MiniMax Coding Plan，享 **9 折优惠 + Builder 权益**：

👉 https://platform.minimaxi.com/subscribe/coding-plan?code=2vNMQFJrZt&source=link

## License

MIT
