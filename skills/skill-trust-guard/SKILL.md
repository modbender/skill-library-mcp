---
name: skill-trust-guard
description: 在安装 skill 前强制执行 skill-trust-scanner 安全扫描，并按评分执行拦截策略。
---

# skill-trust-guard

在安装 skill 前强制执行 **skill-trust-scanner** 安全扫描，并按评分执行拦截策略。

## 目标
- 把 `clawhub install` 前置为“先扫描再安装”
- 默认阻断高风险 skill，降低供应链投毒风险
- 保持现有 CLI 习惯（可用 shim 覆盖原命令）

## 评分策略
- **score < 50**：拒绝安装（block）
- **50 <= score < 75**：告警，需人工确认（`--yes` 可自动继续）
- **score >= 75**：直接安装

## 组成
- `install.sh`：主包装器（方案 B）
- `hooks/pre-install.sh`：可复用 pre-install hook（本地路径扫描 + 决策）
- `integrate.sh`：生成 PATH shim，让 `clawhub install` 自动走 guard
- `README.md`：安装/集成/测试说明

## 依赖
- scanner: `/home/guofeng/clawd/skill-trust-scanner/src/cli.ts`
- Node.js + npx
- clawhub CLI

## 用法
```bash
~/.openclaw/skills/skill-trust-guard/install.sh <slug|path|git-url>
```

或执行：
```bash
~/.openclaw/skills/skill-trust-guard/integrate.sh
export PATH="$HOME/.openclaw/bin:$PATH"
```
之后直接使用：
```bash
clawhub install <skill>
```
（自动触发 trust guard）
