# Feishu Suite Skill / 飞书套件技能

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

### Overview
A comprehensive Feishu (Lark) integration suite for OpenClaw, enabling AI agents to interact with messages, documents, spreadsheets, bitables, and organizational structures.

### Privacy Notice
This project uses the identifier `wilsonsliu` for all configurations. Real names must not be committed to version control.

### Installation
1. Ensure dependencies are built:
   ```bash
   cd lib/feishu-client && npm install && npm run build
   cd ../feishu-utils && npm install && npm run build
   ```
2. Install and build the skill:
   ```bash
   cd skills/feishu && npm install && npm run build
   ```

### Permissions Management
The skill uses two configuration files located in this directory to manage access:
- `feishu_base_permissions.json`: Currently active and verified permissions.
- `feishu_additional_permissions.json`: Required permissions that may need enterprise-level approval. If these are not granted, the skill will automatically downgrade and disable related features.

### Configuration
Set the following environment variables:
- `FEISHU_APP_ID`: Your Feishu App ID.
- `FEISHU_APP_SECRET`: Your Feishu App Secret.

---

<a name="chinese"></a>
## 中文

### 概述
这是一个为 OpenClaw 设计的飞书 (Lark) 综合集成套件，使 AI Agent 能够处理消息、文档、电子表格、多维表格以及组织架构。

### 隐私提示
本项目统一使用 `wilsonsliu` 作为标识。请勿将真实姓名提交至版本控制系统。

### 安装步骤
1. 确保依赖库已编译：
   ```bash
   cd lib/feishu-client && npm install && npm run build
   cd ../feishu-utils && npm install && npm run build
   ```
2. 安装并构建技能：
   ```bash
   cd skills/feishu && npm install && npm run build
   ```

### 权限管理
本技能通过同目录下的两个 JSON 文件管理权限：
- `feishu_base_permissions.json`: 当前已验证且可用的基础权限。
- `feishu_additional_permissions.json`: 完整功能所需的额外权限（需视企业策略申请）。若未申请，技能将自动执行功能降级，关闭相关接口调用。

### 配置
请设置以下环境变量：
- `FEISHU_APP_ID`: 飞书应用 ID。
- `FEISHU_APP_SECRET`: 飞书应用密钥。

---
*Maintained by wilsonsliu*
