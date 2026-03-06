# 飞书发图常见坑 — 诊断与修复

## 正确流程（两步缺一不可）

```
Step 1: POST /im/v1/images
  Headers: Authorization: Bearer {tenant_access_token}
  Body: multipart/form-data
    image_type = "message"   ← 必须是 message，不能是 avatar
    image = <binary>
  Response: { data: { image_key: "img-xxxx" } }

Step 2: POST /im/v1/messages
  Body: {
    receive_id: "<chat_id or user_id>",
    msg_type: "image",
    content: JSON.stringify({ image_key: "img-xxxx" })
  }
```

跳过 Step 1，直接把路径/URL 塞进 content → 飞书收到的是纯文字。

---

## 坑 1：助手直接在回复文字中写了文件路径

**现象：** 用户收到类似 `/home/user/.openclaw/media/xxx.jpg` 的字符串

**原因：** 助手用文字回复，没有调用 `message` 工具

**修复：** 明确指示助手"用 message 工具发图"，或重新触发一次

---

## 坑 2：使用了被拦截的 MEDIA 路径格式

**现象：** 图片不展示，消息为空或路径被截断

**原因：** 使用了 `MEDIA:/绝对路径` 或 `MEDIA:~/相对路径`，被安全过滤器拦截

**规则：**
- `MEDIA:/...` — 绝对路径，被拦截
- `MEDIA:~/...` — tilde 路径，被拦截
- `MEDIA:./image.jpg` — 相对路径，允许（但不推荐，应直接用 message 工具）
- `MEDIA:https://example.com/img.jpg` — URL，允许

**修复：** 改用 `message(filePath="/absolute/path")` 工具调用

---

## 坑 3：image_type 选错

**现象：** 上传成功（有 image_key），但发消息后图片显示异常或报错

**原因：** 上传时用了 `image_type=avatar`，该类型的 key 不能用于发消息

**修复：** 上传时 `image_type` 必须为 `message`

---

## 坑 4：Webhook 自定义机器人 vs 机器人应用混用

**现象：** 发图请求不报错，但消息只有文字

**原因：** Webhook 自定义机器人没有 access_token，无法调用 `/im/v1/images` 上传接口

**区别：**
- 群里手动添加的「自定义机器人」= Webhook bot，只能发文字/卡片
- 开放平台自建应用的机器人 = Bot App，完整支持发图

**修复：** 确认 OpenClaw 飞书 channel 配置的是 Bot App（有 app_id + app_secret），不是 Webhook URL

---

## 坑 5：tenant_access_token 过期

**现象：** 图片时好时坏，过几小时后必现

**原因：** tenant_access_token 有效期约 2 小时，过期后上传 API 返回 401/403，image_key 为空，message content 中就剩路径字符串

**错误码：**
- `99991663` — image_key invalid（通常是 token 失效导致上传失败，拿到了空 key）
- `99991400` — access_token expired
- `99991401` — access_token invalid

**修复：** OpenClaw 每次 API 调用前自动刷新 token。如果仍然报错，检查 app_id/app_secret 是否正确配置。

---

## 坑 6：跨租户 image_key

**现象：** 在 A 飞书环境上传的图片，发到 B 环境的群里不显示

**原因：** image_key 与租户绑定，跨租户无效

**修复：** 在目标租户环境重新上传

---

## 快速排查清单

- [ ] 确认用的是 `message` 工具，不是文字回复
- [ ] filePath 是绝对路径且文件存在
- [ ] 飞书 channel 用的是 Bot App（有 im:resource 权限）
- [ ] 上传时 image_type = "message"
- [ ] tenant_access_token 未过期（看错误码）
- [ ] image_key 和目标群在同一租户

---

## 参考

- 飞书官方：上传图片 API https://open.feishu.cn/document/server-docs/im-v1/image/create
- 飞书常见问题 Q&A https://feishu.apifox.cn/doc-1944903
- OpenClaw 权限列表：im:resource, im:message, im:message:send_as_bot（已全部授权）
