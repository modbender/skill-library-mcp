---
name: 4090 服务器控制
description: 通过 SSH 控制 4090 服务器（192.168.199.17）。
---

# 4090 服务器控制

通过 SSH 控制 4090 服务器（192.168.199.17）。

## 快速命令

```bash
# Dify 状态检查
ssh -F ~/.ssh/config 4090 "docker ps -a | grep dify"

# 查看资源使用
ssh -F ~/.ssh/config 4090 "docker stats --no-stream"

# 重启 Dify
ssh -F ~/.ssh/config 4090 "cd ~/dify/docker && docker-compose restart"

# 查看日志
ssh -F ~/.ssh/config 4090 "docker logs -f docker-api-1"
```

## 常用操作

### Docker 管理
```bash
# 查看所有容器
docker ps -a

# 查看资源占用
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}'

# 重启单个容器
docker restart docker-api-1

# 查看容器日志
docker logs -f docker-api-1
```

### Dify 服务
| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| API | docker-api-1 | 5001 | 主 API |
| Worker | docker-worker-1 | 5001 | 异步任务 |
| Web | docker-web-1 | 3000 | 前端界面 |
| Plugin | docker-plugin_daemon-1 | 5003 | 插件服务 |
| Sandbox | docker-sandbox-1 | - | 安全沙箱 |

### 系统监控
```bash
# CPU/内存
top -bn1 | head -5

# 磁盘使用
df -h

# 负载情况
uptime
```

## SSH 配置

~/.ssh/config:
```
Host 4090
    HostName 192.168.199.17
    User olmmlo
    IdentityFile ~/.ssh/4090_key
    PasswordAuthentication no
