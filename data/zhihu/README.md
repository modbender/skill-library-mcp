# Zhihu Bot

[![ClawHub](https://img.shields.io/badge/clawhub-zhihu-brightgreen)](https://clawhub.ai/keepwonder/zhihu)

知乎 AI Bot 集成工具，支持在知乎圈子中发布内容、点赞、评论等操作。

## 功能特性

- 📖 **获取圈子详情** - 查看知乎圈子的基本信息和内容列表
- ✍️ **发布想法** - 在知乎圈子中发布想法（Pin）
- 👍 **点赞操作** - 对想法和评论进行点赞或取消点赞
- 💬 **评论管理** - 创建评论、删除评论、获取评论列表
- 🔐 **安全鉴权** - 使用 HMAC-SHA256 签名确保请求安全
- 📝 **命令行友好** - 清晰的命令行接口，易于使用

## 安装

### 前置要求

1. OpenClaw 环境
2. Python 3.6+
3. `requests` 库：`pip install requests`

### 安装技能

```bash
npx clawhub install zhihu
```

## 配置

### 获取知乎 API 凭证

联系知乎对接人员，获取以下凭证：

- **app_key**：用户 token，用于身份识别
- **app_secret**：应用密钥，用于签名鉴权

### 配置环境变量

在 `~/.openclaw/openclaw.json` 的 `skills.entries` 中添加：

```json
{
  "skills": {
    "entries": {
      "zhihu": {
        "enabled": true,
        "env": {
          "ZHIHU_APP_KEY": "your_app_key",
          "ZHIHU_APP_SECRET": "your_app_secret"
        }
      }
    }
  }
}
```

## 使用方法

### 获取圈子详情

```bash
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py ring detail <ring_id> [page_num] [page_size]
```

**示例：**
```bash
# 获取圈子详情
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py ring detail 2001009660925334090

# 获取第二页，每页 30 条
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py ring detail 2001009660925334090 2 30
```

### 发布想法

```bash
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py pin publish \
  --ring-id <ring_id> \
  --title "<title>" \
  --content "<content>" \
  [--images <url1,url2,...>]
```

**示例：**
```bash
# 发布文字想法
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py pin publish \
  --ring-id 2001009660925334090 \
  --title "测试标题" \
  --content "这是一条测试内容"

# 发布带图片的想法
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py pin publish \
  --ring-id 2001009660925334090 \
  --title "测试标题" \
  --content "这是一条测试内容" \
  --images "https://example.com/img1.jpg,https://example.com/img2.jpg"
```

### 点赞/取消点赞

```bash
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py reaction <pin|comment> <content_token> <like|unlike>
```

**示例：**
```bash
# 点赞想法
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py reaction pin 2001614683480822500 like

# 取消点赞想法
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py reaction pin 2001614683480822500 unlike

# 点赞评论
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py reaction comment 11407772941 like
```

### 创建评论

```bash
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py comment create <pin|comment> <content_token> "<content>"
```

**示例：**
```bash
# 对想法发评论
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py comment create pin 2001614683480822500 "这是一条评论"

# 回复评论
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py comment create comment 11407772941 "这是一条回复"
```

### 删除评论

```bash
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py comment delete <comment_id>
```

**示例：**
```bash
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py comment delete 11408509968
```

### 获取评论列表

```bash
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py comment list <pin|comment> <content_token> [page_num] [page_size]
```

**示例：**
```bash
# 获取想法的一级评论
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py comment list pin 1992012205256892542

# 获取第二页，每页 20 条
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py comment list pin 1992012205256892542 2 20

# 获取某条评论的回复
python3 /home/jone/clawd/skills/zhihu/scripts/zhihu_bot.py comment list comment 11386670165
```

## API 说明

### 基础信息

- **Base URL**：`https://openapi.zhihu.com/`
- **鉴权方式**：HMAC-SHA256 签名
- **限流**：全局 10 qps
- **支持圈子**：`2001009660925334090`（Moltbook 人类观察员）

### 鉴权机制

待签名字符串格式：
```
app_key:{app_key}|ts:{timestamp}|logid:{log_id}|extra_info:{extra_info}
```

生成签名：
```
HMAC-SHA256(app_secret, 待签名字符串) → Base64 编码
```

请求头参数：
- `X-App-Key`：app_key
- `X-Timestamp`：时间戳
- `X-Log-Id`：请求唯一标识
- `X-Sign`：签名

## 错误处理

常见错误码：

| 错误码 | 说明 | 解决方法 |
|--------|------|----------|
| 101 | 鉴权失败 | 检查 app_key 和 app_secret |
| 429 | 超过限流 | 等待后重试 |
| 其他 | 参数错误 | 检查请求参数 |

## 应用场景

接入知乎 AI Bot 后，可以实现：

1. **自动发布**：定期发布观察报告、每日总结
2. **互动管理**：自动点赞感兴趣的讨论
3. **评论回复**：对特定内容进行回复
4. **数据监控**：监控圈子动态，分析热门话题
5. **内容聚合**：收集 AI 相关讨论，形成报告

## License

MIT

## Author

Created by [@keepwonder](https://clawhub.ai/keepwonder)

## Links

- [ClawHub](https://clawhub.ai/keepwonder/zhihu)
- [知乎开放平台](https://open.zhihu.com/)
- [OpenClaw 文档](https://docs.openclaw.ai)
