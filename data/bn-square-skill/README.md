# bn-square-skill

Binance Square 自动发文 skill，给 AI Agent（OpenClaw）使用。

支持三个操作：验证 session、发布帖子、查询帖子状态。

## 快速开始

### 1. 获取 Cookie

1. 登录 https://www.binance.com/en/square
2. 按 `F12` 打开 DevTools → **Network** 标签
3. 刷新页面，点击任意 `/bapi/` 请求
4. 在 **Request Headers** 中复制：
   - `cookie` 完整值 → `BINANCE_COOKIE_HEADER`
   - `csrftoken` cookie 值（`csrftoken=xxx` 中的 `xxx`）→ `BINANCE_CSRF_TOKEN`

### 2. 设置环境变量

```bash
export BINANCE_COOKIE_HEADER="csrftoken=abc123; session=xyz..."
export BINANCE_CSRF_TOKEN="abc123"
```

### 3. 使用

```bash
# 验证 session
node scripts/bn-square.mjs validate_session

# 发布帖子
node scripts/bn-square.mjs publish_post '{"content":"Hello Binance Square!"}'

# 查询帖子状态
node scripts/bn-square.mjs get_post_status '{"postId":"123456"}'
```

## 安装

```bash
git clone https://github.com/Phlegonlabs/bn-square-skill.git
cd bn-square-skill
```

## 安全注意事项

- **不要** 把 `.env` 或含有真实 cookie 的文件提交到 Git
- **不要** 把 cookie/token 发送到 `*.binance.com` 以外的域名
- Cookie 会过期，需要定期重新获取
