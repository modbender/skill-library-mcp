---
name: xianyu-auto-fulfill
description: 闲鱼自动发货监控。使用 agent-browser 自动检查闲鱼新消息，检测付款订单并自动发货。触发词：闲鱼发货、闲鱼监控、闲鱼自动化、xianyu、自动发货。
---

# 闲鱼自动发货

自动监控闲鱼聊天，检测付款订单并执行发货。

## 首次使用必读

**⚠️ 发货方式因人而异，首次使用时必须询问用户：**

> "请问您的发货方式是什么？例如：
> 1. 调用 API 获取秘钥/激活码
> 2. 从本地秘钥池文件读取
> 3. 发送网盘链接
> 4. 发送固定文本
> 5. 其他方式
> 
> 请描述您的发货流程，我会据此配置自动化。"

**不要假设用户的发货方式，不要预填任何 API 地址或秘钥。**

---

## ⚠️ 重要经验教训

### 1. 不要点击"去发货"按钮

**原因：** 点击"去发货"按钮会弹出需要 APP 扫码确认的对话框，网页版无法完成此操作。

**正确做法：** 检测到付款订单后，直接在聊天框发送秘钥/链接即可，无需点击任何按钮。

### 2. 定时任务必须使用 main session

**原因：** isolated session 每次启动都是新的浏览器实例，无法复用已登录的 Chrome profile，导致需要重新登录。

**正确做法：**
```bash
openclaw cron add \
  --name "闲鱼自动发货" \
  --cron "* * * * *" \
  --tz "Asia/Shanghai" \
  --session main \  # 必须用 main，不能用 isolated
  --system-event "检查闲鱼新消息..."
```

### 3. 快速判断：无新消息 = 无新订单

**如果当前聊天列表没有显示新消息（没有红点、没有"刚刚"时间戳），可以快速结束检查，无需进入每个聊天详情。**

**快速检查方法：**
```bash
agent-browser snapshot | grep -E "我已付款|等待卖家发货|刚刚|分钟前" | head -5
```

如果没有匹配结果，说明没有新订单，直接结束即可。

---

## 核心流程

### 1. 打开闲鱼聊天页面

```bash
agent-browser open "https://www.goofish.com/im"
```

首次需要登录，建议使用 Chrome profile 保持登录状态：

```bash
agent-browser --headed --profile "$HOME/Library/Application Support/Google/Chrome/Default" open "https://www.goofish.com/im"
```

### 2. 快速检测待发货订单

**快速检查（推荐）：**
```bash
agent-browser snapshot | grep -E "我已付款|等待卖家发货"
```

- **无匹配结果** → 无新订单，结束检查
- **有匹配结果** → 进入聊天发货

**付款订单特征（必须同时满足）：**
- 系统消息卡片（带图标）
- 文本包含："我已付款，等待你发货" 或 "等待卖家发货"
- 存在"去发货"按钮（但不要点击它！）

**不能发货的情况：**
- 用户手打文本（如"老板发货"）
- 没有"去发货"按钮
- "待付款"状态

### 3. 执行发货

**进入聊天：**
```bash
agent-browser find text "买家昵称" click
```

**发送消息（不要点"去发货"按钮）：**
```bash
agent-browser type @<输入框ref> "您的秘钥：xxx，祝您使用愉快！"
agent-browser click @<发送按钮ref>
```

### 4. 返回聊天列表

```bash
agent-browser open "https://www.goofish.com/im"
```

---

## 设置定时任务

使用 OpenClaw cron 创建定时监控（**必须用 main session**）：

```bash
openclaw cron add \
  --name "闲鱼自动发货" \
  --cron "* * * * *" \
  --tz "Asia/Shanghai" \
  --session main \
  --system-event "检查闲鱼新消息，有付款订单就发货。发货方式：<根据用户回答填写>" \
  --wake now
```

**常用命令：**
```bash
openclaw cron list              # 查看任务
openclaw cron run <jobId>       # 手动触发
openclaw cron runs --id <jobId> # 运行历史
openclaw cron remove <jobId>    # 删除任务
```

---

## 发货方式示例

以下是常见发货方式，**仅供参考，以用户实际回答为准：**

### 示例1：API 获取秘钥
```
用户回答："调用我们的 API 获取激活码"
实现：curl 调用 API → 解析返回 → 发送给买家
```

### 示例2：本地秘钥池
```
用户回答："从一个 txt 文件里读，用一行删一行"
实现：读取文件 → 取第一行 → 删除该行 → 发送给买家
```

### 示例3：固定链接
```
用户回答："发同一个网盘链接就行"
实现：直接发送固定文本
```

### 示例4：混合方式
```
用户回答："先发教程链接，再调用 API 发激活码"
实现：分两步发送不同内容
```

---

## 注意事项

1. **不要过度频繁检查** - 建议每分钟或更长间隔
2. **保持浏览器会话** - 使用 Chrome profile 避免重复登录
3. **快速结束无新订单的检查** - 节省资源
4. **异常处理** - API 失败时应告知用户，不要发送错误内容
