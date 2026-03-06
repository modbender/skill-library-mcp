# Stratos SDS Resource Node 配置指南

## 前提条件

- ppd v0.12.11 已安装（`ppd version` 验证）
- Go 1.19+
- 稳定的网络连接
- STOS 代币（用于节点激活）

## 一、初始化节点

```bash
mkdir -p ~/rsnode && cd ~/rsnode
ppd config -w -p
```

交互过程说明：

| 提示 | 说明 |
|------|------|
| Wallet nickname | 钱包昵称，如 `main1` |
| Password | 钱包密码（输入两次确认） |
| BIP39 mnemonic | 直接回车 = 生成新钱包；粘贴 24 词 = 恢复已有钱包 |
| HD-path | 回车使用默认值 `m/44'/606'/0'/0/0` |
| P2P key password | P2P 密钥密码 |
| P2P generation method | 选 `1) From the wallet` |

**重要：请务必备份 24 个助记词，丢失后无法恢复钱包。**

## 二、配置文件详解

配置文件位于 `~/rsnode/config/config.toml`。

### [version] 版本信息

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `app_ver` | `12` | 应用版本号 |
| `min_app_ver` | `11` | 最低兼容版本，低于此版本的节点连接将被拒绝 |
| `show` | `"v0.12.11"` | 版本显示字符串 |

### [blockchain] 区块链连接

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `chain_id` | `"stratos-1"` | 链 ID，主网为 `stratos-1` |
| `gas_adjustment` | `1.5` | Gas 估算倍数 |
| `insecure` | `false` | 是否使用非加密连接 |
| `grpc_server` | `"grpc.thestratos.org:443"` | 链的 gRPC 端点 |

### [home] 路径配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `accounts_path` | `"./accounts"` | 钱包和 P2P 密钥文件目录 |
| `download_path` | `"./download"` | 下载文件存放目录 |
| `peers_path` | `"./peers"` | 节点对等列表目录 |
| `storage_path` | `"./storage"` | 文件存储目录 |

### [keys] 密钥配置

| 参数 | 说明 |
|------|------|
| `p2p_address` | P2P 地址（`stsds` 前缀），初始化时自动生成 |
| `p2p_password` | P2P 密钥密码 |
| `wallet_address` | 钱包地址（`st` 前缀），初始化时自动生成 |
| `wallet_password` | 钱包密码 |
| `beneficiary_address` | 挖矿收益接收地址，默认与 `wallet_address` 相同 |

### [node] 节点设置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `debug` | `false` | 是否启用调试日志 |
| `max_disk_usage` | `7629394` | 最大磁盘使用量（MB），根据实际磁盘空间调整 |

### [node.connectivity] 网络连接（需要重点配置）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `internal` | `false` | 是否运行在内网。本地测试设为 `true` |
| `network_address` | `""` | **必填**，节点的外网 IP 地址。内网测试用 `127.0.0.1` |
| `network_port` | `"18081"` | 主通信端口，必须对外开放 |
| `metrics_port` | `"18152"` | Prometheus 指标端口 |
| `rpc_port` | `"18252"` | JSON-RPC API 端口 |
| `rpc_namespaces` | `"user,owner"` | RPC 启用的命名空间 |

### [node.connectivity.seed_meta_node] 种子节点

| 参数 | 说明 |
|------|------|
| `p2p_address` | 初始 Meta 节点的 P2P 地址 |
| `p2p_public_key` | 初始 Meta 节点的公钥 |
| `network_address` | 初始 Meta 节点的网络地址 |

> 默认值指向官方 Meta 节点，一般不需要修改。

### [streaming] 流媒体/SPFS 端口

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `internal_port` | `"18452"` | SPFS 内部 HTTP 服务端口（即 OpenClaw 插件使用的 API 端口） |
| `rest_port` | `"18552"` | REST API 端口 |

### [traffic] 流量控制

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `log_interval` | `10` | 流量日志记录间隔（秒） |
| `max_connections` | `1000` | 最大并发连接数 |
| `max_download_rate` | `0` | 下载速率限制（0 = 不限） |
| `max_upload_rate` | `0` | 上传速率限制（0 = 不限） |

### [monitor] 监控面板

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `tls` | `false` | 是否启用 TLS |
| `cert_file_path` | `""` | TLS 证书路径 |
| `key_file_path` | `""` | TLS 私钥路径 |
| `port` | `"18352"` | 监控 WebSocket 端口 |
| `allowed_origins` | `"localhost"` | 允许连接监控的 IP 列表 |

### [web_server] Web 管理界面

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `path` | `"./web"` | Web 文件目录 |
| `port` | `"18652"` | Web 服务端口 |
| `token_on_startup` | `false` | 启动时自动输入监控 Token |

## 三、关键配置修改

初始化完成后，根据实际情况修改以下参数：

```bash
vim ~/rsnode/config/config.toml
```

**必须修改：**

```toml
[node.connectivity]
# 如果是本地测试
internal = true
network_address = '127.0.0.1'

# 如果是公网节点，填写外网 IP
# internal = false
# network_address = 'YOUR_PUBLIC_IP'
```

**建议修改：**

```toml
[node]
# 根据磁盘空间调整（单位 MB），以下为 500GB
max_disk_usage = 512000
```

## 四、启动节点

```bash
# 推荐使用 tmux 保持后台运行
tmux new -s rsnode
cd ~/rsnode
ppd start
```

## 五、激活节点

在另一个终端打开 ppd 交互界面：

```bash
cd ~/rsnode
ppd terminal
```

依次执行：

```
# 1. 注册到 Meta 节点
rp

# 2. 质押激活（最低 1600 STOS）
activate 1600stos 0.01stos

# 3. 开始挖矿
startmining
```

> 激活前需要确保钱包内有足够的 STOS 代币。可通过交易所购买或向他人获取。

## 六、端口汇总

| 端口 | 用途 |
|------|------|
| 18081 | 主通信端口（必须开放） |
| 18152 | Prometheus 指标 |
| 18252 | JSON-RPC API |
| 18352 | 监控 WebSocket |
| 18452 | SPFS HTTP API（OpenClaw 插件使用） |
| 18552 | REST API |
| 18652 | Web 管理界面 |

## 七、常见问题

**Q: 如何查看钱包地址？**
在 ppd terminal 中执行 `wallets` 命令。

**Q: 节点无法连接？**
检查防火墙是否放行了 18081 端口，`network_address` 是否正确。

**Q: OpenClaw 插件连接失败？**
确认 `streaming.internal_port`（默认 18452）端口可访问，并检查 `skill.json` 中 `STRATOS_SPFS_GATEWAY` 配置。
