---
name: linkedin-warmup
description: LinkedIn 新号自动化养号与轻量加人获客（每日定时 10 分钟左右），通过 AdsPower 指纹浏览器 Local API 启动指定浏览器（可指定 CDP 端口），再用 OpenClaw browser 工具控制 profile=linkedin 的 Chrome 会话，在 My Network 到 More suggestions for you 的推荐区按“先看主页再返回再 Connect”的节奏发送 2-3 个连接邀请；遇到验证码/风控/限制提示立刻停止并通知。
---

# LinkedIn 养号（MVP）

本 skill 用于**每天定时**对 LinkedIn 新号做一套“更像真人”的轻量操作（约 10 分钟）：
- 先浏览 feed 热身
- 再去 My Network 的推荐列表里挑人
- 对每个候选：**先点进 profile 停留** → 返回 → 再点 **Connect**
- 目标：每天 **2-3 个 Connect**（不写 note，保持简单）

> 重要：指纹浏览器只能降低“环境指纹”风险，不能消除平台对“行为异常/频率异常”的风控。务必低频、随机化、遇到验证立即停。

## 运行方式（推荐：cron 定时）

用 cron job 触发（Asia/Shanghai 时区），payload 里传入参数（JSON）。

## 输入参数（建议格式）

将参数作为 JSON 传入（示例）：

```json
{
  "adsPower": {
    "baseUrl": "http://127.0.0.1:50325",
    "apiKey": "YOUR_API_KEY",
    "userId": "k194pjlr",
    "cdpPort": 30001
  },
  "browserProfile": "linkedin",
  "durationMin": 10,
  "connectTarget": 3,
  "connectMin": 2,
  "perSourceConnectMax": 2,
  "headless": false
}
```

参数说明（MVP 只实现最关键的几个即可）：
- `adsPower.userId`：AdsPower 配置文件 ID
- `adsPower.cdpPort`：期望的 CDP 端口（通过 `launch_args=["--remote-debugging-port=..."]` 设置）
- `browserProfile`：OpenClaw browser profile 名（这里固定 `linkedin`）
- `durationMin`：单次运行时长上限
- `connectMin/connectTarget`：每天 Connect 数（建议新号 2-3）

## 工作流（MVP 剧本）

### 0) 启动指纹浏览器（AdsPower Local API）

使用 Local API 启动浏览器：
- `GET /api/v1/browser/start?user_id=...&launch_args=["--remote-debugging-port=30001"]`
- Header：`Authorization: Bearer API_KEY`（API_KEY 用实际值替换）

成功后会返回：
- `data.debug_port`
- `data.ws.puppeteer`

### 1) 让 OpenClaw browser 接管（profile=linkedin）

- `browser.start(profile="linkedin")`（attachOnly 模式）
- 打开 LinkedIn：`https://www.linkedin.com/`

### 2) 热身（2 分钟，低风险）

- 在 feed 页面：
  - 随机滚动 3-6 次（每次间隔 2-6 秒）
  - 随机点开 1 条内容停留 15-40 秒后返回

### 3) 去 My Network 找推荐（3 分钟）

- 访问：`https://www.linkedin.com/mynetwork/`
- 找到区域：`More suggestions for you`

### 4) 加 2-3 个推荐好友（5 分钟）

循环直到达到 `connectTarget` 或到达 `durationMin`：

对每个候选：
1. 点击候选的 profile 链接进入个人页
2. 停留 10-25 秒，轻微滚动 1-2 次
3. 返回上一页（推荐列表）
4. 点击 `Connect`
5. 如果出现弹窗：优先选择“不加 note 直接发送”（若 UI 提供）

**节奏要求（像人一点）**
- Connect 之间至少间隔 20-60 秒（随机）
- 不要连续快速连点多个 Connect

### 5) 风控/验证码处理（必须）

如果检测到以下任一情况：
- Captcha/Verify/Challenge
- “You’ve reached the weekly invitation limit”
- “We restrict certain activity…”
- 页面持续加载异常/按钮点击无响应

立刻：
- 停止后续动作
- 输出一条告警文本（用于 cron deliver 到钉钉）

### 6) 收尾：关闭浏览器

- 调用 AdsPower：`GET /api/v1/browser/stop?user_id=...`

## 输出（用于钉钉通知）

MVP 输出建议用中文简报：
- 今日运行时长
- 访问 feed 动作完成情况
- 已发送 Connect 数量 + 名单（姓名 + profile URL）
- 是否遇到验证码/限制（如有，提示你手工处理）

## 约束（MVP 简化点）

- 只使用入口：**My Network → More suggestions for you**
- 不做私信、不做评论
- 不做复杂关键词筛选（先稳定跑通）
