# 获取飞书 Webhook 指南

## 什么是飞书 Webhook？

Webhook 是一个 URL 地址，OpenClaw 通过这个地址把监控报告发送到你的飞书群聊。

**格式示例：**
```
https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## 方法 1：群聊机器人（推荐）⭐

这是最简单的方法，适合大多数用户。

### 步骤 1：打开飞书群聊

1. 打开飞书 App 或网页版
2. 选择一个群聊（或创建新群）
   - 建议创建专门的"品牌监控"群
   - 可以只有你一个人

### 步骤 2：添加机器人

1. 点击群聊右上角的 **"..."** 或 **"设置"**
2. 选择 **"群机器人"** 或 **"机器人"**
3. 点击 **"添加机器人"**
4. 选择 **"自定义机器人"** 或 **"Custom Bot"**

### 步骤 3：配置机器人

1. **机器人名称**：输入 `品牌监控` 或 `Brand Monitor`
2. **机器人描述**（可选）：`自动发送品牌舆情监控报告`
3. **机器人头像**（可选）：可以上传一个图标
4. 点击 **"添加"** 或 **"确定"**

### 步骤 4：复制 Webhook

添加成功后，会显示 Webhook 地址：

```
https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**重要：** 
- ✅ 立即复制这个地址（只显示一次！）
- ✅ 保存到安全的地方
- ✅ 不要分享给其他人

### 步骤 5：测试 Webhook

在终端中测试：

```bash
curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/717f654e-cd41-470e-9ce5-7c738df9592f" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "text",
    "content": {
      "text": "测试消息：品牌监控机器人已连接 ✅"
    }
  }'
```

**成功标志：** 群聊中收到测试消息

---

## 方法 2：企业自建应用

适合企业用户，需要管理员权限。

### 步骤 1：创建应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 登录你的飞书账号
3. 点击 **"创建企业自建应用"**
4. 填写应用信息：
   - **应用名称**：`品牌监控`
   - **应用描述**：`自动监控品牌舆情`
   - **应用图标**：上传图标（可选）
5. 点击 **"创建"**

### 步骤 2：获取凭证

1. 进入应用详情页
2. 记录 **App ID** 和 **App Secret**
3. 这些凭证用于获取 access_token

### 步骤 3：添加机器人能力

1. 在应用页面，点击 **"添加应用能力"**
2. 选择 **"机器人"**
3. 配置机器人信息

### 步骤 4：配置权限

1. 进入 **"权限管理"**
2. 添加以下权限：
   - `im:message` - 发送消息
   - `im:message:send_as_bot` - 以机器人身份发送
3. 点击 **"发布版本"**

### 步骤 5：获取 Webhook

有两种方式：

#### 方式 A：使用群机器人 Webhook（推荐）

1. 在群聊中添加你创建的机器人
2. 按照方法 1 的步骤获取 Webhook

#### 方式 B：使用 API 发送

使用 App ID 和 App Secret 获取 access_token，然后通过 API 发送消息。

**注意：** 这种方式较复杂，推荐使用方式 A。

---

## 方法 3：个人机器人

适合个人用户，接收私聊消息。

### 步骤 1：搜索机器人

1. 在飞书中搜索你创建的机器人名称
2. 或者使用机器人的 App ID

### 步骤 2：发起对话

1. 点击机器人
2. 发送一条消息（激活对话）

### 步骤 3：获取 Webhook

个人机器人通常需要使用 API 方式发送消息，较为复杂。

**推荐：** 使用方法 1（群聊机器人）更简单。

---

## 图文教程

### 1. 打开群聊设置

<img src="docs/images/feishu-step1.png" width="300" alt="打开群聊设置">

点击群聊右上角的 **"..."**

### 2. 选择群机器人

<img src="docs/images/feishu-step2.png" width="300" alt="选择群机器人">

选择 **"群机器人"** → **"添加机器人"**

### 3. 选择自定义机器人

<img src="docs/images/feishu-step3.png" width="300" alt="选择自定义机器人">

选择 **"自定义机器人"**

### 4. 配置机器人

<img src="docs/images/feishu-step4.png" width="300" alt="配置机器人">

