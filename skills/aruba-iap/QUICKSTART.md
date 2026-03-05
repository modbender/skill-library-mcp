# Aruba IAP Skill - Quick Start Guide

本指南帮助你快速开始使用 Aruba IAP Skill 管理 Aruba Instant Access Points。

## 前置要求

- Python 3.9+
- OpenClaw 已安装
- Aruba IAP 设备（运行 Instant OS）

## 安装

```bash
cd /Users/scsun/.openclaw/workspace/skills/aruba-iap
./install.sh
```

安装完成后，`iapctl` 命令将安装到 `/opt/homebrew/bin/iapctl`。

## 基本使用

### 1. 发现 IAP 集群

首先发现你的 IAP 集群，获取基本信息：

```bash
iapctl discover --cluster office-iap --vc 192.168.20.56 --out ./out
```

参数说明：
- `--cluster`: 集群名称（自定义）
- `--vc`: 虚拟控制器 IP 地址
- `--out`: 输出目录

### 2. 创建配置快照

获取完整的配置快照作为基线：

```bash
iapctl snapshot --cluster office-iap --vc 192.168.20.56 --out ./baseline
```

生成的文件：
- `result.json` - 结构化结果
- `raw/show_version.txt` - 版本信息
- `raw/show_running-config.txt` - 完整配置
- `raw/show_wlan.txt` - WLAN 配置
- `raw/show_ap_database.txt` - AP 数据库
- 其他原始输出文件

### 3. 配置 SSH 认证（推荐）

使用 SSH 密钥进行认证更安全：

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -f ~/.ssh/aruba_iap_key

# 添加公钥到 IAP
ssh-copy-id -i ~/.ssh/aruba_iap_key.pub admin@192.168.20.56

# 配置 SSH config
cat >> ~/.ssh/config << EOF
Host office-iap-vc
  HostName 192.168.20.56
  User admin
  IdentityFile ~/.ssh/aruba_iap_key
EOF
```

现在可以使用 SSH config 连接：

```bash
iapctl discover --cluster office-iap --vc 192.168.20.56 --out ./out --ssh-config ~/.ssh/config
```

### 4. 准备配置变更

创建一个变更文件 `changes.json`：

```json
{
  "changes": [
    {
      "type": "ntp",
      "servers": ["10.10.10.1", "10.10.10.2"]
    },
    {
      "type": "ssid_vlan",
      "profile": "Corporate",
      "essid": "CorporateWiFi",
      "vlan_id": 100
    },
    {
      "type": "radius_server",
      "name": "radius-primary",
      "ip": "10.10.10.5",
      "auth_port": 1812,
      "acct_port": 1813,
      "secret_ref": "secret:radius-primary-key"
    }
  ]
}
```

### 5. 生成差异

查看将要执行的操作：

```bash
iapctl diff --cluster office-iap --vc 192.168.20.56 --in changes.json --out ./diff
```

输出文件：
- `commands.json` - 要执行的命令（JSON）
- `commands.txt` - 要执行的命令（可读文本）
- `risk.json` - 风险评估

### 6. 应用变更

查看生成的命令后，可以应用变更：

```bash
# 查看命令
cat ./diff/commands.txt

# 预演模式（不实际执行）
iapctl apply --cluster office-iap --vc 192.168.20.56 \
  --change-id chg_20260222_0001 \
  --in ./diff/commands.json \
  --out ./apply \
  --dry-run

# 真实执行（需要 OpenClaw 审批）
iapctl apply --cluster office-iap --vc 192.168.20.56 \
  --change-id chg_20260222_0001 \
  --in ./diff/commands.json \
  --out ./apply
```

### 7. 验证配置

应用变更后，验证配置是否正确：

```bash
iapctl verify --cluster office-iap --vc 192.168.20.56 \
  --level basic \
  --out ./verify
```

### 8. 回滚（如需要）

如果需要回滚变更：

```bash
iapctl rollback --cluster office-iap --vc 192.168.20.56 \
  --from-change-id chg_20260222_0001 \
  --out ./rollback
```

## 密钥管理

### 方法 1：使用 JSON 文件

创建 `secrets.json`：

```json
{
  "radius-primary-key": "my-secret-password-123",
  "radius-secondary-key": "my-secondary-password-456"
}
```

在 Python 代码中加载：

```python
from iapctl.secrets import load_secrets_file

load_secrets_file("secrets.json")
```

### 方法 2：使用环境变量

```bash
export RADIUS_SHARED_SECRET="my-secret-value"
```

在变更文件中引用：

```json
{
  "type": "radius_server",
  "secret_ref": "env:RADIUS_SHARED_SECRET"
}
```

## OpenClaw 集成

在 OpenClaw 中使用时，确保配置正确的工具白名单：

```json
{
  "allowedTools": [
    "Bash(iapctl:*)"
  ]
}
```

## 完整工作流示例

```bash
# 1. 建立基线
iapctl snapshot --cluster office-iap --vc 192.168.20.56 --out ./baseline

# 2. 准备变更
cat > changes.json << EOF
{
  "changes": [
    {
      "type": "ntp",
      "servers": ["10.10.10.1"]
    }
  ]
}
EOF

# 3. 生成差异
iapctl diff --cluster office-iap --vc 192.168.20.56 --in changes.json --out ./diff

# 4. 检查命令
cat ./diff/commands.txt

# 5. 预演
iapctl apply --cluster office-iap --vc 192.168.20.56 \
  --change-id chg_$(date +%Y%m%d_%H%M%S) \
  --in ./diff/commands.json \
  --out ./apply \
  --dry-run

# 6. 应用
iapctl apply --cluster office-iap --vc 192.168.20.56 \
  --change-id chg_$(date +%Y%m%d_%H%M%S) \
  --in ./diff/commands.json \
  --out ./apply

# 7. 验证
iapctl verify --cluster office-iap --vc 192.168.20.56 \
  --level basic \
  --out ./verify
```

## 故障排查

### 连接失败

```bash
# 直接测试 SSH 连接
ssh admin@192.168.20.56

# 使用详细模式运行
iapctl discover --cluster test --vc 192.168.20.56 \
  --out ./test --verbose
```

### 找不到命令

```bash
# 检查安装
which iapctl

# 手动激活 venv
source /opt/homebrew/iapctl-venv/bin/activate
python -m iapctl.cli --help
```

### Python 依赖问题

```bash
cd /Users/scsun/.openclaw/workspace/skills/aruba-iap/iapctl
source venv/bin/activate
pip install -e . 'scrapli[paramiko]'
```

## 更多信息

- 完整文档：查看 `SKILL.md`
- API 参考：查看 `iapctl/` 目录下的 Python 代码
- 示例文件：查看 `examples/` 目录

## 支持

遇到问题？检查：
1. SSH 连接是否正常
2. IAP 设备是否可达
3. 日志文件：`./out/*/result.json`
4. 原始输出：`./out/*/raw/*.txt`
