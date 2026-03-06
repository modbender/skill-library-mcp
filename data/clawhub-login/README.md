# clawhub-login

**ClawHub OAuth 登录助手 - 无头服务器专用**

---

## 快速开始

```bash
# 交互式登录
python3 scripts/clawhub_login.py

# 检查登录状态
python3 scripts/clawhub_login.py --check

# 退出登录
python3 scripts/clawhub_login.py --logout

# 仅获取授权 URL
python3 scripts/clawhub_login.py --get-url
```

---

## 使用场景

### 场景 1：无头服务器登录

```bash
$ python3 scripts/clawhub_login.py

🔐 ClawHub OAuth 登录助手

1. 打开以下 URL（复制到本地浏览器）：
   https://clawhub.ai/cli/auth?redirect_uri=...

2. 在浏览器中授权

3. 完成后按回车...

✓ 登录成功！欢迎 @mengwuzhi
```

### 场景 2：检查登录状态

```bash
$ python3 scripts/clawhub_login.py --check
✓ 已登录：@mengwuzhi
```

### 场景 3：在 OpenClaw Agent 中使用

```bash
$ openclaw agent --message "帮我登录 ClawHub"

Agent 会运行 clawhub_login.py 并指导你完成登录流程。
```

---

## 功能

| 功能 | 命令 | 说明 |
|------|------|------|
| 交互式登录 | `python3 clawhub_login.py` | 自动获取 URL + 验证 |
| 检查状态 | `--check` | 检查是否已登录 |
| 退出登录 | `--logout` | 删除本地 token |
| 获取 URL | `--get-url` | 仅输出授权 URL |

---

## 技术原理

ClawHub 使用 OAuth 2.0 流程：

1. CLI 生成授权 URL
2. 用户在浏览器授权
3. 回调 URL 包含授权码
4. CLI 用授权码交换 token
5. Token 保存到 `~/.clawhub/token`

本脚本自动化步骤 1-4，适配无头环境。

---

## 文件结构

```
clawhub-login/
├── SKILL.md              # Skill 定义
├── README.md             # 本文档
└── scripts/
    └── clawhub_login.py  # 登录脚本
```

---

## 故障排查

### 问题：无法获取授权 URL

**解决：** 手动运行 `clawhub login` 并复制输出

### 问题：登录验证失败

**解决：** 
1. 确认已在浏览器完成授权
2. 检查网络连接
3. 重新获取授权 URL

### 问题：Token 文件位置

**位置：** `~/.clawhub/token`

---

## 安全提示

- ⚠️ Token 相当于密码
- ⚠️ 不要分享 Token 文件
- ⚠️ 定期重新登录更新 Token

---

## 许可证

MIT License

---

**作者:** 大总管  
**版本:** 1.0.0  
**创建日期:** 2026-02-28
