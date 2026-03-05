# 🦞 ClawHub.ai 发布指南

## 快速发布（推荐）

由于环境限制，建议使用 **网站直接发布** 方式。

### 步骤 1: 访问 ClawHub 发布页面

打开浏览器访问：https://clawhub.ai/skills/publish

### 步骤 2: 登录账号

使用你的账号登录（GitHub 账号或邮箱注册）

**账号信息**: Sunnyfo

### 步骤 3: 填写发布信息

复制以下内容到 ClawHub 发布表单：

#### 基本信息
| 字段 | 填写内容 |
|------|----------|
| **Name** | `sina-stock` |
| **Display Name** | `Sina Stock - A 股实时行情` |
| **Description** | `获取 A 股实时股票行情数据（上证指数、深证成指、创业板指等），使用新浪财经 API。无需 API Key。` |
| **Version** | `1.0.0` |
| **Category** | `Finance` |
| **License** | `MIT` |
| **Icon** | 📈 |

#### 标签 (Tags)
```
stock, finance, A 股，行情，股票，中国，新浪财经，上证指数，深证成指
```

#### GitHub 仓库
```
https://github.com/Sunnyfo/sina-stock
```

### 步骤 4: 上传配置文件

上传 `clawhub.yaml` 文件内容：

```yaml
---
name: sina-stock
version: 1.0.0
description: 获取 A 股实时股票行情数据（上证指数、深证成指、创业板指等），使用新浪财经 API。无需 API Key。
author: Sunnyfo
license: MIT
category: finance
tags:
  - stock
  - finance
  - A 股
  - 行情
  - 股票
  - 中国
entry:
  type: script
  path: scripts/get_stock.py
  interpreter: python3
```

### 步骤 5: 提交审核

点击 **Submit for Review** 按钮

审核时间：1-3 个工作日

---

## 📋 发布检查清单

提交前确认：

- [x] GitHub 仓库已公开（https://github.com/Sunnyfo/sina-stock）
- [x] README.md 已包含使用说明
- [x] SKILL.md 已包含详细文档
- [x] clawhub.yaml 配置正确
- [x] 代码可以正常运行
- [ ] ClawHub 表单已填写完整
- [ ] 已点击提交审核

---

## 🔍 审核后

审核通过后：
1. 你会收到邮件通知
2. Skill 会在 ClawHub 上线
3. 用户可以通过 `skill install sina-stock` 安装

---

## 💡 提示

- 确保 GitHub 仓库是 **Public**（公开）
- 审核期间保持仓库可访问
- 如有问题，ClawHub 团队会通过邮件联系你

---

**祝发布顺利！** 🎉
