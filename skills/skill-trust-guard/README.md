# Skill Trust Guard

OpenClaw skill 安装安全门：在 `clawhub install` 之前自动调用 `skill-trust-scanner`，按评分决策是否放行。

## 1) 目录结构

```text
~/.openclaw/skills/skill-trust-guard/
├── SKILL.md
├── README.md
├── install.sh               # wrapper（方案 B）
├── integrate.sh             # 生成 clawhub shim（无缝集成）
└── hooks/
    └── pre-install.sh       # pre-install hook（可独立复用）
```

## 2) 决策逻辑

- `< 50`：阻断安装，输出完整 JSON 报告
- `50~74`：告警并询问继续（`--yes` 跳过确认）
- `>= 75`：直接安装

## 3) 使用方式

### A. 显式调用（最稳妥）

```bash
~/.openclaw/skills/skill-trust-guard/install.sh [global opts] [--yes] <slug|path|git-url> [install opts]
```

### B. 无缝集成（推荐）

```bash
~/.openclaw/skills/skill-trust-guard/integrate.sh
export PATH="$HOME/.openclaw/bin:$PATH"
```

此后：
```bash
clawhub install <slug>
```
会自动走 trust guard；其他子命令（search/list/update 等）仍走原始 clawhub。

> 若想永久生效，把 `export PATH="$HOME/.openclaw/bin:$PATH"` 写入 `~/.bashrc` 或 `~/.zshrc`。

## 4) Hook 说明

`hooks/pre-install.sh` 可作为独立 pre-install hook 使用：

```bash
hooks/pre-install.sh <local-skill-path>
# 输出:
# SCORE=...
# SUMMARY=...
# DECISION=allow|warn|reject
# exit code: 0/10/20/30
```

## 5) OpenClaw 原生 Hook 调研结论

已检查 `openclaw hooks` 机制：当前为**内部 agent hook 管理**（session-memory/boot-md/command-logger 类），未发现可直接拦截 `clawhub install` 的官方 preInstall 扩展点。

因此当前最佳可交付路径为：
- **方案 B（wrapper + PATH shim）主实现**
- 同时提供可复用 `pre-install.sh`，便于未来迁移到原生 hook

## 6) 错误处理

- scanner 缺失 / node 或 npx 缺失：fail fast
- clawhub 下载失败（网络/限流/认证问题）：停止并提示日志 `/tmp/skill-trust-guard.install.log`
- 扫描解析失败：停止安装

## 7) WSL/Linux 兼容性

脚本全部使用 POSIX/Bash 常见能力（bash + coreutils），在当前 WSL2 Linux 环境已通过测试。
