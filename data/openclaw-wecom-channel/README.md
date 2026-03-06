# 企业微信 (WeCom) Channel 插件

企业微信是企业内部沟通协作平台。本插件将 OpenClaw 连接到企业微信自建应用，通过 HTTP 回调接收消息，通过 API 发送消息。

---

## 需要安装插件

将插件克隆到 OpenClaw extensions 目录：

```bash
git clone https://github.com/darrryZ/openclaw-wecom-channel.git ~/.openclaw/extensions/wecom
```

或手动复制：

```bash
mkdir -p ~/.openclaw/extensions/wecom
cp -r . ~/.openclaw/extensions/wecom/
```

---

## 快速开始

有两种方式添加企业微信 Channel：

### 方式一：CLI 设置（推荐）

```bash
openclaw channels add
```

选择 **WeCom**，然后按提示输入企业 ID、应用 Secret 等信息。

✅ **配置完成后**，管理 Gateway：

- `openclaw gateway status`
- `openclaw gateway restart`
- `openclaw logs --follow`

### 方式二：手动编辑配置文件

参见下方 [Step 2: 配置 OpenClaw](#step-2-配置-openclaw)。

---

## Step 1: 创建企业微信应用

### 1. 登录企业微信管理后台

访问 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame) 并登录。

### 2. 获取企业 ID

进入 **我的企业** → **企业信息**，复制 **企业 ID**（格式：`wwxxxxxxxxxx`）。

### 3. 创建自建应用

进入 **应用管理** → **自建** → **创建应用**：

1. 填写应用名称和描述
2. 选择可见范围（建议先选自己测试）
3. 创建后进入应用详情页

### 4. 获取应用凭证

在应用详情页复制：

- **AgentId** — 应用 ID（数字格式，如 `1000003`）
- **Secret** — 应用密钥

❗ **重要：** Secret 请妥善保管，不要泄露。

### 5. 配置接收消息

在应用详情页 → **接收消息** → **设置 API 接收**：

