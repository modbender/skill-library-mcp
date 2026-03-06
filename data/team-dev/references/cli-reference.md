# CLI Reference (dev-team)

各 agent 的 CLI 用法摘要。实际命令以 `config/agents.json` 为准，spawn-agent 会据此构建。

## Codex

```bash
codex exec [OPTIONS] "prompt"
  --dangerously-bypass-approvals-and-sandbox
  -C, --cd <DIR>
```

## Claude Code

```bash
claude [OPTIONS] "prompt"
  --dangerously-skip-permissions
  -p, --print
```

## Gemini

```bash
gemini [OPTIONS] "prompt"
  # 推荐使用 config/agents.json 中的 args（含 --approval-mode yolo --allowed-tools ...）
  -p
```

## Cursor

```bash
cursor agent [OPTIONS] "prompt"
  -f, --force
  --workspace <path>
  --model <model>
  --mode <plan|ask>
```

推荐：
- 开发模式（可改代码）：`cursor agent -f -p --workspace <path> --model composer-1.5 "prompt"`
- 规划模式（只读）：`cursor agent -f -p --mode plan --workspace <path> --model gpt-5.3-codex "prompt"`

## tmux（脚本内部使用）

```bash
tmux new-session -d -s <name> -c <dir> "command"
tmux send-keys -t <session> "text" Enter
tmux list-sessions
tmux kill-session -t <session>
```

## 发送消息到运行中的代理

```bash
tmux send-keys -t <session-name> "你的指令" Enter
```

## 停止代理

```bash
tmux kill-session -t <session-name>
# 或使用 scripts/stop-agent.sh --branch <branch>
```
