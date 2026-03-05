---
name: xiaoyu-bot-status
description: 小雨 bot 状态监测页面技能包。提供实时监控 OpenClaw Agent 工作状态、定时任务和系统健康状况的 Web 界面。包含静态缓存机制确保快速加载，美化 UI 界面，以及独立部署能力。使用场景：需要监控 AI Agent 运行状态、查看最近工作记录、管理定时任务、检查系统健康状况。
---

# 小雨 Bot 状态监测页面

## 概述

这是一个完整的 Web 应用，用于实时监控 OpenClaw Agent 的运行状态。它提供三个主要功能模块：
- **最近工作**：显示 Agent 最近完成的工作任务
- **定时任务**：显示当前配置的定时任务及其下次执行时间  
- **健康状态**：显示系统运行时间、CPU 负载、内存可用性、OpenClaw 连接状态等

## 核心特性

### 静态缓存优先
- 页面加载时优先从 `status-cache.json` 静态文件读取数据
- 确保用户访问时立即显示内容，避免"加载中..."等待
- 后台静默从 API 获取最新数据并更新显示

### 美化 UI 界面
- 渐变背景设计（紫色到蓝色）
- 响应式卡片布局，支持桌面和移动设备
- 悬停动画效果，提升用户体验
- 彩色状态指示器（绿色正常、黄色警告、红色错误）

### 独立部署
- 完全独立的 Node.js 服务器，不依赖 OpenClaw 主进程
- 可以在任意端口运行（默认 8888）
- 支持 Cloudflare Tunnel 外网访问

### 隐藏彩蛋功能
- 在标题上连续点击 7 次可激活隐藏聊天窗口
- 支持与小雨进行秘密对话（需验证身份）

## 部署说明

### 文件结构
```
xiaoyu-bot-status/
├── SKILL.md
├── server.js              # 主服务器文件
├── public/                # 静态资源目录
│   ├── index.html         # 主页面（包含静态缓存逻辑）
│   └── status-cache.json  # 静态缓存文件
├── scripts/               # 数据获取脚本
│   ├── get-work-tasks-fixed.js      # 获取最近工作数据
│   ├── get-scheduled-tasks-simple.js # 获取定时任务数据  
│   └── auto-update-work-fixed.js    # 自动更新工作记录
└── references/            # 参考文档
    └── api-spec.md        # API 接口规范
```

### 启动服务
```bash
# 在技能目录下运行
node server.js

# 或使用启动脚本
./start.sh
```

### 自动缓存更新
创建 cron 任务每 3 小时更新缓存：
```bash
# 缓存更新脚本位置
/home/admin/openclaw/workspace/skills/xiaoyu-bot-status/scripts/update-cache.sh
```

## API 接口

### GET /api/status
返回完整的状态数据，包含：
- `recent_work`: 最近工作列表
- `scheduled_tasks`: 定时任务列表  
- `health_status`: 系统健康状态
- `last_updated`: 最后更新时间

### POST /api/chat
处理隐藏聊天功能的消息（需要身份验证）

## 使用场景

- **日常监控**：定期查看 Agent 工作状态和系统健康度
- **故障排查**：当 Agent 出现异常时快速定位问题
- **任务管理**：查看和验证定时任务的执行情况
- **性能优化**：监控 CPU 和内存使用情况
- **演示展示**：向他人展示 AI Agent 的工作成果

## 维护建议

- 定期检查缓存更新脚本是否正常运行
- 监控服务器日志 (`server.log`) 发现潜在问题
- 根据实际需求调整数据刷新频率（默认 2 秒后台刷新）
- 如需修改 UI 样式，直接编辑 `public/index.html` 中的 CSS 部分