1. **URL**: `https://你的域名/wecom/callback`（需公网可达，见 [公网访问](#公网访问)）
2. **Token**: 点击随机生成，复制保存
3. **EncodingAESKey**: 点击随机生成，复制保存
4. 点击保存（此时 Gateway 必须已启动，否则验证会失败）

### 6. 配置可信 IP

在应用详情页 → **企业可信IP**：

添加你的服务器公网 IP。如果使用家庭宽带，IP 可能会变化，需要及时更新。

> 💡 **提示：** 可以通过 `curl ifconfig.me` 查询当前公网 IP。

---

## Step 2: 配置 OpenClaw

### 通过配置文件

编辑 `~/.openclaw/openclaw.json`：

```json5
{
  channels: {
    wecom: {
      enabled: true,
      corpId: "wwxxxxxxxxxx",       // 企业 ID
      agentId: 1000003,              // 应用 AgentId
      secret: "你的应用Secret",       // 应用 Secret
      token: "回调Token",             // 接收消息 Token
      encodingAESKey: "回调AESKey",   // 接收消息 EncodingAESKey
      port: 18800,                    // 回调监听端口
      dmPolicy: "open"               // 访问策略
    }
  },
  plugins: {
    entries: {
      wecom: { enabled: true }
    }
  }
}
```

### 通过环境变量

```bash
export WECOM_CORP_ID="wwxxxxxxxxxx"
export WECOM_AGENT_ID="1000003"
export WECOM_SECRET="你的应用Secret"
export WECOM_TOKEN="回调Token"
export WECOM_ENCODING_AES_KEY="回调AESKey"
```

---

## 公网访问

企业微信回调需要公网可达的 HTTPS URL。推荐使用 **Cloudflare Tunnel**（免费）：

```bash
# 安装 cloudflared
brew install cloudflared    # macOS
# 或 apt install cloudflared  # Linux

# 登录 Cloudflare
cloudflared tunnel login

# 创建 tunnel
cloudflared tunnel create wecom-tunnel

# 配置 DNS（将子域名指向 tunnel）
cloudflared tunnel route dns wecom-tunnel wecom.yourdomain.com

# 启动 tunnel
cloudflared tunnel run --url http://localhost:18800 wecom-tunnel
```

> ⚠️ **ClashX / 代理用户注意：** 如果使用 ClashX 等代理工具，需要添加参数避免 fake-ip 干扰：
>
> ```bash
> cloudflared tunnel run --edge-ip-version 4 --edge-bind-address 0.0.0.0 \
>   --url http://localhost:18800 wecom-tunnel
> ```

然后在企业微信后台设置回调 URL 为 `https://wecom.yourdomain.com/wecom/callback`。

### 其他公网方案

- **ngrok**: `ngrok http 18800`
- **frp**: 自建内网穿透
- **云服务器**: 直接部署

---

## Step 3: 启动 + 测试

### 1. 启动 Gateway

```bash
openclaw gateway restart
```

### 2. 发送测试消息

在企业微信中找到你的应用，发送一条消息。

### 3. 查看日志

```bash
openclaw logs --follow
```

如果一切正常，你应该能看到消息接收和回复的日志。

---

## 概览

- **企业微信 Channel**: 通过自建应用与企业微信通信
- **HTTP 回调**: 接收消息通过 HTTP POST 回调
- **主动推送**: 发送消息通过企业微信 API
- **消息加解密**: 完整实现 WXBizMsgCrypt 标准（AES-256-CBC + PKCS7）
- **智能回复**: 5 秒内被动回复，超时自动降级为主动推送

---

## 访问控制

### 私聊策略（dmPolicy）

| 值 | 行为 |
|---|---|
| `"open"` | **允许所有用户**（默认） |
| `"pairing"` | 未知用户需要配对码，需管理员批准 |
| `"allowlist"` | 仅白名单用户可使用 |

### 配对模式

```bash
# 查看待批准的配对请求
openclaw pairing list wecom

# 批准配对
openclaw pairing approve wecom <CODE>
```

### 白名单模式

```json5
{
  channels: {
    wecom: {
      dmPolicy: "allowlist",
      allowFrom: ["userId1", "userId2"]
    }
  }
}
```

---

## 配置项参考

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `enabled` | ❌ | 启用/禁用 Channel | `true` |
| `corpId` | ✅ | 企业微信企业 ID | - |
| `agentId` | ✅ | 自建应用 Agent ID | - |
| `secret` | ✅ | 自建应用 Secret | - |
| `token` | ✅ | 接收消息回调 Token | - |
| `encodingAESKey` | ✅ | 接收消息回调 EncodingAESKey | - |
| `port` | ✅ | 回调监听端口 | - |
| `dmPolicy` | ❌ | 访问策略 | `"open"` |
| `allowFrom` | ❌ | 白名单用户列表 | - |

---

## 常用命令

在企业微信中发送：

| 命令 | 说明 |
|------|------|
| `/status` | 查看 Agent 状态 |
| `/reset` | 重置会话 |
| `/model` | 查看/切换模型 |

> 注意：企业微信不支持原生命令菜单，需以文本形式发送。

### Gateway 管理

| 命令 | 说明 |
|------|------|
| `openclaw gateway status` | 查看 Gateway 状态 |
| `openclaw gateway restart` | 重启 Gateway |
| `openclaw logs --follow` | 实时查看日志 |

---

## 项目结构

```
├── index.ts              # 插件入口
├── package.json
├── openclaw.plugin.json
├── SKILL.md              # ClawHub Skill 描述
├── LICENSE               # MIT License
└── src/
    ├── channel.ts        # ChannelPlugin 定义（配置、路由、能力声明）
    ├── bot.ts            # HTTP 回调服务（签名验证、消息解析、分发）
    ├── crypto.ts         # AES-256-CBC 消息加解密
    ├── token.ts          # access_token 获取与缓存
    ├── send.ts           # 主动发送消息
    ├── outbound.ts       # 出站消息处理
    ├── reply-dispatcher.ts # 被动回复调度（5秒超时降级为主动推送）
    ├── accounts.ts       # 账户解析
    ├── monitor.ts        # 服务生命周期管理
    ├── runtime.ts        # 运行时上下文
    └── types.ts          # 类型定义
```

---

## 技术细节

### 被动回复 vs 主动推送

企业微信要求回调请求在 **5 秒内** 响应。插件实现了智能回复机制：

1. 收到消息后启动 5 秒计时器
2. 如果 Agent 在 5 秒内生成回复 → 被动回复（XML 格式）
3. 如果超时 → 先返回空响应，再通过 API 主动推送

### 消息加解密

完整实现企业微信 `WXBizMsgCrypt` 标准：

- 加密：AES-256-CBC + PKCS7 填充 + 签名
- 解密：签名验证 + AES-256-CBC 解密 + PKCS7 去填充
- 随机 16 字节 nonce + 4 字节消息长度 + 明文 + CorpID

### Token 管理

- access_token 缓存在内存
- 提前 5 分钟自动刷新
- 失败自动重试

---

## 故障排查

### Agent 不回复消息

1. 确认 Gateway 正在运行：`openclaw gateway status`
2. 确认回调 URL 可达：`curl https://wecom.yourdomain.com/wecom/callback`
3. 检查企业可信 IP 是否正确
4. 查看日志：`openclaw logs --follow`

### 回调验证失败

1. 确认 Token 和 EncodingAESKey 与企业微信后台一致
2. 确认 Gateway 在保存回调配置**之前**已启动
3. 确认 Cloudflare Tunnel 正在运行

### 消息发送失败（IP 白名单）

企业微信要求发送消息的服务器 IP 在可信列表中：

1. 查询当前公网 IP：`curl ifconfig.me`
2. 在企业微信管理后台更新可信 IP
3. 如果使用家庭宽带，IP 可能定期变化，需注意更新

### Secret 泄露

1. 在企业微信管理后台重置 Secret
2. 更新 OpenClaw 配置
3. 重启 Gateway：`openclaw gateway restart`

---

## 当前限制

- 仅支持 **文本消息**（图片/文件/语音待后续支持）
- 仅支持 **单聊**（群聊待后续支持）
- 不支持 reactions、threads、polls
- 不支持 streaming（流式输出）

---

## License

MIT

---

## 相关链接

- [OpenClaw](https://github.com/openclaw/openclaw) — AI Agent 框架
- [OpenClaw 文档](https://docs.openclaw.ai)
- [企业微信开发文档](https://developer.work.weixin.qq.com/document/)
- [ClawHub](https://clawhub.com) — OpenClaw Skill 市场
