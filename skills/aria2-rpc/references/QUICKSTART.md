# aria2-rpc Quick Reference

## 快速命令参考

### 添加下载

```bash
# 添加单个 HTTP 链接
python3 scripts/aria2_rpc.py add-uri "http://example.com/file.zip"

# 添加多个镜像源
python3 scripts/aria2_rpc.py add-uri \
  "http://mirror1/file.zip" \
  "http://mirror2/file.zip"

# 添加 Magnet 链接
python3 scripts/aria2_rpc.py add-uri "magnet:?xt=urn:btih:HASH"

# 指定下载目录和文件名
python3 scripts/aria2_rpc.py add-uri "http://example.com/file.zip" \
  --dir /path/to/download \
  --out myfile.zip

# 使用自定义连接数
python3 scripts/aria2_rpc.py add-uri "http://example.com/file.zip" \
  --split 16 \
  --max-connections 8
```

### 查询状态

```bash
# 查看所有活动下载
python3 scripts/aria2_rpc.py tell-active

# 查看等待中的下载
python3 scripts/aria2_rpc.py tell-waiting

# 查看已停止/已完成的下载
python3 scripts/aria2_rpc.py tell-stopped

# 查看特定任务详情
python3 scripts/aria2_rpc.py tell-status <GID>

# 查看全局统计
python3 scripts/aria2_rpc.py global-stat
```

### 控制下载

```bash
# 暂停下载
python3 scripts/aria2_rpc.py pause <GID>

# 强制暂停下载
python3 scripts/aria2_rpc.py pause <GID> --force

# 继续下载
python3 scripts/aria2_rpc.py unpause <GID>

# 删除下载
python3 scripts/aria2_rpc.py remove <GID>

# 强制删除下载
python3 scripts/aria2_rpc.py remove <GID> --force
```

### 远程连接

```bash
# 使用远程 aria2 服务器
python3 scripts/aria2_rpc.py tell-active \
  --rpc-url http://192.168.1.100:6800/jsonrpc \
  --rpc-secret my-secret-token

# 或设置环境变量
export ARIA2_RPC_URL="http://192.168.1.100:6800/jsonrpc"
export ARIA2_RPC_SECRET="my-secret-token"
python3 scripts/aria2_rpc.py tell-active
```

## 常用场景

### 场景 1: 批量下载

```bash
# 从文件读取 URLs
cat urls.txt | while read url; do
  python3 scripts/aria2_rpc.py add-uri "$url"
done
```

### 场景 2: 监控下载进度

```bash
# 每秒刷新显示活动下载
watch -n 1 'python3 scripts/aria2_rpc.py tell-active 2>/dev/null | head -20'
```

### 场景 3: 下载完成后清理

```bash
# 删除所有已完成的下载
for gid in $(python3 scripts/aria2_rpc.py tell-stopped | grep -oP '\[GID: \K[a-f0-9]+'); do
  python3 scripts/aria2_rpc.py remove "$gid"
done
```

## GID 说明

- 每个下载任务有唯一的 GID（全局 ID）
- GID 是 16 字符的十六进制字符串
- 可以通过 `tell-active`、`tell-waiting`、`tell-stopped` 获取
- 后续操作（暂停、继续、删除）都需要 GID

## 输出说明

### tell-active / tell-waiting / tell-stopped

```
[GID: abc12345] filename.zip
  Status: active | Progress: 45.2%
  Size: 45.20 MB / 100.00 MB
  Speed: ↓ 2.50 MB/s | ↑ 0.00 B/s
  Connections/Peers: 8 | ETA: 22s
```

### global-stat

```
aria2 Global Statistics
============================================================
Active downloads:      3
Waiting downloads:     5
Stopped downloads:     12
Total speed:           ↓ 5.25 MB/s
                       ↑ 125.00 KB/s
Files downloaded:      156
Files removed:         42

aria2 Version:       1.36.0
Enabled Features:    Async DNS, BitTorrent, ...
```

## 故障排除

### 连接被拒绝
```bash
# 检查 aria2 是否运行
ps aux | grep aria2c

# 检查端口
netstat -tlnp | grep 6800

# 启动 aria2（带 RPC）
aria2c --enable-rpc --rpc-listen-all=true --rpc-secret=mytoken -D
```

### 认证失败
```bash
# 确保使用正确的 secret
python3 scripts/aria2_rpc.py tell-active --rpc-secret correct-token
```

### 依赖缺失
```bash
# 安装 requests 库
pip3 install requests
```

### 配置管理

```bash
# 获取全局配置
python3 scripts/aria2_rpc.py get-global-option

# 获取特定配置项
python3 scripts/aria2_rpc.py get-global-option --key max-overall-download-limit

# 修改全局配置（单个）
python3 scripts/aria2_rpc.py set-global-option max-overall-download-limit=10M

# 修改全局配置（多个）
python3 scripts/aria2_rpc.py set-global-option \
  max-overall-download-limit=50M \
  split=16 \
  max-connection-per-server=8

# 获取任务配置
python3 scripts/aria2_rpc.py get-option <GID>

# 修改任务配置
python3 scripts/aria2_rpc.py set-option <GID> split=8 dir=/downloads
```

## 常用配置项

### 速度限制
- `max-overall-download-limit` - 全局最大下载速度（如：10M, 0 为不限）
- `max-overall-upload-limit` - 全局最大上传速度

### 并发控制
- `max-concurrent-downloads` - 最大同时下载数（默认：5）
- `split` - 文件分块数（默认：5）
- `max-connection-per-server` - 每服务器连接数（默认：1）

### 其他常用
- `dir` - 下载目录
- `user-agent` - 用户代理
- `timeout` - 超时时间（秒）
- `continue` - 断点续传（true/false）

详见：[references/CONFIG_GUIDE.md](references/CONFIG_GUIDE.md)
