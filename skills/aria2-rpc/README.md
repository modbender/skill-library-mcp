# aria2-rpc Skill

远程控制 aria2 下载服务的 OpenClaw 技能。

## 功能

- ✅ 添加 HTTP/FTP/HTTPS/Magnet 下载
- ✅ 查询活动/等待/已完成任务
- ✅ 获取任务详情和进度
- ✅ 暂停/继续/删除任务
- ✅ 全局统计信息
- ✅ 支持远程 aria2 实例
- ✅ 支持 RPC 认证

## 快速开始

### 1. 安装依赖

```bash
pip3 install requests
```

### 2. 启动 aria2（带 RPC）

```bash
aria2c --enable-rpc --rpc-listen-all=true --rpc-secret=mytoken -D
```

### 3. 使用技能

```bash
# 添加下载
python3 scripts/aria2_rpc.py add-uri "http://example.com/file.zip" --rpc-secret mytoken

# 查看活动下载
python3 scripts/aria2_rpc.py tell-active --rpc-secret mytoken

# 查看全局统计
python3 scripts/aria2_rpc.py global-stat --rpc-secret mytoken
```

## 文档

- [SKILL.md](SKILL.md) - 完整使用说明
- [references/QUICKSTART.md](references/QUICKSTART.md) - 快速命令参考

## 示例

```bash
# 添加带多个镜像的下载
python3 scripts/aria2_rpc.py add-uri \
  "http://mirror1/file.zip" \
  "http://mirror2/file.zip" \
  --dir /downloads \
  --rpc-secret mytoken

# 暂停下载
python3 scripts/aria2_rpc.py pause <GID> --rpc-secret mytoken

# 删除下载
python3 scripts/aria2_rpc.py remove <GID> --rpc-secret mytoken
```

## 环境变量

```bash
export ARIA2_RPC_URL="http://localhost:6800/jsonrpc"
export ARIA2_RPC_SECRET="mytoken"

# 之后可以省略 --rpc-url 和 --rpc-secret 参数
python3 scripts/aria2_rpc.py tell-active
```

## 注意事项

1. 此技能仅控制下载任务，不涉及下载后文件的操作
2. 建议使用 `rpc-secret` 进行认证
3. 远程访问需确保防火墙允许 6800 端口
