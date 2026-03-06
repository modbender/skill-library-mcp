---
name: GPU 状态检查 (gpu_check)
description: 实时获取局域网内分布式 AI 算力节点的显存占用情况。
---

# GPU 状态检查 (gpu_check)

实时获取局域网内分布式 AI 算力节点的显存占用情况。

## 功能
* 自动轮询 3090 (192.168.2.236) 和 4090 (192.168.2.164) 的显存状态
* 输出带进度条的 Markdown 表格
* 监控各节点 API 服务在线情况

## 依赖
* Node.js 环境（已内置）
* axios 库（需安装）

## 安装
1. 在技能目录安装依赖：
   ```bash
   cd ~/.openclaw/workspace/skills/gpu_check
   npm init -y
   npm install axios
   ```
2. 确保 GPU 节点 API 已启动（需在 192.168.2.236 和 192.168.2.164 运行支持 `/gpu` 端点的服务）

## 使用
在聊天中发送：
- `/gpu`
- `@机器人 显卡状态`
- `查看 GPU 占用`