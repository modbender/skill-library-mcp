---
name: larksync-feishu-local-cache
description: Sync Feishu docs into local cache for OpenClaw-first reading, reducing API calls and token cost. / 把飞书文档同步为本地缓存供 OpenClaw 优先读取，显著降低飞书 API 请求频率与 token 成本。
homepage: https://github.com/gooderno1/LarkSync
metadata: {"category":"integrations","tags":["openclaw","feishu","larksync","sync","local-cache"],"license":"CC-BY-NC-SA-4.0"}
---

# LarkSync Feishu Local Cache Skill

参考：
- `OPENCLAW_AGENT_GUIDE.md`：面向 OpenClaw 代理的自动执行 runbook（首次授权分支、无人值守分支、失败分支）

## English Overview
- Purpose: sync Feishu documents to local markdown/files and let OpenClaw read local cache first.
- Value: fewer Feishu API calls, lower token consumption, and more stable retrieval latency.
- Default mode: `download_only` with low-frequency schedule (daily by default).
- Advanced mode: `bidirectional` and `upload_only` are supported when explicitly requested.

### Typical intents (EN)
- "Set up a daily 01:00 sync from this Feishu folder to local cache."
- "Check my current LarkSync auth and task status first."
- "Switch this task to bidirectional sync and explain the risk."

## 价值主张
- 让 OpenClaw 的高频文档问答“走本地、不走云端接口”。
- 把 API 调用从“每次问答触发”变成“低频定时同步触发”。
- 在不改用户飞书使用习惯的前提下，直接获得更稳、更省的文档检索链路。

## 适用目标
- 目标：减少 OpenClaw 直接调用飞书 API 的频率，优先读取本地 Markdown/附件。
- 默认策略：`download_only` + 每日低频同步（可自定义时间与周期）。
- 进阶策略：支持 `bidirectional`（双向）和 `upload_only`，但仅在用户明确要求时启用。
- Windows 侧建议直接使用 LarkSync 安装包版运行服务，不需要源码构建。

## 触发意图（示例）
- “把飞书生产测试文件夹每天 01:00 同步到本地，给我配置好。”
- “先检查 LarkSync 当前授权和同步任务状态。”
- “我想把这个目录切成双向同步，先评估风险再改。”

## 默认执行流程
1. 检查本地 LarkSync 服务与授权状态。
2. 配置低频下载策略（默认每天一次）。
3. 创建同步任务（默认 `download_only`）。
4. 按需触发一次立即同步，建立本地缓存基线。
5. 后续回答用户文档问题时，优先读取本地同步目录。

## 命令入口
使用以下脚本作为统一入口（返回 JSON，便于自动化编排）：

```bash
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_skill_helper.py check
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_skill_helper.py configure-download --download-value 1 --download-unit days --download-time 01:00
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_skill_helper.py create-task --name "OpenClaw 每日同步" --local-path "D:\\Knowledge\\FeishuMirror" --cloud-folder-token "<TOKEN>" --sync-mode download_only
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_skill_helper.py run-task --task-id "<TASK_ID>"
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_skill_helper.py bootstrap-daily --local-path "D:\\Knowledge\\FeishuMirror" --cloud-folder-token "<TOKEN>" --sync-mode download_only --download-value 1 --download-unit days --download-time 01:00 --run-now
```

WSL 场景（OpenClaw 在 WSL，LarkSync 在 Windows）推荐入口：

```bash
# 先做地址诊断（逐项显示 localhost / host.docker.internal / gateway / resolv nameserver）
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_wsl_helper.py diagnose

# 直接执行原有命令（自动探测可达地址；远程地址自动补 --allow-remote-base-url）
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_wsl_helper.py check
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_wsl_helper.py bootstrap-daily --local-path "/mnt/d/Knowledge/FeishuMirror" --cloud-folder-token "<TOKEN>" --sync-mode download_only --download-value 1 --download-unit days --download-time 01:00 --run-now
```

若全部候选地址不可达，优先确认 Windows 侧：
- LarkSync 已启动；
- 若手动设置过 `LARKSYNC_BACKEND_BIND_HOST=127.0.0.1`，请改回 `0.0.0.0` 或移除该变量；
- 防火墙已放行 WSL 网段到 TCP `8000`。

安全边界：
- 未探测到 Windows 侧可达服务时，脚本会输出诊断信息并停止，不会自动在 WSL 安装依赖或启动后端。
- 请先在 Windows 侧启动 LarkSync（安装包版或开发模式），确认 `:8000` 可达后再重试。
- 注意：飞书 OAuth 首次授权仍需用户完成；授权完成后可进入日常低频同步运行。

默认安全策略：
- `base-url` 仅允许 `localhost/127.0.0.1/::1`，避免把云目录 token 发送到未知远端地址。
- 只有在明确可信内网场景，才允许开启远程地址：

```bash
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_skill_helper.py --base-url "https://larksync.internal.example" --allow-remote-base-url check
```

## 约束与安全边界
- 未通过 `check` 之前，不执行任务创建或策略变更。
- 未经用户明确同意，不把 `download_only` 自动切到 `bidirectional`。
- 若用户要开启双向，必须先告知风险：
  - 本地误改可能上云；
  - 首次建任务可能触发下行/上行扫描；
  - 建议先在测试目录验证。

## 失败处理
- 若接口返回 401/403：提示重新授权飞书并检查“用户身份权限”。
- 若创建任务冲突（409）：自动复用同路径+同云目录的现有任务并回显任务 ID。
- 若后端不可达：优先提示启动 LarkSync 安装包版托盘程序（开发者再使用 `npm run dev`）。

## 输出规范
- 对用户：简明中文结论 + 下一步操作。
- 对系统：保留 helper 脚本 JSON 原始输出，便于追踪与审计。
