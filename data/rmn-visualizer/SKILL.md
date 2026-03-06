---
name: RMN Visualizer — 递归记忆神经网络可视化
description: RMN Visualizer 扫描你的 Agent 记忆文件（MEMORY.md, memory/.md, .issues/），
  自动解析为 5 层递归神经网络，并用 D3.js 力导向图实时可视化。
---

# RMN Visualizer — 递归记忆神经网络可视化

> 一键查看你的 AI Agent 大脑结构

## Overview

RMN Visualizer 扫描你的 Agent 记忆文件（MEMORY.md, memory/*.md, .issues/*），
自动解析为 5 层递归神经网络，并用 D3.js 力导向图实时可视化。

零外部依赖，纯 Node.js 内置 HTTP server + 内嵌 D3.js。

## When to Activate

- 用户说 "可视化记忆" / "visualize memory" / "show memory network" / "记忆网络"
- 用户说 "看看我的大脑" / "memory map" / "brain map"

## Quick Launch (推荐)

一键启动本地服务 + Cloudflare Tunnel，返回公网链接到聊天窗口：

```bash
node <skill_directory>/scripts/launch.js
```

**stdout 只输出一行公网 URL**（如 `https://xxx.trycloudflare.com`），
agent 应该把这个链接直接发给用户，附上简要说明。

需要 `cloudflared` 已安装。如果没有，fallback 到本地模式。

## Local Only

```bash
node <skill_directory>/scripts/serve.js
```

然后打开 http://localhost:3459

## What You See

- 5 层彩色节点：Identity (红) → Semantic (橙) → Episodic (黄) → Working (绿) → Sensory (蓝)
- 节点大小 = 权重（越重要越大）
- 连线 = 记忆关联
- 悬停显示详情
- 实时统计面板：节点数、连接数、各层分布、平均权重
- 衰减动画：权重低的节点逐渐透明

## Configuration

默认扫描 OpenClaw workspace 下的文件。可通过环境变量覆盖：

```bash
RMN_WORKSPACE=/path/to/workspace node scripts/launch.js
RMN_PORT=3459 node scripts/launch.js
```

## Architecture

```
Memory Files (MEMORY.md, memory/*.md, .issues/*)
  ↓ [Parser — 正则 + 启发式分层]
5-Layer Neural Network (JSON)
  ↓ [D3.js Force Simulation]
Interactive Visualization (Browser)
```
