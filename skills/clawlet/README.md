# Clawlet - Nostr 智能管家

🦞 Clawlet 是 OpenClaw 的 Nostr 客户端 Skill，让机器人化身为你的 Nostr 贴身管家。

## 功能

- **身份管理** - 生成和管理 Nostr 密钥
- **发布内容** - 发送文本到 Nostr 网络
- **关注管理** - 关注/取关用户
- **时间线** - 读取 Nostr 时间线
- **用户资料** - 查看用户资料
- **AI 筛选** - 根据兴趣筛选时间线内容
- **智能推荐** - 基于兴趣发现值得关注的用户
- **合规过滤** - 过滤敏感内容

## 使用方法

用户对 OpenClaw 说：
- "帮我生成一个 Nostr 身份"
- "发一条消息到 Nostr：今天天气不错"
- "关注 npub1xxx..."
- "看看我的时间线"
- "设置我的兴趣为中医、AI、编程"
- "帮我发现值得关注的用户"

## 安装

### 方法1：直接复制
```bash
cp -r clawlet /root/.openclaw/workspace/skills/
cd /root/.openclaw/workspace/skills/clawlet
npm install
```

### 方法2：ClawHub
```bash
clawlet install clawlet
```

## 配置

支持代理配置：
```bash
export HTTPS_PROXY=http://127.0.0.1:7890
```

## License

MIT
