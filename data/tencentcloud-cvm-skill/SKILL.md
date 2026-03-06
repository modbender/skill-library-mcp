---
name: tencentcloud-cvm-skill
description: 腾讯云 CVM 云服务器运维工具集
version: 2.0.0
author: garden
tags: [tencent-cloud, cvm, devops, automation]
---

# 腾讯云 CVM 运维工具

基于 Bash + tccli 的腾讯云 CVM 云服务器运维工具集，支持**实例创建**、**资源查询**、**服务器运维**三大核心功能。

## 快速开始

### 1. 安装依赖

```bash
# tccli（腾讯云命令行工具）
pip3 install tccli

# jq（JSON 解析）
brew install jq        # macOS
apt install jq         # Ubuntu

# sshpass（SSH 密码认证，运维操作需要）
brew install hudochenkov/sshpass/sshpass   # macOS
apt install sshpass                         # Ubuntu
```

### 2. 配置凭证

```bash
export TENCENTCLOUD_SECRET_ID="your-secret-id"
export TENCENTCLOUD_SECRET_KEY="your-secret-key"
```

### 3. 典型工作流

```bash
# 1. 查询资源准备创建实例
./scripts/query/describe-zones.sh                    # 查可用区
./scripts/query/describe-images.sh --platform Ubuntu # 查镜像
./scripts/query/describe-vpcs.sh                     # 查 VPC

# 2. 创建实例（密码自动保存）
./scripts/lifecycle/create-instance.sh \
  --zone ap-guangzhou-3 \
  --instance-type S5.MEDIUM2 \
  --image-id img-xxx \
  --vpc-id vpc-xxx \
  --subnet-id subnet-xxx \
  --sg-id sg-xxx

# 3. 更新实例 IP
./scripts/utils/update-instance-ip.sh --instance-id ins-xxx --auto

# 4. 运维操作（只需 instance-id）
./scripts/ops/ssh-connect.sh --instance-id ins-xxx
./scripts/ops/system-info.sh --instance-id ins-xxx
```

## 功能模块

```
scripts/
├── lifecycle/    # 实例生命周期：创建、启动、停止、重启、销毁
├── query/        # 资源查询：实例、镜像、VPC、子网、安全组、可用区
├── ops/          # 服务器运维：SSH、远程执行、系统信息、磁盘、进程、服务、日志、安全、传输、网络
├── utils/        # 辅助工具：密码管理、IP 更新、配置查看
└── common.sh     # 公共函数库
```

### 实例生命周期

| 脚本 | 功能 | 示例 |
|------|------|------|
| `recommend-instance.sh` | 场景推荐创建 | `--scene blog-small` |
| `create-instance.sh` | 手动创建实例 | `--zone ap-guangzhou-3 --instance-type S5.MEDIUM2` |
| `start-instance.sh` | 启动实例 | `--instance-id ins-xxx` |
| `stop-instance.sh` | 停止实例 | `--instance-id ins-xxx [--force]` |
| `reboot-instance.sh` | 重启实例 | `--instance-id ins-xxx` |
| `terminate-instance.sh` | 销毁实例 | `--instance-id ins-xxx` |

#### 场景推荐

根据使用场景自动推荐配置：

```bash
./scripts/lifecycle/recommend-instance.sh --scene blog-small    # 个人博客
./scripts/lifecycle/recommend-instance.sh --scene web-medium    # 中型Web应用
./scripts/lifecycle/recommend-instance.sh --list-scenes         # 查看所有场景
```

| 场景 | 适用 | 配置 |
|------|------|------|
| `blog-small` | 个人博客 (日PV<5K) | 1核1G |
| `blog-medium` | 中型博客 (日PV 5K-50K) | 2核4G |
| `web-small` | 小型Web (日PV<10K) | 2核2G |
| `web-medium` | 中型Web (日PV 10K-100K) | 4核8G |
| `api-small` | 小型API (QPS<100) | 2核4G |
| `dev` | 开发测试 | 2核2G |
| `database-small` | 小型数据库 | 2核4G + 50G数据盘 |

### 资源查询

