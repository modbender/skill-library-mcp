# 从浏览器获取 ClawHub Token 指南

## 方法 1：通过开发者工具（推荐）

### 步骤

**1. 打开 ClawHub 网站**
- 访问 https://clawhub.ai/ 或 https://clawhub.biz/
- 确保你已经登录

**2. 打开开发者工具**
- Windows: 按 `F12` 或 `Ctrl+Shift+I`
- 或右键点击页面 → "检查"

**3. 切换到 Network（网络）标签**

**4. 刷新页面**
- 按 `F5` 刷新
- 会看到很多网络请求

**5. 查找 API 请求**
- 在左侧请求列表中找包含 `api` 的请求
- 常见 URL 模式：
  - `https://clawhub.ai/api/...`
  - `https://api.clawhub.ai/...`
  - `https://clawhub.biz/api/...`

**6. 查看请求头**
- 点击该请求
- 在右侧找到 "Headers"（请求头）标签
- 查找以下字段之一：

```
Authorization: Bearer eyJhbGc...（很长一串）
```
或
```
Cookie: token=eyJhbGc...
```
或
```
x-api-key: sk-...
```

**7. 复制 Token**
- 复制 `Bearer ` 后面的部分（不包括 "Bearer "）
- 或复制 `token=` 后面的值

---

## 方法 2：查看 LocalStorage

**1. 打开开发者工具** (F12)

**2. 切换到 Application（应用）标签**
- 或 Storage（存储）标签（Firefox）

**3. 左侧展开 Local Storage**
- 点击 `https://clawhub.ai` 或对应域名

**4. 查找 Token**
- 在右侧找 key 为 `token` / `auth_token` / `clawhub_token` 的项
- 复制对应的值

---

## 方法 3：查看账号设置页面

**1. 登录 ClawHub**

**2. 进入账号设置**
- 点击右上角头像
- 选择 "Settings" 或 "Account"
- 找 "API Keys" 或 "API Token" 选项

**3. 生成/复制 Token**
- 如果有现成的，直接复制
- 如果没有，点击 "Generate New Token" 创建一个新的

---

## 在服务器上使用 Token

拿到 Token 后，在服务器上执行：

```bash
# 登录
clawhub login --token <粘贴-Token> --label "server-cli"

# 验证
clawhub whoami

# 发布 skill
cd /root/.openclaw/workspace/skills/create-agent
clawhub publish .
```

---

## 常见问题

**Q: Token 格式是什么样的？**
A: 通常是很长的字符串，如 `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**Q: Token 会过期吗？**
A: 可能会，如果发布失败，重新获取一个新的

**Q: 安全吗？**
A: Token 相当于密码，不要分享给他人

---

## 需要帮助？

如果以上方法都找不到，告诉我：
1. 你访问的 ClawHub URL 是什么
2. 登录后页面长什么样
3. 我可以帮你找更具体的方法
