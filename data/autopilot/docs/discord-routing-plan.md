# Discord → Autopilot 任务路由

## 目标
在 Discord 项目频道发的代码任务，自动路由到对应 tmux Codex 会话执行。

## 架构

```
用户在 Discord #replyher 说 "修复 SSE 超时问题"
         │
         ▼
   OpenClaw (小秘) 判断: 这是代码任务
         │
         ▼
   task-queue.sh add replyher_android-2 "修复 SSE 超时问题"
         │
         ▼
   watchdog.sh handle_idle() 检测到 idle + 队列有任务
         │
         ▼
   tmux send-keys → Codex CLI 开始工作
         │
         ▼
   Codex 完成 → watchdog 检测到新 commit
         │
         ▼
   discord-notify.sh replyher "✅ 任务完成: 修复 SSE 超时问题 (commit abc1234)"
```

## 需要改动的组件

### 1. 频道↔项目映射配置 (新增)
**文件**: `config.yaml` 新增 `discord_channels:` 段

```yaml
discord_channels:
  shike:
    channel_id: "1473294169203150941"
    tmux_window: "Shike"
    project_dir: "/Users/wes/Shike"
  replyher:
    channel_id: "1473294176128077888"
    tmux_window: "replyher_android-2"
    project_dir: "/Users/wes/replyher_android-2"
  simcity:
    channel_id: "1473294182905938013"
    tmux_window: "agent-simcity"
    project_dir: "/Users/wes/projects/agent-simcity"
  autopilot:
    channel_id: "1473294190094848133"
    tmux_window: "autopilot-dev"
    project_dir: "/Users/wes/.autopilot"
  wpk:
    channel_id: "1477291487170400429"
    tmux_window: "kpw-bot-js"
    project_dir: "/Users/wes/clawd/kpw-bot-js"
```

### 2. discord-notify.sh 改进
- 从 config.yaml 读取频道映射（替代硬编码 case 语句）
- 新增反向查找: `discord-notify.sh --by-window <window_name>` 自动找到对应频道
- 保留 case 语句作为 fallback

### 3. watchdog.sh 任务完成通知
在以下位置增加 Discord 通知:

**a) 队列任务完成时** (`handle_idle` 检测到 commit 后):
```bash
# 现有: send_telegram "$done_msg"
# 新增: 
discord_channel=$(get_discord_channel_for_window "$window")
if [ -n "$discord_channel" ]; then
    "${SCRIPT_DIR}/discord-notify.sh" "$discord_channel" "✅ ${done_msg}"
fi
```

**b) Review 完成时** (Layer 2 review consumer):
```bash
discord_channel=$(get_discord_channel_for_window "$window")
if [ -n "$discord_channel" ]; then
    "${SCRIPT_DIR}/discord-notify.sh" "$discord_channel" "🔍 Review: ${review_result}"
fi
```

### 4. task-queue.sh 增强
- `task-queue.sh add` 新增可选参数 `--source discord:<channel_id>:<message_id>`
  跟踪任务来源，完成时可以 reply 到原消息
- `task-queue.sh done` 输出包含 source 信息，方便 watchdog 回推

### 5. autopilot-lib.sh 新增辅助函数
```bash
# 从 config.yaml 获取 window→discord_channel 映射
get_discord_channel_for_window() {
    local window="$1"
    # 读 config.yaml discord_channels，找 tmux_window 匹配的条目，返回频道名
}

# 从 config.yaml 获取 channel_name→tmux_window 映射
get_tmux_window_for_channel() {
    local channel_name="$1"
    # 读 config.yaml discord_channels
}
```

## 实现顺序

1. **config.yaml 映射** — 加 `discord_channels` 段 (5 min)
2. **autopilot-lib.sh 辅助函数** — `get_discord_channel_for_window` + `get_tmux_window_for_channel` (15 min)
3. **discord-notify.sh 改造** — 读 config.yaml，支持 `--by-window` (15 min)
4. **watchdog.sh 完成通知** — commit 完成/review 完成时推 Discord (15 min)
5. **task-queue.sh source 追踪** — `--source` 参数 (10 min)

总工作量: ~1 小时

## 不需要改的

- **OpenClaw 侧的路由判断**: 这是我（小秘）的行为逻辑，不在 Autopilot 代码里。我在收到 Discord 消息时自行判断是否调用 `task-queue.sh add`。
- **watchdog 主循环**: 已有队列消费逻辑，无需改动。
- **tmux-send.sh**: 已有完整的 send-keys 逻辑。

## 测试计划

1. 手动 `task-queue.sh add Shike "test task"` → 验证 watchdog 消费 → 验证 Discord 通知
2. 在 #shike 频道发代码任务 → 验证全链路
3. 多任务排队测试
4. Codex 正在 working 时加任务 → 验证排队等待
