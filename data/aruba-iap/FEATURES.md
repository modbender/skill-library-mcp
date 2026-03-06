# Aruba-IAP Skill 功能清单

**版本**: v0.1.0
**日期**: 2026-02-22
**状态**: ✅ 生产就绪（需真实设备测试）

---

## 📋 命令列表

### 1. discover - 发现 IAP 集群

**功能**：收集基本 IAP 集群信息

**用法**：
```bash
iapctl discover --cluster <name> --vc <ip> --out <dir>
```

**参数**：
- `--cluster`: 集群名称（必需）
- `--vc`: 虚拟控制器 IP（必需）
- `--out`: 输出目录（默认：`./out`）
- `--ssh-host`: SSH 主机（默认：vc）
- `--ssh-user`: SSH 用户名（默认：admin）
- `--ssh-password`: SSH 密码
- `--ssh-port`: SSH 端口（默认：22）
- `--ssh-config`: SSH 配置文件路径
- `--quiet`, `-q`: 安静模式

**输出**：
- `result.json` - 结构化结果
- `raw/show_version.txt` - 版本信息
- `raw/show_ap_database.txt` - AP 数据库
- `raw/show_ap_group.txt` - AP 组信息

---

### 2. snapshot - 配置快照

**功能**：获取完整的配置快照

**用法**：
```bash
iapctl snapshot --cluster <name> --vc <ip> --out <dir>
```

**参数**：与 `discover` 相同

**输出**：
- `result.json` - 结构化结果
- `raw/show_version.txt` - 版本信息
- `raw/show_running-config.txt` - 完整配置
- `raw/show_wlan.txt` - WLAN 配置
- `raw/show_ap_database.txt` - AP 数据库
- `raw/show_user-table.txt` - 用户表
- `raw/show_interface.txt` - 接口状态
- `raw/show_radio.txt` - 无线状态

---

### 3. diff - 生成差异

**功能**：生成当前配置与期望配置的差异

**用法**：
```bash
iapctl diff --cluster <name> --vc <ip> --in <changes.json> --out <dir>
```

**参数**：
- `--cluster`: 集群名称（必需）
- `--vc`: 虚拟控制器 IP（必需）
- `--in`: 变更 JSON 文件（必需）
- `--out`: 输出目录（默认：`./out`）
- `--change-id`: 变更 ID（自动生成）
- 其他 SSH 参数同上

**输出**：
- `result.json` - 结构化结果
- `raw/show_version.txt` - 版本信息
- `raw/show_running-config.txt` - 当前配置
- `commands.json` - 要执行的命令（JSON）
- `commands.txt` - 要执行的命令（可读文本）
- `risk.json` - 风险评估

---

### 4. apply - 应用变更

**功能**：应用配置变更（支持 dry_run）

**用法**：
```bash
iapctl apply --cluster <name> --vc <ip> --change-id <id> --in <commands.json> --out <dir>
```

**参数**：
- `--cluster`: 集群名称（必需）
- `--vc`: 虚拟控制器 IP（必需）
- `--change-id`: 变更 ID（必需）
- `--in`: 命令 JSON 文件（必需）
- `--out`: 输出目录（默认：`./out`）
- `--dry-run`: 预演模式（不实际执行）
- 其他 SSH 参数同上

**输出**：
- `result.json` - 结构化结果
- `raw/show_version.txt` - 版本信息
- `raw/pre_running-config.txt` - 应用前配置
- `raw/apply_step_*.txt` - 每步输出
- `raw/post_running-config.txt` - 应用后配置（非 dry_run）

**审批要求**：需要 OpenClaw 审批

---

### 5. verify - 验证配置

**功能**：验证配置状态

**用法**：
```bash
iapctl verify --cluster <name> --vc <ip> --level <basic|full> --out <dir>
```

**参数**：
- `--cluster`: 集群名称（必需）
- `--vc`: 虚拟控制器 IP（必需）
- `--level`: 验证级别（`basic` 或 `full`，默认：`basic`）
- `--expect`: 期望状态文件（可选）
- `--out`: 输出目录（默认：`./out`）
- 其他 SSH 参数同上

