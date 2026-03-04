# clawhub-login

**ClawHub OAuth 登录助手 - 无头服务器专用**

**version:** 1.0.0  
**author:** 大总管  
**description:** 帮助在无头服务器上通过 OAuth 方式登录 ClawHub，解决浏览器认证问题

---

## 问题场景

在无头服务器（无浏览器）上使用 `clawhub login` 时：
- 默认会尝试打开浏览器 → 失败 (`spawn xdg-open ENOENT`)
- 需要手动获取授权 URL → 在本地浏览器打开 → 完成认证

本 skill 自动化这个流程。

---

## 使用方法

### 方式 1：交互式（推荐）

```bash
python3 ~/.openclaw/workspace/skills/clawhub-login/scripts/clawhub_login.py
```

按提示操作：
1. 复制输出的授权 URL
2. 在本地浏览器打开
3. 授权后复制回调 URL
4. 粘贴到服务器完成登录

### 方式 2：命令行

```bash
# 获取授权 URL
python3 ~/.openclaw/workspace/skills/clawhub-login/scripts/clawhub_login.py --get-url

# 验证登录状态
python3 ~/.openclaw/workspace/skills/clawhub-login/scripts/clawhub_login.py --check

# 退出登录
python3 ~/.openclaw/workspace/skills/clawhub-login/scripts/clawhub_login.py --logout
```

---

## 完整流程

### 步骤 1：运行脚本

```bash
$ python3 scripts/clawhub_login.py

🔐 ClawHub OAuth 登录助手

检测到无头环境，使用手动授权模式...

1. 打开以下 URL（复制到本地浏览器）：
   https://clawhub.ai/cli/auth?redirect_uri=...&state=xxx

2. 授权后，复制浏览器显示的 URL

3. 粘贴回调 URL：
```

### 步骤 2：在本地浏览器打开 URL

- 点击授权
- 浏览器会跳转到回调页面
- 复制完整的回调 URL

### 步骤 3：粘贴到服务器

```bash
粘贴回调 URL：https://clawhub.ai/cli/auth/callback?code=xxx&state=xxx

✅ 登录成功！欢迎 @mengwuzhi
```

---

## 在 OpenClaw 中使用

```bash
# 让 agent 帮你登录
openclaw agent --message "帮我登录 ClawHub"
```

Agent 会：
1. 运行 `clawhub login` 获取授权 URL
2. 输出 URL 让你复制到本地浏览器
3. 等待你提供回调 URL
4. 完成登录

---

## 技术原理

ClawHub 使用 OAuth 2.0 流程：

```
1. CLI 生成授权 URL（含 state 参数）
   ↓
2. 用户在浏览器打开并授权
   ↓
3. ClawHub 重定向到回调 URL（含 code）
   ↓
4. CLI 用 code 交换 token
   ↓
5. Token 保存到 ~/.clawhub/token
```

---

## 故障排查

### 问题：`xdg-open ENOENT`

**原因：** 无头服务器没有图形界面

**解决：** 使用本 skill 的手动授权模式

### 问题：回调 URL 无效

**原因：** 授权已过期或 state 不匹配

**解决：** 重新运行脚本获取新的授权 URL

### 问题：登录状态丢失

**原因：** Token 文件被删除或过期

**解决：** 重新登录

---

## 相关文件

| 文件 | 路径 |
|------|------|
| Token 存储 | `~/.clawhub/token` |
| Token 配置 | `~/.config/clawhub/config.json` |

---

## 安全提示

- ⚠️ Token 相当于密码，不要分享
- ⚠️ 定期更新 Token（重新登录）
- ⚠️ 不要在公共电脑上保存 Token

---

## 基于实战经验

本 skill 基于 2026-02-28 在无头服务器上登录 ClawHub 发布 `create-openclaw-agent` skill 的实战经验总结。

---

## 许可证

MIT License

---

**作者备注：** 这是第一个专门解决 ClawHub 无头登录问题的 skill。
