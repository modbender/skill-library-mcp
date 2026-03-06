# osint-social

[English Version](./README.md)

> OpenClaw Skill，支持在 1000+ 社交媒体平台（含中国大陆平台）查询用户名

基于 [qeeqbox/social-analyzer](https://github.com/qeeqbox/social-analyzer) 的 [OpenClaw](https://openclaw.ai) Skill，整合了全球平台扫描与专属中国平台查询模块（B站、知乎、微博）。

## 功能介绍

直接对 Mon3tr 说自然语言即可触发，例如：

- "帮我查一下用户名 johndoe 在哪些平台有账号"
- "调查用户名 shadowfox99"
- "查一下 testuser，包括国内平台"
- "检查这个用户名在 B站和知乎有没有账号"

自动扫描 1000+ 全球平台及国内主流平台，以自然语言摘要返回结果，不输出原始 JSON。

## 平台覆盖

### 全球平台（via social-analyzer）
- 社交：Twitter/X、Instagram、Facebook、TikTok、Pinterest、Reddit、Tumblr
- 开发者：GitHub、GitLab、Stack Overflow、Dev.to
- 游戏：Steam、Chess.com、Roblox、Twitch
- 音乐：SoundCloud、Bandcamp、Last.fm
- 其他 990+ 平台...

### 中国大陆平台（via cn_lookup.py）

| 平台 | 支持情况 | 可获取信息 |
|------|---------|-----------|
| Bilibili 哔哩哔哩 | ✅ 完整支持 | 用户名、粉丝数、视频数、简介 |
| 知乎 Zhihu | ✅ 完整支持 | 用户名、关注者数、简介 |
| 微博 Weibo | ⚠️ 降级支持 | 存在性检测 + 基本信息 |
| 小红书 / 抖音 | ❌ 不支持 | 需要登录，无公开接口 |

## 安装

```bash
git clone https://github.com/guleguleguru/osint-social.git skills/osint-social
```

或通过 ClawHub 安装：
```bash
clawhub install osint-social
```

## 依赖

- Python 3
- `pip3 install social-analyzer --break-system-packages`
- 无需任何 API Key

## 文件结构

```
osint-social/
├── SKILL.md                    # OpenClaw 主 Skill 文件
├── README.md                   # 英文说明
├── README.zh.md                # 中文说明（本文件）
├── scripts/
│   ├── run_osint.sh            # 全球平台查询脚本
│   └── cn_lookup.py            # 中国平台查询脚本
└── references/
    └── platforms.md            # 平台分类参考
```

## 输出示例

```
找到 5 个账号：

全球平台（social-analyzer）：
• GitHub (rate: 95): github.com/johndoe — 234 followers
• Twitter (rate: 88): twitter.com/johndoe
• Instagram (rate: 82): instagram.com/johndoe — 摄影爱好者

国内平台（cn_lookup）：
• Bilibili [95] ✅ 精确匹配: space.bilibili.com/12345678 — 粉丝: 1,200
• 知乎 [92] ✅ 精确匹配: zhihu.com/people/johndoe — 关注者: 340

⚠️ 以上均为公开信息，请合法合理使用。
```

## 免责声明

本工具仅访问**公开可见的信息**，适用于自我审计、安全研究、新闻调查等合法用途。请勿用于跟踪、骚扰或侵犯他人隐私，使用者需自行遵守所在地区的法律法规。

## 致谢

- 全球平台查询由 [qeeqbox/social-analyzer](https://github.com/qeeqbox/social-analyzer) 驱动
- ClawHub 上第一个 OSINT Skill
- 作者：[@guleguleguru](https://github.com/guleguleguru)
