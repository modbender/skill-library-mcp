# ZeroTier Remote Web Access Skill

利用 ZeroTier 实现 OpenClaw 远程 WEB 访问的技能。

## 功能

- ✅ 检查 ZeroTier 网络状态
- ✅ 自动配置 OpenClaw Gateway 绑定到 ZeroTier IP
- ✅ 一键启用/禁用远程访问
- ✅ 提供恢复备份功能

## 使用场景

当用户需要：
- 在公司或外面远程访问家里的 OpenClaw
- 通过网页 Control UI 远程管理 OpenClaw
- 不暴露公网 IP 的情况下实现安全远程访问

## 前提条件

1. **ZeroTier 已安装并运行**
   ```bash
   # 检查服务状态
   systemctl status zerotier-one
   
   # 如果未安装
   curl https://install.zerotier.com | sudo bash
   ```

2. **已加入 ZeroTier 网络**
   ```bash
   # 加入网络 (需要 Network ID)
   sudo zerotier-cli join <Network-ID>
   
   # 在 zerotier.com 网页授权设备
   ```

3. **获取 ZeroTier IP**
   ```bash
   # 查看分配的 IP
   ip addr show | grep -A 2 "zt"
   # 或
   zerotier-cli listnetworks
   ```

## 使用方法

### 1. 检查当前状态

```bash
# 运行检查脚本
node ~/.openclaw/workspace/skills/zerotier-remote-web/scripts/check-status.mjs
```

输出示例：
```
✅ ZeroTier 服务：运行中
✅ 网络接口：ztjlhry67z
✅ ZeroTier IP: 10.243.127.213
❌ Gateway 绑定：loopback (仅本地访问)
```

### 2. 启用远程访问

```bash
# 自动配置并重启 Gateway
node ~/.openclaw/workspace/skills/zerotier-remote-web/scripts/enable-remote.mjs
```

脚本会：
1. 备份当前配置 (`openclaw.json.backup-YYYYMMDD-HHMMSS`)
2. 修改 Gateway 配置绑定到 `0.0.0.0`（所有网络接口）
3. 重启 Gateway 服务
4. 验证配置是否生效

### 3. 禁用远程访问（恢复本地）

```bash
# 恢复到本地绑定
node ~/.openclaw/workspace/skills/zerotier-remote-web/scripts/disable-remote.mjs
```

### 4. 从备份恢复

```bash
# 列出所有备份
ls -la ~/.openclaw/openclaw.json.backup-*

# 恢复到指定备份
cp ~/.openclaw/openclaw.json.backup-20260304-152800 ~/.openclaw/openclaw.json
pkill -f openclaw-gateway
nohup openclaw gateway > /tmp/openclaw-gateway.log 2>&1 &
```

## 远程访问方法

### 从远程设备访问

1. **远程设备安装 ZeroTier**
   - 手机/电脑都要安装 ZeroTier 客户端
   - 加入同一个 Network ID
   - 在 zerotier.com 授权设备

2. **访问 Control UI**
   ```
   # 本地访问
   http://localhost:1880
   
   # SSH 登录后访问
   http://<服务器内网 IP>:1880
   
   # 远程 ZeroTier 访问
   http://<ZeroTier-IP>:1880
   例如：http://10.243.127.213:1880
   ```

3. **输入 Token 连接**
   - Token 在 `~/.openclaw/openclaw.json` 的 `gateway.auth.token` 字段

## 配置文件说明

修改后的 `~/.openclaw/openclaw.json` Gateway 配置：

```json
"gateway": {
  "port": 1880,
  "mode": "local",
  "bind": "custom",
  "customBindHost": "0.0.0.0",
  "controlUi": {
    "allowedOrigins": [
      "http://localhost:1880",
      "http://127.0.0.1:1880",
      "http://10.243.127.213:1880"
    ],
    "allowInsecureAuth": true,
    "dangerouslyDisableDeviceAuth": true
  },
  "auth": {
    "mode": "token",
    "token": "your-token-here"
  }
}
```

### 关键字段说明

| 字段 | 说明 |
|------|------|
| `bind: "custom"` | 使用自定义绑定地址 |
| `customBindHost` | `0.0.0.0` 绑定所有网络接口（推荐） |
| `port` | Gateway 端口 (默认 1880) |
| `allowedOrigins` | 允许的访问来源 |

## 故障排查

### 问题 1: ZeroTier 服务未运行
```bash
systemctl start zerotier-one
systemctl enable zerotier-one
```

### 问题 2: 设备未授权
- 登录 zerotier.com
- 找到你的网络
- 勾选 "Auth?" 授权新设备

### 问题 3: Gateway 无法启动
```bash
# 查看日志
tail -50 /tmp/openclaw-gateway.log

# 检查端口占用
ss -tlnp | grep 1880

# 手动启动测试
openclaw gateway --port 1880
```

### 问题 4: 远程无法连接
```bash
# 检查 ZeroTier 连接
zerotier-cli listnetworks

# 检查防火墙
sudo ufw allow 9993/udp  # ZeroTier 端口
sudo ufw allow 1880/tcp  # Gateway 端口

# 测试连通性
ping <ZeroTier-IP>
```

## 安全注意事项

⚠️ **重要**:
- ZeroTier 网络 ID 和 Token 不要公开分享
- 只在可信设备上安装 ZeroTier 客户端
- 定期备份配置文件
- 如果不再需要远程访问，及时禁用

## 文件结构

```
~/.openclaw/workspace/skills/zerotier-remote-web/
├── SKILL.md              # 本文档
└── scripts/
    ├── check-status.mjs  # 检查状态脚本
    ├── enable-remote.mjs # 启用远程访问
    └── disable-remote.mjs # 禁用远程访问
```

## 相关资源

- ZeroTier 官网：https://zerotier.com
- ZeroTier 文档：https://zerotier.atlassian.net/wiki/
- OpenClaw 文档：https://docs.openclaw.ai

---

**版本**: 1.0.0  
**创建日期**: 2026-03-04  
**作者**: 妞子 🌸
