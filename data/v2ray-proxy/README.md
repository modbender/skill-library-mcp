# OpenClaw V2Ray 代理管理技能

自动管理 V2Ray 代理，根据网络状况自动开关系统代理。

## 功能

- 🚀 启动/停止 V2Ray
- 🌐 自动配置/清除系统代理
- 🔄 自动模式（根据网络状况自动开关）
- 📊 状态查看和连接测试
- 🤖 自动代理包裹命令

## 系统要求

- Linux/macOS
- V2Ray/Xray 已安装
- Bash

## 快速开始

### 1. 配置 V2Ray 路径

编辑 `scripts/v2ray-proxy.sh`，确认 V2Ray 路径：
```bash
V2RAY_DIR="/media/felix/d/v2rayN-linux-64"
```

### 2. 使用命令

```bash
# 开启代理
bash v2ray-proxy.sh on

# 关闭代理
bash v2ray-proxy.sh off

# 自动模式
bash v2ray-proxy.sh auto

# 自动代理包裹命令（自动开关）
bash v2ray-proxy.sh wrap curl https://github.com

# 查看状态
bash v2ray-proxy.sh status
```

## 命令说明

| 命令 | 说明 |
|------|------|
| `on` | 开启代理（启动V2Ray + 系统代理） |
| `off` | 关闭代理（清除系统代理 + 停止） |
| `auto` | 自动模式 |
| `status` | 查看状态 |
| `test` | 测试连接 |
| `check` | 检查网络是否需要代理 |
| `ensure` | 确保代理开启 |
| `wrap <命令>` | 自动代理包裹命令 |

## 自动代理场景

技能会自动检测以下网站是否可访问：
- github.com
- google.com

如果不可访问，自动开启代理。

## 使用示例

```bash
# 访问 GitHub（自动开关代理）
./scripts/v2ray-proxy.sh wrap git clone https://github.com/user/repo.git

# 在需要外网的技能中使用
./scripts/v2ray-proxy.sh on
# ... 执行需要外网的操作 ...
./scripts/v2ray-proxy.sh off
```

## 许可证

MIT License