**输出**：
- `result.json` - 结构化结果
- `raw/show_version.txt` - 版本信息
- `raw/show_ap_database.txt` - AP 数据库
- `raw/show_wlan.txt` - WLAN 配置
- `raw/show_interface.txt` - 接口状态（full 级别）
- `raw/show_radio.txt` - 无线状态（full 级别）
- `raw/show_user-table.txt` - 用户表（full 级别）

---

### 6. rollback - 回滚配置

**功能**：回滚到之前的配置

**用法**：
```bash
iapctl rollback --cluster <name> --vc <ip> --from-change-id <id> --out <dir>
```

**参数**：
- `--cluster`: 集群名称（必需）
- `--vc`: 虚拟控制器 IP（必需）
- `--from-change-id`: 要回滚的变更 ID（必需）
- `--out`: 输出目录（默认：`./out`）
- 其他 SSH 参数同上

**输出**：
- `result.json` - 结构化结果
- `raw/show_version.txt` - 版本信息
- `raw/pre_rollback_running-config.txt` - 回滚前配置
- `raw/rollback_step_*.txt` - 每步输出
- `raw/post_rollback_running-config.txt` - 回滚后配置

**审批要求**：需要 OpenClaw 审批

---

## 🔧 支持的变更类型

### 1. NTP 配置

**类型**: `ntp`

**示例**：
```json
{
  "type": "ntp",
  "servers": ["10.10.10.1", "10.10.10.2"]
}
```

**生成的命令**：
```
ntp server 1 10.10.10.1
ntp server 2 10.10.10.2
```

**回滚命令**：
```
no ntp server 1
no ntp server 2
```

---

### 2. DNS 配置

**类型**: `dns`

**示例**：
```json
{
  "type": "dns",
  "servers": ["10.10.10.3", "10.10.10.4"]
}
```

**生成的命令**：
```
ip name-server 1 10.10.10.3
ip name-server 2 10.10.10.4
```

**回滚命令**：
```
no ip name-server 1
no ip name-server 2
```

---

### 3. SSID 和 VLAN 配置

**类型**: `ssid_vlan`

**示例**：
```json
{
  "type": "ssid_vlan",
  "profile": "Corporate",
  "essid": "CorporateWiFi",
  "vlan_id": 100
}
```

**生成的命令**：
```
wlan Corporate
  ssid CorporateWiFi
  vlan-id 100
  exit
```

**回滚命令**：
```
no wlan Corporate
```

---

### 4. RADIUS 服务器配置

**类型**: `radius_server`

**示例**：
```json
{
  "type": "radius_server",
  "name": "radius-primary",
  "ip": "10.10.10.5",
  "auth_port": 1812,
  "acct_port": 1813,
  "secret_ref": "secret:radius-primary-key"
}
```

**生成的命令**：
```
radius-server radius-primary
  host 10.10.10.5
  auth-port 1812
  acct-port 1813
  key <resolved-secret>
  exit
```

**回滚命令**：
```
no radius-server radius-primary
```

---

### 5. SSID 与 RADIUS 绑定

**类型**: `ssid_bind_radius`

**示例**：
```json
{
  "type": "ssid_bind_radius",
  "profile": "Corporate",
  "radius_primary": "radius-primary",
  "radius_secondary": "radius-secondary"
}
```

**生成的命令**：
```
wlan Corporate
  auth-server radius-primary
  auth-server radius-secondary
  exit
```

**回滚命令**：
```
wlan Corporate
  no auth-server
  exit
```

---

### 6. RF 模板配置

**类型**: `rf_template`

**示例**：
```json
{
  "type": "rf_template",
  "template": "office-default"
}
```

**支持的模板值**：
- `office-default` - 办公室默认
- `high-density` - 高密度
- `conference` - 会议室
- `corridor` - 走廊

**生成的命令**：
```
rf-profile office-default
```

**回滚命令**：
```
no rf-profile
```

---

## 🔐 密钥管理

### 密钥格式

