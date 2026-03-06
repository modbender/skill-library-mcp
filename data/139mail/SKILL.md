---
name: 139mail
description: 139邮箱IMAP/POP3操作技能。支持通过IMAP/POP3协议查看收件箱/未读邮件、发送邮件、搜索邮件、管理邮件、邮件分拣。首次使用需配置账号和授权码。当用户需要操作139邮箱（mail.10086.cn）时触发此技能。
---

# 139邮箱IMAP/POP3操作技能

## 概述

本技能通过IMAP/POP3协议直接连接139邮箱服务器，实现高效的邮件管理功能。

**重要：首次使用需配置账号和授权码**

## 安装依赖

本技能需要安装第三方依赖库：

```bash
pip install imapclient
```

**依赖说明**：
- `imapclient`：用于IMAP协议连接139邮箱服务器
- 标准库：`smtplib`, `email`, `json`, `argparse`（Python内置）

## SSL/TLS 安全说明

由于139邮箱服务器使用的是较旧版本的TLS协议（TLS 1.0/1.1），本技能使用兼容模式连接。
**安全建议**：
- 兼容模式会降低SSL安全性，建议仅在受信任的网络环境中使用

## 首次使用流程

当用户首次请求操作139邮箱时：

### 第1步：环境检查（推荐）

运行环境检查脚本，确保所有依赖就绪：

```bash
python scripts/check_env.py
```

此脚本会检查：
- Python版本 >= 3.8
- OpenSSL版本 >= 1.1.1
- imapclient模块已安装
- SSL兼容性设置
- 配置文件是否存在

### 第2步：安装依赖

```bash
pip install imapclient
```

### 第3步：开启IMAP服务并获取授权码

1. 前往 https://mail.10086.cn/ 登录邮箱
2. 进入 **设置 → 账户 → IMAP/POP3服务**
3. 开启 **IMAP/SMTP服务**
4. 获取**授权码**（16位字符串，不是登录密码！）

⚠️ **重要**：授权码只显示一次，请务必保存！

### 第4步：保存配置

```bash
python scripts/config_manager.py save --username 136xxxxxxxxx@139.com --password 你的授权码
```

### 第5步：测试连接

```bash
python scripts/check_mail.py --limit 5
```

如果显示邮件列表，说明配置成功！

### 快速开始（一步完成）

```bash
# 1. 安装依赖
pip install imapclient

# 2. 运行环境检查
python scripts/check_env.py

# 3. 配置账号（替换为你的账号和授权码）
python scripts/config_manager.py save --username 136xxxxxxxxx@139.com --password xxxxxxxxxxxxxxxx

# 4. 查看邮件
python scripts/check_mail.py --unread
```

## 配置管理

**脚本**：`scripts/config_manager.py`

**命令**：
- `python scripts/config_manager.py check` - 检查是否已配置
- `python scripts/config_manager.py save --username <账号> --password <授权码>` - 保存配置
- `python scripts/config_manager.py show` - 显示当前配置（隐藏授权码）

**配置文件**：`config/139mail.conf`

配置文件格式（JSON）：
```json
{
  "username": "136xxxxxxxxx@139.com",
  "password": "授权码",
  "imap_server": "imap.139.com",
  "imap_port": 993,
  "smtp_server": "smtp.139.com",
  "smtp_port": 465
}
```

## 项目结构

```
skills/139mail/
├── SKILL.md                    # 本文件 - 使用文档
├── config/                     # 配置目录
│   └── 139mail.conf           # 账号配置文件（自动创建）
├── references/                 # 参考资料
│   ├── credentials.md         # 服务器配置信息
│   └── imap_guide.md          # IMAP操作指南
└── scripts/                    # 核心脚本
    ├── check_env.py           # ⭐ 环境检查脚本（新手先用）
    ├── config_manager.py      # 配置管理
    ├── check_mail.py          # 查看邮件
    ├── view_mail.py           # 查看邮件详情
    ├── send_mail.py           # 发送邮件
    ├── search_mail.py         # 搜索邮件
    ├── manage_mail.py         # 邮件管理（标记/删除）
    └── move_mail.py           # 邮件分拣
```

## 核心功能

### 1. 查看收件箱/未读邮件

**触发场景**："查看139邮箱"、"有没有新邮件"

**流程**：
1. 检查配置是否存在（`config_manager.py check`）
2. 如无配置，执行首次使用流程
3. 调用 `scripts/check_mail.py --unread`