输入名称：`品牌监控`

### 5. 复制 Webhook

<img src="docs/images/feishu-step5.png" width="300" alt="复制 Webhook">

**立即复制 Webhook 地址！**

---

## 验证 Webhook

### 方法 1：使用 curl 测试

```bash
curl -X POST "你的Webhook地址" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "text",
    "content": {
      "text": "✅ 测试成功！品牌监控机器人已连接"
    }
  }'
```

### 方法 2：使用 PowerShell 测试（Windows）

```powershell
$webhook = "你的Webhook地址"
$body = @{
    msg_type = "text"
    content = @{
        text = "✅ 测试成功！品牌监控机器人已连接"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri $webhook -Method Post -Body $body -ContentType "application/json"
```

### 方法 3：使用在线工具测试

1. 访问 [Postman](https://www.postman.com/) 或类似工具
2. 创建 POST 请求
3. URL：你的 Webhook 地址
4. Headers：`Content-Type: application/json`
5. Body：
   ```json
   {
     "msg_type": "text",
     "content": {
       "text": "测试消息"
     }
   }
   ```
6. 发送请求

**成功标志：** 群聊收到测试消息

---

## 配置到 config.json

获取 Webhook 后，添加到配置文件：

```bash
cd ~/.openclaw/workspace/skills/brand-monitor
nano config.json
```

```json
{
  "brand_name": "理想汽车",
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/你的Webhook"
}
```

保存并测试：

```bash
openclaw skill run brand-monitor monitor
```

---

## 常见问题

### Q: Webhook 地址在哪里找？

A: 添加自定义机器人时会显示，只显示一次。如果忘记了，需要删除机器人重新添加。

### Q: 可以使用同一个 Webhook 吗？

A: 可以。一个 Webhook 可以用于多个 skill 或多个品牌监控。

### Q: Webhook 会过期吗？

A: 不会。除非你删除了机器人，Webhook 会一直有效。

### Q: 如何删除机器人？

A: 
1. 进入群聊设置
2. 选择"群机器人"
3. 找到机器人，点击"移除"

### Q: 可以修改机器人名称吗？

A: 可以。在群机器人设置中修改，Webhook 地址不变。

### Q: 测试时没有收到消息？

A: 检查：
1. Webhook 地址是否完整
2. 是否在正确的群聊中
3. 网络是否正常
4. curl 命令是否有错误提示

### Q: 报告发送失败？

A: 
1. 检查 Webhook 是否正确
2. 检查网络连接
3. 查看 OpenClaw 日志：
   ```bash
   tail -f ~/.openclaw/logs/gateway.log | grep message
   ```

### Q: 可以发送到多个群吗？

A: 可以。创建多个机器人，获取多个 Webhook，在配置中使用数组：
```json
{
  "feishu_webhooks": [
    "webhook1",
    "webhook2"
  ]
}
```

但当前版本只支持单个 Webhook，需要修改代码支持多个。

---

## 安全建议

### ✅ 应该做的

1. **保密 Webhook**：不要分享给其他人
2. **定期检查**：定期检查群成员，确保只有授权人员
3. **使用专用群**：创建专门的监控群，不要在工作群中添加
4. **备份 Webhook**：保存到密码管理器

### ❌ 不应该做的

1. **不要公开**：不要提交到 Git、不要发到公开渠道
2. **不要共享**：不要分享给不相关的人
3. **不要硬编码**：不要直接写在代码中

---

## 快速参考

### 获取 Webhook（3步）

1. 打开飞书群聊 → 设置 → 群机器人
2. 添加机器人 → 自定义机器人 → 输入名称
3. 复制 Webhook 地址

### 测试 Webhook

```bash
curl -X POST "你的Webhook" \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"测试"}}'
```

### 配置到 config.json

```json
{
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
}
```

---

## 需要帮助？

- 飞书开放平台文档：https://open.feishu.cn/document/
- 飞书机器人指南：https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN
- 本项目 Issues：https://github.com/your-repo/issues

---

**总结：** 最简单的方法是在群聊中添加自定义机器人，立即获取 Webhook 地址。整个过程不超过 2 分钟！🚀
