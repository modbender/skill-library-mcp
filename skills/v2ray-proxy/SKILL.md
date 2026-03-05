---
name: v2ray-proxy
description: V2Ray代理管理 - 自动开关代理、根据网络状况自动配置系统代理。使用场景：OpenClaw需要访问外网时自动开启代理、不需要时关闭。
---

# V2Ray 代理管理

管理 V2Ray 代理的自动开关，根据网络状况自动配置系统代理。

## 功能

- 🚀 启动/停止 V2Ray
- 🌐 自动配置/清除系统代理
- 🔄 自动模式（根据网络状况自动开关）
- 📊 状态查看和连接测试

## 配置

V2Ray 位置: `/media/felix/d/v2rayN-linux-64/`
代理端口: `10808`

## 使用方式

```bash
# 完整开启代理
bash <skill>/scripts/v2ray-proxy.sh on

# 完整关闭代理
bash <skill>/scripts/v2ray-proxy.sh off

# 自动模式（根据网络状况自动开关）
bash <skill>/scripts/v2ray-proxy.sh auto

# 查看状态
bash <skill>/scripts/v2ray-proxy.sh status

# 测试代理
bash <skill>/scripts/v2ray-proxy.sh test
```

## 命令说明

| 命令 | 说明 |
|------|------|
| `start` | 仅启动 V2Ray |
| `stop` | 仅停止 V2Ray |
| `on` | 启动 + 设置系统代理 |
| `off` | 清除代理 + 停止 |
| `auto` | 自动模式 |
| `status` | 查看状态 |
| `test` | 测试连接 |

## 自动代理工作流

1. 当 OpenClaw 需要访问外网（如搜索、API调用）
2. 执行 `auto` 或 `on` 开启代理
3. 访问完成后执行 `off` 关闭代理

## 开机自启

V2Ray 可以设置开机自启，但代理开关由本脚本控制：

```bash
# 添加到开机启动（可选）
# 编辑 /etc/rc.local 或使用 systemd
```
