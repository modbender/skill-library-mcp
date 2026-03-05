---
name: aria2-rpc
description: Remote control for aria2 download service via JSON-RPC 2.0. Supports adding downloads (HTTP/FTP/Torrent/Magnet), querying task status, pausing/resuming, and removing tasks. Works with local or remote aria2 instances.
allowed-tools: Bash(aria2:*)
homepage: https://aria2.github.io
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      pip: [requests]
---

# aria2-rpc Skill

通过 JSON-RPC 2.0 协议远程控制 aria2 下载服务。

## 功能

- 添加 HTTP/FTP/Magnet/Torrent 下载
- 查询任务状态、暂停/继续/删除任务
- 获取全局统计和配置
- 支持远程 aria2 实例和 RPC 认证

## 安装

```bash
# 安装依赖
pip3 install requests

# 配置 aria2（启用 RPC）
aria2c --enable-rpc --rpc-listen-all=true --rpc-secret=mytoken -D
```

## 快速开始

```bash
# 添加下载
python3 /root/.openclaw/workspace/skills/aria2-rpc/scripts/aria2_rpc.py add-uri "http://example.com/file.zip" --rpc-secret mytoken

# 查看进度
python3 scripts/aria2_rpc.py tell-active --rpc-secret mytoken
```

## 环境变量

```bash
export ARIA2_RPC_URL="http://localhost:6800/jsonrpc"
export ARIA2_RPC_SECRET="your-secret-token"
```

## 脚本路径

- **主脚本**: `/root/.openclaw/workspace/skills/aria2-rpc/scripts/aria2_rpc.py`

## 详细文档

- [快速开始](references/QUICKSTART.md)
- [配置指南](references/CONFIG_GUIDE.md)
- [使用示例](references/USAGE.md)
- [API 参考](references/API_REFERENCE.md)
- [配置示例](references/aria2.conf.example)