| 脚本 | 功能 | 常用参数 |
|------|------|----------|
| `describe-regions.sh` | 查询地域 | `--available` |
| `describe-instances.sh` | 查询实例 | `--instance-id`, `--name` |
| `describe-zones.sh` | 查询可用区 | `--region` |
| `describe-instance-types.sh` | 查询机型 | `--zone`, `--family`, `--type` |
| `describe-images.sh` | 查询镜像 | `--instance-type`, `--platform` |
| `describe-vpcs.sh` | 查询 VPC | `--vpc-id` |
| `describe-subnets.sh` | 查询子网 | `--vpc-id`, `--zone` |
| `describe-security-groups.sh` | 查询安全组 | `--sg-id`, `--name` |

### 服务器运维

> **优先级策略**：运维操作优先使用 ops 脚本（SSH + 密码直连执行），仅在脚本无法满足需求时才使用 tccli 接口调用。
>
> **安全限制**：ops 目录仅使用已有的预定义脚本，不支持动态生成新脚本。
>
> **重要原则**：运维写操作（如停止、重启、销毁实例，服务管理，文件传输等）需要人工确认后执行。
>
> 所有运维脚本只需 `--instance-id` 即可自动获取密码和 IP

| 脚本 | 功能 | 特殊参数 |
|------|------|----------|
| `ssh-connect.sh` | SSH 连接 | `--port` |
| `remote-exec.sh` | 远程命令（仅支持预定义安全命令） | `--cmd <command>` |
| `system-info.sh` | 系统信息 | - |
| `disk-usage.sh` | 磁盘检查 | `--threshold <n>` |
| `process-monitor.sh` | 进程监控 | `--top <n>`, `--filter` |
| `service-manage.sh` | 服务管理 | `--service`, `--action` |
| `log-viewer.sh` | 日志查看 | `--file`, `--lines`, `--follow` |
| `security-check.sh` | 安全检查 | - |
| `file-transfer.sh` | 文件传输 | `--upload/--download`, `--local`, `--remote` |
| `network-check.sh` | 网络检查 | `--target` |

#### remote-exec 安全命令集

`remote-exec.sh` 仅支持以下预定义的只读命令或 ops 目录下的脚本：

| 分类 | 命令 | 用途 |
|------|------|------|
| **系统信息** | `uptime` | 系统运行时间和负载 |
| | `uname -a` | 内核和系统信息 |
| | `hostname` | 主机名 |
| | `cat /etc/os-release` | 操作系统版本 |
| | `date` | 系统时间 |
| | `timedatectl` | 时区和时间同步状态 |
| **CPU** | `cat /proc/loadavg` | 系统负载 |
| | `top -bn1 \| head -20` | CPU 和进程概览 |
| | `mpstat` | CPU 使用统计 |
| | `nproc` | CPU 核数 |
| | `lscpu` | CPU 详细信息 |
| **内存** | `free -h` | 内存使用情况 |
| | `cat /proc/meminfo` | 内存详细信息 |
| | `vmstat` | 虚拟内存统计 |
| **磁盘** | `df -h` | 磁盘使用情况 |
| | `df -i` | inode 使用情况 |
| | `lsblk` | 块设备列表 |
| | `fdisk -l` | 磁盘分区信息 |
| | `du -sh <path>` | 目录大小 |
| **进程** | `ps aux` | 进程列表 |
| | `ps aux \| head -20` | 前 20 个进程 |
| | `pgrep <name>` | 按名称查找进程 |
| | `pidof <name>` | 获取进程 PID |
| **网络** | `ip addr` | 网络接口信息 |
| | `ip route` | 路由表 |
| | `netstat -tlnp` | TCP 端口监听 |
| | `ss -tlnp` | 套接字统计 |
| | `ping -c 4 <host>` | 网络连通性测试 |
| | `curl -I <url>` | HTTP 头信息 |
| | `dig <domain>` | DNS 解析 |
| | `traceroute <host>` | 路由追踪 |
| **服务** | `systemctl status <service>` | 服务状态 |
| | `systemctl is-active <service>` | 服务是否运行 |
| | `systemctl list-units --type=service` | 服务列表 |
| **日志** | `tail -n 100 <logfile>` | 查看日志末尾 |
| | `head -n 100 <logfile>` | 查看日志开头 |
| | `journalctl -u <service> -n 100` | 服务日志 |
| | `dmesg \| tail -50` | 内核日志 |
| **安全** | `who` | 当前登录用户 |
| | `w` | 用户活动 |
| | `last -n 20` | 登录历史 |
| | `cat /etc/passwd` | 用户列表 |
| | `cat /etc/group` | 用户组列表 |
| **其他** | `env` | 环境变量 |
| | `crontab -l` | 定时任务列表 |
| | `docker ps` | Docker 容器列表 |
| | `docker images` | Docker 镜像列表 |
| | `scripts/ops/*.sh` | ops 目录下的预定义运维脚本 |

