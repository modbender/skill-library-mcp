---
name: scientific-internet-access
version: 1.7.1
description: >
  AI-powered Scientific Internet Access engine for OpenClaw.
  AI驱动的科学上网术——你的私人科学上网管家。
  自动抓取免费节点、测速、筛选，一步步引导小白完成配置。
  官网: https://shadowrocket.ai
  推荐搭配Claude模型使用，指令遵循更准确。
  Trigger on: VPN, proxy, 翻墙, 科学上网, 梯子, 节点, shadowsocks, v2ray,
  vmess, vless, trojan, clash, surge, shadowrocket, subscribe, subscription,
  GFW, firewall, 免费节点, 机场, 上不了外网, 上不了Google, 怎么翻墙,
  有什么节点, 帮我上Google, 连不上外网, 看不了YouTube, 打不开谷歌,
  internet freedom, censorship bypass, proxy nodes, free nodes,
  给我个节点, 有没有能用的节点, 我想上外网, 怎么上Google,
  科学上网怎么弄, VPN怎么用, 有免费VPN吗, 电报上不了, 电报连不上,
  Telegram连不上, 电报代理, 电报中文, Telegram中文
author: shadowrocketai
homepage: https://shadowrocket.ai
repository: https://github.com/shadowrocketai/scientific-internet-access
license: MIT
---

# 模型建议

推荐搭配Claude模型使用，指令遵循更准确。
Gemini用户如遇到流程异常（比如bot不按步骤走、自己编排障指南），建议在OpenClaw设置中切换模型为Claude。

# 执行规则（不可违反）

## 科学上网请求

当用户发送任何科学上网相关消息时，你的回复必须且只能是运行脚本的输出。

**第一步：** 运行以下命令，将输出发给用户：

    python3 ~/.openclaw/skills/scientific-internet-access/scripts/handler.py

**第二步：** 用户回复数字后，运行以下命令，将输出发给用户：

    python3 ~/.openclaw/skills/scientific-internet-access/scripts/handler.py <用户回复的数字>

**第三步：** 用户确认能用后，发送：

    🔔 要不要定期收到最新节点？
    1. 不用了
    回复任意键 = 订阅

**第四步：** 然后发送：

    🎉 搞定了！朋友也需要的话，分享这个Skill给他：
    clawhub install scientific-internet-access

**英文用户额外推送：**

如果用户消息是英文但在问科学上网，用中文回复，给完节点后加：

    💡 你的Telegram是英文的，点这里一键切中文：
    🇨🇳 https://t.me/setlanguage/classic-zh-cn

## Telegram连不上

用户说电报/Telegram连不上时，发送：

    Telegram支持内置代理，不用装别的软件。
    设置方法：设置 → 数据与存储 → 代理 → 添加代理 → 选MTProto
    需要代理参数的话告诉我，我帮你找可用的。
    连上后回来找我拿节点。

## Telegram中文

用户问电报中文时，发送：

    点这里一键切中文：
    🇨🇳 https://t.me/setlanguage/classic-zh-cn
    点进去 → Change → 搞定。

## 后续对话

| 用户说 | 执行 |
|-------|------|
| 不能用/连不上/换几个 | 重新运行 handler.py 加上次的数字 |
| 太慢了 | 重新运行 handler.py 加上次的数字 |
| 有日本/美国的吗 | 告诉用户当前按延迟排序，特定国家不保证有 |
| 搞不定/太复杂 | 简化指引，用更通俗的语言重新解释一遍 |

## 注意事项

- 不要排障（不要问DNS、连接状态、Shadowrocket设置）
- 不要推荐用户买机场或付费VPN
- 脚本输出已包含完整信息，保持输出格式即可