**命令示例**：
```bash
python scripts/check_mail.py --limit 10
python scripts/check_mail.py --unread
```

### 2. 查看指定邮件详情

**脚本**：`scripts/view_mail.py <邮件ID>`

**示例**：
```bash
python scripts/view_mail.py 123
```

### 3. 发送邮件

**脚本**：`scripts/send_mail.py <收件人> <主题> <正文>`

**示例**：
```bash
python scripts/send_mail.py "recipient@example.com" "主题" "正文内容"
```

### 4. 搜索邮件

**脚本**：`scripts/search_mail.py <关键词>`

**示例**：
```bash
python scripts/search_mail.py "工作汇报"
```

### 5. 管理邮件

**脚本**：`scripts/manage_mail.py`

**常用命令**：
```bash
# 列出邮件
python scripts/manage_mail.py --list

# 列出已删除邮件
python scripts/manage_mail.py --list-trash

# 标记已读/未读
python scripts/manage_mail.py --mark-read <ID>
python scripts/manage_mail.py --mark-unread <ID>

# 删除邮件（移动到已删除文件夹）
python scripts/manage_mail.py --delete <ID>

# 恢复邮件（从已删除文件夹恢复）
python scripts/manage_mail.py --restore <ID>

# 彻底删除（永久删除，不可恢复）
python scripts/manage_mail.py --permanent-delete <ID>
```

### 6. 邮件分拣

**脚本**：`scripts/move_mail.py`

**示例**：
```bash
# 列出所有文件夹
python scripts/move_mail.py --list-folders

# 移动邮件
python scripts/move_mail.py --move <邮件ID> --to <目标文件夹>
```

## 错误处理与故障排除

### 常见错误及解决方案

#### 1. SSL握手失败
**错误信息**：
```
[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure
```

**原因**：
- 139邮箱使用较旧的TLS 1.0/1.1协议
- Python 3.10+ 默认OpenSSL安全级别过高

**解决方案**：
本技能已自动配置兼容性设置，无需手动修改。如仍失败：
```bash
# 检查Python版本
python --version  # 需要 >= 3.8

# 检查OpenSSL版本
python -c "import ssl; print(ssl.OPENSSL_VERSION)"  # 需要 >= 1.1.1
```

#### 2. 登录失败
**错误信息**：
```
imapclient.exceptions.LoginError
```

**检查清单**：
- [ ] 账号格式正确：`136xxxxxxxxx@139.com`（不是纯手机号）
- [ ] 使用的是**授权码**，不是登录密码
- [ ] 已在网页版开启 IMAP 服务
- [ ] 授权码未过期（如过期需重新获取）

#### 3. 找不到模块
**错误信息**：
```
ModuleNotFoundError: No module named 'imapclient'
```

**解决**：
```bash
pip install imapclient
```

#### 4. 中文显示乱码
**现象**：邮件主题/发件人显示为乱码

**原因**：Windows终端编码问题

**解决**：
- 使用 VS Code 终端（推荐）
- 或设置 Windows 使用 UTF-8：
  ```cmd
  chcp 65001
  ```

### 调试模式

如需详细调试信息，可在运行脚本前设置环境变量：
```bash
set PYTHONHTTPSVERIFY=0
python scripts/check_mail.py --limit 5
```

## 首次使用提示模板

当检测到用户未配置时，使用以下提示：

```
首次使用139邮箱功能，需要您先完成以下设置：

1. 安装依赖：
   pip install imapclient

2. 登录 https://mail.10086.cn/
3. 进入 设置 → 账户 → IMAP/POP3服务
4. 开启 IMAP/POP3 服务
5. 获取授权码（不是登录密码！）

请提供：
- 139邮箱账号（如 136xxxxxxxxx@139.com）
- 授权码：______
```

## 安全说明

1. **配置文件权限**：配置文件 `config/139mail.conf` 保存时设置权限为 600（仅所有者可读写）
2. **SSL/TLS**：使用兼容模式连接139邮箱。由于139邮箱使用较旧TLS协议，此模式会降低SSL安全性，建议仅在受信任的网络环境中使用。
3. **授权码保护**：授权码仅保存在本地配置文件，不会上传到任何外部服务器。
4. **使用完成后**：如不再使用，建议删除配置文件并撤销邮箱授权码。

## 参考文档

- **IMAP操作指南**：参见 [references/imap_guide.md](references/imap_guide.md)
- **服务器配置**：参见 [references/credentials.md](references/credentials.md)
