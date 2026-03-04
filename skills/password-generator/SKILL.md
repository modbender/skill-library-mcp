---
name: password-generator
description: 生成随机安全密码。长度12-16位随机(默认)，包含大小写字母、数字、符号。当用户要求生成密码、创建密码、随机密码时使用此技能。
---

# Password Generator

生成随机安全密码的工具技能。

## Usage

当用户要求:
- "生成密码"
- "创建一个密码"
- "随机密码"
- "生成12位密码"

执行 `scripts/generate_password.py` 并将生成的密码保存到 `memory/passwords.md`。

## 功能

- 长度: 12-16位随机
- 字符: 大小写字母 + 数字 + 符号

## 保存密码

将生成的密码保存到 `memory/passwords.md`，格式:
```markdown
## [日期]

- **随机密码**
  - 密码: `[密码]`
  - 长度: [长度] 位 (12-16位随机)
  - 字符: 大小写字母 + 数字 + 符号
```
