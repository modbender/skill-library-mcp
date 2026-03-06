# OpenClaw Agent 使用说明（安全收敛版）

本文档面向 OpenClaw 代理本身，不是给人工点点点的教程。  
目标：让代理在拉取仓库后，按安全边界完成 LarkSync 同步任务配置与执行。

## 1. 适用场景
- OpenClaw 在 WSL 运行（最常见）。
- OpenClaw 在 macOS/Linux 运行。
- OpenClaw 在 Windows 运行。

统一原则：优先调用 skill helper，不直接拼 API 请求。

## 2. 必须使用的命令入口
- 通用 helper：`scripts/larksync_skill_helper.py`
- WSL 专用 helper：`scripts/larksync_wsl_helper.py`

路径（相对仓库根目录）：

```text
integrations/openclaw/skills/larksync_feishu_local_cache/scripts/
```

## 3. 默认执行策略（Agent SOP）
1. 先执行健康检查（不要跳过）：

```bash
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_wsl_helper.py check
```

2. 若返回 JSON 中 `auth.connected=false`：
- 停止自动配置。
- 明确提示用户“需完成一次飞书 OAuth 授权”。
- 授权完成后重试步骤 1。

3. 若检查通过，执行一键初始化（推荐）：

```bash
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_wsl_helper.py bootstrap-daily \
  --local-path "/mnt/d/Knowledge/FeishuMirror" \
  --cloud-folder-token "<TOKEN>" \
  --sync-mode download_only \
  --download-value 1 \
  --download-unit days \
  --download-time 01:00 \
  --run-now
```

4. 首次成功后，后续按需执行：
- `check`：巡检状态
- `run-task --task-id <id>`：立即触发
- `configure-download`：调整周期

## 4. WSL 安全边界（关键）
`larksync_wsl_helper.py` 的职责仅限于：
- 诊断 `localhost` / `host.docker.internal` / gateway / nameserver 的可达性。
- 自动补入探测到的 `--base-url`。
- 对非回环地址自动补 `--allow-remote-base-url`。

明确限制：
- 探测不到 Windows 侧 `:8000` 时，直接返回诊断结果并停止。
- 不自动执行 `pip install`。
- 不自动在 WSL 拉起本地后端。
- 需要用户或外层流程先确保 Windows 侧 LarkSync 已启动。

## 5. 首次授权边界（必须告知用户）
- 飞书 OAuth 首次授权必须用户确认，这是平台限制，不是代理故障。
- 完成首次授权后，可以进入长期无人值守运行。

## 6. 错误处理规范
- `HTTP 401/403`：提示重新授权并检查飞书应用权限（用户身份权限）。
- `HTTP 409`（任务冲突）：优先复用已有任务，不重复创建。
- 网络不可达：先跑 `diagnose`，再提示启动 Windows 侧 LarkSync 后重试。

## 7. 给用户的最小反馈模板
- 成功：
  - “已完成低频同步任务配置，任务 ID: <id>，模式: download_only，每天 <HH:MM> 执行。”
- 需人工介入（首次 OAuth）：
  - “当前未完成飞书授权，请先完成一次 OAuth 授权；完成后我会自动继续配置任务。”
- 失败：
  - “已完成自动诊断，当前失败点：<具体错误>；建议动作：<单条可执行建议>。”