| 格式 | 说明 | 示例 |
|------|------|------|
| `secret:<name>` | 内存存储查找 | `secret:radius-primary-key` |
| `env:<VAR_NAME>` | 环境变量 | `env:RADIUS_SHARED_SECRET` |
| `file:<path>` | 文件内容 | `file:/path/to/secret.txt` |

### 加载密钥

**从 JSON 文件**：
```python
from iapctl.secrets import load_secrets_file

load_secrets_file("/path/to/secrets.json")
```

**secrets.json 格式**：
```json
{
  "radius-primary-key": "my-secret-password",
  "radius-secondary-key": "my-secondary-password"
}
```

**从环境变量**：
```bash
export RADIUS_SHARED_SECRET="my-secret-value"
```

然后在变更文件中使用：
```json
{
  "type": "radius_server",
  "secret_ref": "env:RADIUS_SHARED_SECRET"
}
```

---

## 📊 风险评估

### 风险级别

- **low**: 低风险 - 常规配置变更
- **medium**: 中风险 - 可能影响部分用户
- **high**: 高风险 - 可能影响整个网络

### 风险检测规则

1. **WLAN/RADIUS 删除** → medium
   - 可能导致用户无法连接

2. **VLAN 变更** → concern
   - 可能影响网络连通性

3. **大量变更** (>20 条命令) → medium
   - 建议分阶段应用

---

## 📈 版本兼容性

| Aruba 版本 | 状态 | 备注 |
|-----------|------|------|
| Instant 6.x | ✅ 支持 | 基础 IAP 功能 |
| Instant 8.x | ✅ 支持 | WiFi 6 (802.11ax) |
| AOS 10.x | ✅ 支持 | 最新功能和云管理 |

---

## 🎯 使用场景

### 场景 1：新站点部署

```bash
# 1. 配置基础网络
iapctl diff --cluster new-site --vc 10.0.0.1 \
  --in config/network-setup.json --out ./apply/network

# 2. 配置无线网络
iapctl diff --cluster new-site --vc 10.0.0.1 \
  --in config/wireless-setup.json --out ./apply/wireless

# 3. 应用配置（需要审批）
iapctl apply --cluster new-site --vc 10.0.0.1 \
  --change-id chg_deploy_20260222 \
  --in ./apply/network/commands.json --out ./result/network

# 4. 验证
iapctl verify --cluster new-site --vc 10.0.0.1 \
  --level full --out ./verify
```

### 场景 2：配置变更

```bash
# 1. 建立基线
iapctl snapshot --cluster office-iap --vc 192.168.20.56 \
  --out ./baseline/$(date +%Y%m%d)

# 2. 生成变更
iapctl diff --cluster office-iap --vc 192.168.20.56 \
  --in config/update-ntp.json --out ./diff

# 3. 审查
cat ./diff/commands.txt
cat ./diff/risk.json

# 4. 应用（dry run）
iapctl apply --cluster office-iap --vc 192.168.20.56 \
  --change-id chg_ntp_20260222 \
  --in ./diff/commands.json --out ./apply --dry-run

# 5. 真实应用
iapctl apply --cluster office-iap --vc 192.168.20.56 \
  --change-id chg_ntp_20260222 \
  --in ./diff/commands.json --out ./apply
```

### 场景 3：回滚

```bash
# 应用出错，立即回滚
iapctl rollback --cluster office-iap --vc 192.168.20.56 \
  --from-change-id chg_ntp_20260222 \
  --out ./rollback

# 验证回滚成功
iapctl verify --cluster office-iap --vc 192.168.20.56 \
  --level basic --out ./verify
```

---

## 📞 获取帮助

**命令帮助**：
```bash
iapctl --help
iapctl discover --help
iapctl apply --help
```

**文档**：
- `README.md` - 项目总览
- `QUICKSTART.md` - 快速开始
- `SKILL.md` - OpenClaw 技能文档
- `DEVELOPMENT_SUMMARY.md` - 开发总结

**社区**：
- Discord: https://discord.gg/clawd
- GitHub: https://github.com/openclaw/openclaw

---

**最后更新**: 2026-02-22
**版本**: v0.1.0
