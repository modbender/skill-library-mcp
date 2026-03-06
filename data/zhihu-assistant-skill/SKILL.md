---
name: zhihu-assistant
description: 知乎热榜抓取与回答草稿生成助手 - 自动抓取知乎热榜，使用 AI 生成优质回答草稿，推送到飞书审核
version: 1.0.0
author: naiveKid
requires:
  - python3
  - pip3
---

# 知乎助手 (Zhihu Assistant)

自动抓取知乎热榜、生成回答草稿并推送到飞书审核的 OpenClaw Skill。

## 功能特性

- ⏰ **定时抓取**：每小时自动抓取知乎热榜前10条
- 🧠 **智能生成**：使用 Kimi AI 生成优质回答草稿
- 📋 **审核队列**：推送到飞书，人工确认后手动发布
- 📝 **记忆去重**：自动过滤已回答过的问题
- 📊 **操作日志**：完整记录所有操作

## 安装

```bash
openclaw skills install zhihu-assistant
```

## 配置

安装后需要配置以下参数：

### 1. 知乎 Cookie（必需）

从浏览器开发者工具复制知乎 Cookie：

1. 登录知乎网页版
2. 按 F12 打开开发者工具 → Network
3. 刷新页面，找到任意请求
4. 复制 Request Headers 中的 Cookie

```bash
openclaw config set skills.zhihu-assistant.zhihu_cookie "your_zhihu_cookie_here"
```

### 2. Kimi API Key（必需）

从 [Kimi 开放平台](https://platform.moonshot.cn/) 获取 API Key：

```bash
openclaw config set skills.zhihu-assistant.kimi_api_key "your_api_key_here"
```

### 3. 飞书用户 ID（可选）

用于接收推送通知：

```bash
openclaw config set skills.zhihu-assistant.feishu_user_id "your_feishu_user_id"
```

### 4. 其他配置（可选）

```bash
# 每次抓取数量（默认10）
openclaw config set skills.zhihu-assistant.fetch_limit 10

# 最小热度过滤，单位万（默认10）
openclaw config set skills.zhihu-assistant.min_heat 10
```

## 使用

### 快捷命令

```bash
# 抓取热榜并生成草稿
openclaw zhihu fetch --limit 10

# 查看统计信息
openclaw zhihu stats

# 推送到飞书
openclaw zhihu notify

# 查看操作日志
openclaw zhihu logs

# 拒绝草稿
openclaw zhihu reject --id P20260301...
```

### 详细说明

#### `openclaw zhihu fetch [--limit N]`

抓取知乎热榜并生成回答草稿。

参数：
- `--limit`：抓取前 N 条热榜（默认 10，最大 50）

#### `openclaw zhihu stats`

查看当前统计信息：
- 已回答问题数
- 待审核数量
- 已批准数量
- 已发布数量
- 已拒绝数量

#### `openclaw zhihu notify`

获取待推送的审核项列表，用于推送到飞书。

#### `openclaw zhihu logs`

查看最近的操作日志（最近 20 条）。

#### `openclaw zhihu reject --id <ID>`

拒绝指定的待审核项。

## 定时任务

安装后会自动创建以下定时任务：

| 任务 | 时间 | 功能 |
|------|------|------|
| zhihu-fetch | 每小时 0 分 | 抓取热榜并生成草稿 |
| zhihu-notify | 每小时 5 分 | 推送待审核项到飞书 |

查看定时任务：
```bash
openclaw cron list
```

## 飞书交互

### 接收推送

系统每小时自动推送待审核项到飞书，格式如下：

```
📋 知乎回答待审核

问题：为什么现在的年轻人都不爱结婚了？
热度：1250万  
链接：https://zhihu.com/question/...

---

回答草稿（800字）：
...

---

待审核ID：P20260301120000_123456

💡 操作方式：
• 复制内容到知乎发布
• 回复 "查看 P20260301..." 查看完整草稿
```

### 查看完整草稿

在飞书中回复：
```
查看 P20260301120000_123456
```

## 项目结构

```
zhihu-assistant/
├── main.py                    # 主程序入口
├── modules/                   # 功能模块
│   ├── __init__.py
│   ├── zhihu_hot.py          # 知乎热榜抓取
│   ├── memory_store.py       # 记忆存储管理
│   ├── content_gen.py        # 内容生成
│   └── feishu_notify.py      # 飞书通知
├── data/                      # 数据存储
│   ├── answered.json         # 已回答问题列表
│   └── pending.json          # 待审核队列
└── logs/                      # 日志文件
    └── app.log               # 应用日志
```

## 注意事项

1. **Cookie 有效期**：知乎 Cookie 会过期，通常 1-3 个月，过期后需要重新获取
2. **API 调用限制**：Kimi API 有速率限制（免费版 20 RPM），请勿频繁调用
3. **内容质量**：AI 生成的内容仅供参考，发布前请人工审核
4. **账号安全**：请勿将 Cookie 和 API Key 提交到代码仓库
5. **合规使用**：遵守知乎社区规范，不要发布违规内容

## 故障排查

### 抓取失败（401 错误）

- 检查 Cookie 是否过期
- 重新从浏览器复制最新 Cookie

### API 调用失败（429 错误）

- 遇到速率限制，系统会自动等待并重试
- 免费版限制 20 请求/分钟，如需更高额度请升级账户

### 飞书推送失败

- 检查 OpenClaw 飞书配置
- 检查目标用户 ID 是否正确

## 更新日志

### v1.0.0 (2026-03-01)

- 初始版本发布
- 支持知乎热榜抓取
- 支持 AI 生成回答草稿
- 支持飞书推送
- 支持审核队列管理

## License

MIT

## 作者

- GitHub: [@naiveKid](https://github.com/naiveKid)
