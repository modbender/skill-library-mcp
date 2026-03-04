# Gateway Schema（网关配置）

## 基础配置

```json5
{
  gateway: {
    port: 18789,
    mode: "local",
    bind: "loopback",
    auth: {
      mode: "token",
      token: "c91c184aabe5ac6bb4e11de46770dbf10ae9e2636cbd771e",
    },
    reload: {
      mode: "hybrid",
    },
  }
}
```

### 核心字段

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `port` | number | `1024` - `65535` | `18789` | 监听端口 |
| `mode` | string | `local` \| `remote` \| `tunnel` | `local` | 运行模式 |
| `bind` | string | `loopback` \| `lan` \| `tailnet` \| `any` | `loopback` | 绑定地址 |
| `auth.mode` | string | `token` \| `password` \| `none` | `token` | 认证模式 |
| `auth.token` | string | 任意字符串 | - | 认证令牌 |
| `reload.mode` | string | `hybrid` \| `hot` \| `restart` \| `off` | `hybrid` | 热重载模式 |

### Bind 有效值详解

| 值 | 说明 |
|---|---|
| `loopback` | 仅本地回环 (127.0.0.1) |
| `lan` | 局域网 (0.0.0.0) |
| `tailnet` | Tailscale 网络 |
| `any` | 所有接口 |

### Reload Mode 详解

| 模式 | 说明 |
|---|---|
| `hybrid` | 安全更改热应用，关键更改重启（默认） |
| `hot` | 仅热应用安全更改 |
| `restart` | 任何更改都重启 |
| `off` | 禁用热重载 |

---

## Tailscale 配置

```json5
{
  gateway: {
    tailscale: {
      mode: "off",
      resetOnExit: false,
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `mode` | string | `off` \| `serve` \| `funnel` | `off` | Tailscale 模式 |
| `resetOnExit` | boolean | `true` \| `false` | `false` | 退出时重置 |

### Tailscale Mode 详解

| 模式 | 说明 |
|---|---|
| `off` | 禁用 Tailscale |
| `serve` | Tailscale Serve（私有网络） |
| `funnel` | Tailscale Funnel（公开访问） |

---

## Nodes 配置

```json5
{
  gateway: {
    nodes: {
      denyCommands: [
        "camera.snap",
        "camera.clip",
        "screen.record",
      ],
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `denyCommands` | array | 命令列表 | `[]` | 禁止的命令 |

### 常见禁止命令

| 命令 | 说明 |
|---|---|
| `camera.snap` | 相机拍照 |
| `camera.clip` | 相机录像 |
| `screen.record` | 屏幕录制 |
| `calendar.add` | 添加日历事件 |
| `contacts.add` | 添加联系人 |
| `reminders.add` | 添加提醒 |

---

## Canvas Host 配置

```json5
{
  gateway: {
    canvasHost: {
      enabled: true,
      port: 18793,
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `enabled` | boolean | `true` \| `false` | `true` | 启用 Canvas 服务 |
| `port` | number | `1024` - `65535` | `18793` | Canvas 端口 |

---

## 常见错误

| 错误 | 原因 | 修复 |
|---|---|---|
| `"port": "18789"` | 类型错误（应为 number） | 改为 `18789` |
| `"bind": "localhost"` | 不是有效枚举值 | 改为 `loopback` |
| `"reload.mode": "auto"` | 不是有效枚举值 | 改为 `hybrid` |
| `"tailscale.mode": "on"` | 不是有效枚举值 | 改为 `serve` \| `funnel` |
| 端口超出范围 | `port: 99999` | 改为 `1024` - `65535` 之间 |

---

## 官方文档

- https://docs.openclaw.ai/gateway/configuration-reference#gateway
- https://docs.openclaw.ai/zh-CN/gateway/index
