# LarkSync Feishu Local Cache Skill

把飞书文档“变成本地知识库”的 OpenClaw 集成技能。  
核心目标：让 OpenClaw **优先读本地同步副本**，而不是每次都打飞书 API，从源头降低 token 消耗与限流风险。

## English Overview
An OpenClaw integration that turns Feishu docs into a local knowledge cache.  
Core goal: make OpenClaw read local synced files first instead of calling Feishu API on every query.

- Lower cost: shift frequent Q&A reads from Feishu API to local filesystem.
- Better stability: local cache still works when cloud API is throttled.
- Faster retrieval: local-first access for daily queries.
- Safe by default: `download_only` mode, with optional advanced bidirectional mode.

## 为什么值得安装
- 省额度：把高频问答读取从飞书 API 转到本地文件系统。
- 更稳：飞书偶发限流/网络波动时，本地副本仍可读。
- 更快：日常检索直接命中本地目录，不必每次远程拉取。
- 可扩展：默认低风险 `download_only`，需要时可升级到双向同步。

## 一句话效果（Before / After）
- Before：问一个文档问题 -> 调一次飞书 API -> 累积额度消耗。
- After：每天低频同步一次 -> 多次问答都走本地读取 -> API 用量大幅下降。

## 适合谁
- 已经在飞书沉淀大量文档、同时用 OpenClaw 做日常知识检索的人。
- 想把飞书纳入 NAS/本地知识管理体系的人。
- 关注“可持续调用成本”的个人或团队。

## 默认推荐模式
- 同步模式：`download_only`
- 下载频率：每日 1 次（可配置时间）
- 读取策略：OpenClaw 优先本地目录检索与引用

## 目录结构
```text
integrations/openclaw/skills/larksync_feishu_local_cache/
  SKILL.md
  OPENCLAW_AGENT_GUIDE.md
  README.md
  scripts/
    larksync_skill_helper.py
```

## Agent Runbook
- OpenClaw 代理专用执行说明：[`OPENCLAW_AGENT_GUIDE.md`](./OPENCLAW_AGENT_GUIDE.md)

## 依赖前提
1. Windows 侧已安装并运行 LarkSync（安装包版即可，不需要拉源码构建；后端可访问 `http://localhost:8000`）。
2. 已在 LarkSync 中完成飞书 OAuth 授权。
3. 出于安全考虑，helper 默认只允许连接本机 `localhost/127.0.0.1/::1`。

## 30 秒快速上手
```bash
# 1) 环境检查
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_skill_helper.py check

# 2) 一键配置每日低频同步（推荐）
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_skill_helper.py bootstrap-daily --local-path "D:\\Knowledge\\FeishuMirror" --cloud-folder-token "<TOKEN>" --sync-mode download_only --download-value 1 --download-unit days --download-time 01:00 --run-now
```

完成后，OpenClaw 可优先读取本地镜像目录，减少飞书 API 请求。

## 常用命令
```bash
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_skill_helper.py check
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_skill_helper.py bootstrap-daily --local-path "D:\\Knowledge\\FeishuMirror" --cloud-folder-token "<TOKEN>" --sync-mode download_only --download-value 1 --download-unit days --download-time 01:00 --run-now
```

远程地址（仅可信网络）：
```bash
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_skill_helper.py --base-url "https://larksync.internal.example" --allow-remote-base-url check
```

## WSL 用户（推荐）
当 OpenClaw 跑在 WSL、LarkSync 跑在 Windows 时，优先使用 WSL 包装脚本：

```bash
# 诊断可达地址（会逐项输出 localhost / host.docker.internal / gateway / resolv nameserver）
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_wsl_helper.py diagnose

# 自动探测并执行原命令
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_wsl_helper.py check
python integrations/openclaw/skills/larksync_feishu_local_cache/scripts/larksync_wsl_helper.py bootstrap-daily --local-path "/mnt/d/Knowledge/FeishuMirror" --cloud-folder-token "<TOKEN>" --sync-mode download_only --download-value 1 --download-unit days --download-time 01:00 --run-now
```

说明：
- 若所有候选地址都显示 `UNREACHABLE`，主因通常是 Windows 侧 LarkSync 尚未启动或未监听 8000 端口。
- 如果 Windows 侧不可达，脚本会输出诊断信息并停止，不会在 WSL 自动安装依赖或自动拉起后端。
- 请先在 Windows 侧启动 LarkSync，再重新执行 `check` / `bootstrap-daily`。
- Windows 版 LarkSync 默认允许 WSL 通过宿主机地址访问；若你手动设置过 `LARKSYNC_BACKEND_BIND_HOST=127.0.0.1`，请改为 `0.0.0.0` 或移除后重启，再执行 `diagnose`。
- 手动传远程 `--base-url` 时，脚本会自动补 `--allow-remote-base-url`。
- 飞书 OAuth 首次授权仍需用户确认；完成首次授权后可长期无人值守运行。

## 上架 ClawHub（建议先 dry-run）
```bash
cd integrations/openclaw/skills/larksync_feishu_local_cache
clawhub login
clawhub sync --root . --dry-run
clawhub publish . --slug larksync-feishu-local-cache --name "LarkSync Feishu Local Cache" --version 0.1.6 --changelog "fix(security): remove WSL auto-install and auto-start behaviors"
```

> 具体发布流程请结合 OpenClaw 官方文档与 `docs/OPENCLAW_SKILL.md`。