### 辅助工具

| 脚本 | 功能 |
|------|------|
| `show-defaults.sh` | 查看当前配置 |
| `get-password.sh` | 获取实例密码 |
| `update-instance-ip.sh` | 更新实例 IP |
| `manage-passwords.sh` | 管理密码存储 |

## 配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TENCENTCLOUD_SECRET_ID` | API 密钥 ID | **必需** |
| `TENCENTCLOUD_SECRET_KEY` | API 密钥 Key | **必需** |
| `TENCENT_CVM_DEFAULT_REGION` | 默认地域 | `ap-guangzhou` |
| `TENCENT_CVM_DEFAULT_ZONE` | 默认可用区 | - |
| `TENCENT_CVM_DEFAULT_INSTANCE_TYPE` | 默认机型 | - |
| `TENCENT_CVM_DEFAULT_IMAGE_ID` | 默认镜像 | - |
| `TENCENT_CVM_DEFAULT_VPC_ID` | 默认 VPC | - |
| `TENCENT_CVM_DEFAULT_SUBNET_ID` | 默认子网 | - |
| `TENCENT_CVM_DEFAULT_SG_ID` | 默认安全组 | - |
| `TENCENT_CVM_DEFAULT_DISK_SIZE` | 系统盘大小 | `20` |
| `TENCENT_CVM_DEFAULT_CHARGE_TYPE` | 计费类型 | `POSTPAID_BY_HOUR` |

### 支持的地域

`ap-beijing` | `ap-shanghai` | `ap-guangzhou` | `ap-chengdu` | `ap-nanjing` | `ap-hongkong`

### 支持的镜像平台

`TencentOS` | `CentOS` | `Ubuntu` | `Debian`

### SSH 登录用户名

| 系统 | 默认用户名 | 示例 |
|------|------------|------|
| Ubuntu | `ubuntu` | `ssh ubuntu@<ip>` |
| 其他 Linux (TencentOS, CentOS, Debian) | `root` | `ssh root@<ip>` |

## 密码存储

创建实例时自动生成密码并保存到 `~/.tencent_cvm_passwords`（权限 600）：

```json
{
  "ins-xxx": {
    "password": "aB3#xK9$mN2@pQ",
    "host": "1.2.3.4",
    "region": "ap-guangzhou",
    "created_at": "2026-02-06 15:30:00"
  }
}
```

管理命令：
```bash
./scripts/utils/manage-passwords.sh --list              # 列出所有
./scripts/utils/manage-passwords.sh --show ins-xxx      # 查看详情
./scripts/utils/manage-passwords.sh --delete ins-xxx    # 删除记录
```

## 安全说明

本工具集设计用于可信环境下的服务器运维，遵循以下安全原则：

1. **预定义脚本**：仅执行 `scripts/` 目录下已审核的预定义脚本，禁止动态生成或执行任意代码
2. **人工确认**：所有写操作（停止、重启、销毁、文件传输等）必须经人工确认后执行
3. **凭证安全**：密码文件 `~/.tencent_cvm_passwords` 权限为 600，仅限本地用户访问
4. **操作审计**：所有操作均有日志输出，便于追溯
5. **使用场景**：适用于开发测试环境，生产环境建议配合堡垒机使用

## 参考

- [腾讯云 CVM API 文档](https://cloud.tencent.com/document/product/213)
- [tccli 使用指南](https://cloud.tencent.com/document/product/440/34011)
