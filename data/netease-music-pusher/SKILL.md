---
name: 网易云音乐推送技能
description: 自动获取网易云音乐每日推荐并推送，支持验证码登录获取个性化日推。
---

# 网易云音乐推送技能

自动获取网易云音乐每日推荐并推送，支持验证码登录获取个性化日推。

## 功能特性

- ✅ **个性化日推** - 登录后获取专属每日推荐
- ✅ **验证码登录** - 无需密码，短信验证码安全登录
- ✅ **自动Cookie管理** - 登录状态自动保存和恢复
- ✅ **定时推送** - 可配置定时任务自动推送
- ✅ **多榜单支持** - 飙升榜、新歌榜、热歌榜等公开榜单
- ✅ **丰富歌曲信息** - 歌曲链接、推荐理由、别名标签

## 推送内容

每日推送包含以下信息：

| 字段 | 说明 | 示例 |
|------|------|------|
| 歌曲名 | 歌曲标题 | "Yellow" |
| 歌手 | 演唱者 | "Coldplay" |
| 专辑 | 所属专辑 | "Yellow" |
| 歌曲链接 | 网易云直达链接 | `https://music.163.com/song?id=xxx` |
| 推荐理由 | 热度指标 | "十万红心"、"超85%人播放" |
| 别名标签 | 歌曲别名/备注 | "电影《阳光小美女》最热配乐" |

### 关于风格标签

**当前状态**: 网易云官方API对歌曲风格标签的支持有限

**已有信息**:
- 推荐理由（反映歌曲热度）
- alia别名（部分歌曲有电影/场景标注）

**替代方案**: 推荐理由已能很好地反映歌曲的流行程度和用户喜好

## 快速开始

### 1. 安装依赖

```bash
pip3 install cryptography
```

### 2. 登录网易云

```bash
cd /root/.openclaw/workspace

# 发送验证码
python3 skills/netease-music-pusher/scripts/netease_client.py send_captcha <手机号>

# 使用验证码登录
python3 skills/netease-music-pusher/scripts/netease_client.py login <手机号> <验证码>
```

### 3. 获取日推

```bash
# 获取个性化日推（需要登录）
python3 skills/netease-music-pusher/scripts/netease_client.py daily

# 获取公开榜单（无需登录）
python3 skills/netease-music-pusher/scripts/netease_client.py toplist
```

## 配置定时任务

添加OpenClaw定时任务，每天自动推送：

```bash
# 任务配置示例
{
  "name": "网易云日推推送",
  "schedule": "0 8 * * *",
  "command": "python3 skills/netease-music-pusher/scripts/netease_client.py daily"
}
```

## 文件说明

```
netease-music-pusher/
├── SKILL.md                          # 本说明文档
├── scripts/
│   ├── netease_client.py            # 主客户端（支持登录+日推）
│   └── netease_public_api.py        # 公开API（无需登录）
└── README.md                         # 详细使用说明
```

## 技术细节

### 登录流程

1. **发送验证码**
   - 调用 `/weapi/sms/captcha/sent`
   - 网易云发送短信验证码到手机

2. **验证码登录**
   - 调用 `/weapi/login/cellphone`
   - 提交手机号+验证码
   - 成功后获取Cookies

3. **保存登录状态**
   - 保存到 `secrets/netease_cookies.json`
   - 后续自动加载，无需重复登录

### 获取日推

- 接口: `/weapi/v1/discovery/recommend/songs`
- 需要: 登录后的Cookies
- 返回: 每日推荐歌曲列表（通常20-30首）

### 加密算法

网易云API使用自定义加密：
- **AES-CBC**: 两次加密，密钥分别为固定值和随机值
- **RSA**: 加密随机密钥
- **填充**: PKCS7

具体实现见 `netease_client.py` 中的 `NeteaseCrypto` 类。

## 常见问题

### Q: 验证码收不到？
A: 可能原因：
- 手机号输入错误
- 网易云风控限制（短时间内发送次数过多）
- 运营商短信拦截

**解决**: 等待几分钟后重试，或尝试其他时间段。

### Q: 登录过期了？
A: Cookies通常7-30天有效，过期后需要重新登录。

**解决**: 重新执行验证码登录流程。

### Q: 可以密码登录吗？
A: 当前版本仅支持验证码登录，更安全且无需存储密码。

### Q: 二维码登录支持吗？
A: 网易云已限制二维码登录API（返回8821错误），建议使用验证码登录。

## 更新记录

- **2026-02-18** - 初版发布，支持验证码登录和日推获取

## 参考

- 网易云音乐API逆向参考
- `cryptography` 库文档
- OpenClaw定时任务配置
