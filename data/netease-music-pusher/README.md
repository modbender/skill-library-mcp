# 网易云音乐推送技能

> 一键获取网易云每日推荐，支持验证码登录获取个性化内容

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install cryptography
```

### 2. 首次登录

```bash
cd /root/.openclaw/workspace

# Step 1: 发送验证码
python3 skills/netease-music-pusher/scripts/netease_client.py send_captcha 17651730816

# Step 2: 收到验证码后登录（把7725换成你收到的验证码）
python3 skills/netease-music-pusher/scripts/netease_client.py login 17651730816 7725
```

### 3. 获取日推

```bash
# 获取个性化日推
python3 skills/netease-music-pusher/scripts/netease_client.py daily
```

输出示例：
```
🎵 网易云日推
📅 02月18日
💝 专属于你的每日推荐
========================================

 1. Yellow
    🎤 Coldplay
    💿 Yellow
    💡 昨日十万播放
    🔗 https://music.163.com/song?id=17177324

 2. 春的女孩
    🎤 生石灰拌蛋1.0
    💿 春的女孩
    💡 超85%人播放
    🔗 https://music.163.com/song?id=2071222896

 9. The Winner Is
    🎤 Mychael Danna
    💿 Little Miss Sunshine
    🏷️ 电影《阳光小美女》最热配乐
    🔗 https://music.163.com/song?id=3038433

...
```

### 推送内容说明

| 信息 | 说明 |
|------|------|
| 🎤 歌手 | 演唱者名称 |
| 💿 专辑 | 所属专辑 |
| 💡 推荐理由 | 热度指标（如"十万红心"、"超85%人播放"）|
| 🏷️ 别名标签 | 歌曲别名或场景标注 |
| 🔗 歌曲链接 | 点击直达网易云音乐 |

**关于风格标签**: 网易云API对歌曲风格标签的支持有限，当前通过推荐理由和别名标签来反映歌曲特点和热度。

## 📋 命令说明

### netease_client.py

| 命令 | 说明 | 示例 |
|------|------|------|
| `send_captcha <手机号>` | 发送验证码 | `send_captcha 17651730816` |
| `login <手机号> <验证码>` | 验证码登录 | `login 17651730816 7725` |
| `daily` | 获取日推 | `daily` |
| `status` | 检查登录状态 | `status` |

### netease_public_api.py（无需登录）

| 命令 | 说明 |
|------|------|
| `daily` | 获取飙升榜 |
| `飙升榜` | 飙升榜 |
| `新歌榜` | 新歌榜 |
| `原创榜` | 原创榜 |
| `热歌榜` | 热歌榜 |

## ⏰ 配置定时推送

### OpenClaw定时任务

```bash
# 查看当前任务
openclaw cron list

# 添加网易云日推任务（每天8:00推送）
openclaw cron add \
  --name "网易云日推" \
  --schedule "0 8 * * *" \
  --command "python3 skills/netease-music-pusher/scripts/netease_client.py daily"
```

或使用cron工具：

```bash
# 添加任务（北京时间每天8:00）
curl -X POST "http://localhost:8000/cron/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "网易云日推推送",
    "schedule": "0 8 * * *",
    "timezone": "Asia/Shanghai",
    "command": "cd /root/.openclaw/workspace && python3 skills/netease-music-pusher/scripts/netease_client.py daily"
  }'
```

## 🔧 技术实现

### 登录流程

```
1. 发送验证码
   POST /weapi/sms/captcha/sent
   { cellphone: "手机号", ctcode: "86" }
   
2. 验证码登录
   POST /weapi/login/cellphone
   { phone: "手机号", captcha: "验证码", countrycode: "86" }
   
3. 保存Cookies → secrets/netease_cookies.json
```

### 日推接口

```
POST /weapi/v1/discovery/recommend/songs
Headers: Cookies (MUSIC_U, __csrf等)
返回: { code: 200, data: { dailySongs: [...] } }
```

### 加密算法

网易云API使用两层加密：

```python
# 1. AES-CBC加密（两次）
text = json.dumps(params)
enc1 = AES.encrypt(text, NONCE)  # 固定密钥
enc2 = AES.encrypt(enc1, secKey) # 随机密钥

# 2. RSA加密随机密钥
encSecKey = RSA.encrypt(secKey, PUBKEY, MODULUS)

# 3. 发送
POST data: { params: enc2, encSecKey: encSecKey }
```

## 📁 文件结构

```
skills/netease-music-pusher/
├── SKILL.md                    # 技能说明
├── README.md                   # 本文件
└── scripts/
    ├── netease_client.py      # 主客户端（登录+日推）
    └── netease_public_api.py  # 公开榜单API
```

## ⚠️ 注意事项

1. **登录有效期**: Cookies通常7-30天有效，过期后需要重新登录
2. **验证码频率**: 不要频繁发送验证码，避免触发风控
3. **账号安全**: 验证码登录比密码登录更安全，不存储敏感信息
4. **网络要求**: 需要能访问网易云音乐域名（music.163.com）

## 🔍 故障排查

### 验证码收不到

- 检查手机号是否正确
- 等待2-3分钟后重试
- 检查手机短信拦截设置

### 登录失败

- 验证码是否正确（区分大小写）
- 验证码是否过期（5分钟有效）
- 检查网络连接

### 日推获取失败

- 检查登录状态: `python3 scripts/netease_client.py status`
- 如已过期，重新执行登录流程

### 风格标签缺失

**现象**: 推送中缺少歌曲风格标签

**原因**: 网易云官方API对歌曲风格标签的支持有限，大部分歌曲不返回风格字段

**当前替代方案**:
- 推荐理由（如"十万红心"、"超85%人播放"）反映歌曲热度
- 别名标签（如"电影《阳光小美女》最热配乐"）标注特殊场景

**技术限制**: 已通过多种API接口测试，包括歌曲详情、歌单信息、歌手信息等，均无法稳定获取风格标签

## 📝 更新计划

- [ ] 支持多账号切换
- [ ] 支持歌单推送
- [ ] 支持歌曲搜索
- [ ] 支持歌词获取

## 📄 License

MIT
