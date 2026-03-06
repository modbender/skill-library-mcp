---
name: dida365
description: 滴答清单任务管理。管理你的滴答清单任务，包括查看项目、创建任务、完成任务、查询完成历史等。
---

# dida365 - 滴答清单管理

管理你的滴答清单任务。

## 前置要求

- Node.js 18+
- npm 或 pnpm

## 安装

```bash
npm install -g dida365-ai-tools
```

## 认证配置

### 第一步：获取 Cookie

1. 登录网页版滴答清单 https://dida365.com
2. 按 F12 打开开发者工具
3. 切换到 **Application** 标签
4. 左边找到 **Cookies** > **https://dida365.com**
5. 复制 **t** cookie 的值

### 第二步：配置环境变量

```bash
export DIDA365_CLIENT_ID="你的_client_id"
export DIDA365_CLIENT_SECRET="你的_client_secret"
```

> 注意：Client ID 和 Secret 需要去滴答清单开发者平台 https://developer.dida365.com/ 注册应用获取。如果使用 Cookie 认证，只需要设置 Cookie 即可。

### 第三步：保存 Cookie

```bash
dida365 auth cookie "你的cookie值"
```

## 使用命令

### 查看项目列表
```bash
dida365 project list
```

### 查看项目任务
```bash
dida365 project show <projectId>
```

### 创建任务
```bash
dida365 task create "<标题>" -p <projectId>
```

### 完成任务
```bash
dida365 task complete <projectId> <taskId>
```

### 查看今日完成
```bash
dida365 completed today
```

### 查看本周完成
```bash
dida365 completed week
```

### 同步所有数据
```bash
dida365 sync all
```

## 项目 ID

运行以下命令查看你的项目 ID：

```bash
dida365 project list
```

常见项目类型：
- 收集箱 (Inbox)
- 自定义项目

## OpenClaw 集成

在 OpenClaw 中使用，可以创建一个 wrapper 脚本：

```bash
#!/bin/bash
export DIDA365_CLIENT_ID="你的_client_id"
export DIDA365_CLIENT_SECRET="你的_client_secret"
dida365 "$@"
```

保存为 `dida365` 并添加到 PATH，然后在飞书里直接调用命令即可。
