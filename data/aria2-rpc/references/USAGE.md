# Aria2 RPC 使用示例

## 基本语法

```bash
python3 /root/.openclaw/workspace/skills/aria2-rpc/scripts/aria2_rpc.py <command> [options]
```

## 命令示例

### 添加下载任务

```bash
# 添加 HTTP/FTP 下载
python3 scripts/aria2_rpc.py add-uri "http://example.com/file.zip"

# 添加多个链接（同一文件的不同源）
python3 scripts/aria2_rpc.py add-uri "http://mirror1/file.zip" "http://mirror2/file.zip"

# 添加 Magnet 链接
python3 scripts/aria2_rpc.py add-uri "magnet:?xt=urn:btih:..."

# 指定下载目录
python3 scripts/aria2_rpc.py add-uri "http://example.com/file.zip" --dir /path/to/download

# 指定文件名
python3 scripts/aria2_rpc.py add-uri "http://example.com/file.zip" --out myfile.zip

# 使用认证
python3 scripts/aria2_rpc.py add-uri "http://example.com/file.zip" --rpc-secret your-token
```

### 查询下载任务

```bash
# 获取活动下载
python3 scripts/aria2_rpc.py tell-active

# 获取等待中的下载
python3 scripts/aria2_rpc.py tell-waiting

# 获取已停止的下载
python3 scripts/aria2_rpc.py tell-stopped

# 获取特定任务详情
python3 scripts/aria2_rpc.py tell-status <GID>
```

### 控制下载任务

```bash
# 暂停下载
python3 scripts/aria2_rpc.py pause <GID>

# 继续下载
python3 scripts/aria2_rpc.py unpause <GID>

# 删除下载
python3 scripts/aria2_rpc.py remove <GID>

# 强制删除（包括已完成的）
python3 scripts/aria2_rpc.py remove-force <GID>
```

### 全局统计

```bash
python3 scripts/aria2_rpc.py global-stat
```

## 远程实例配置

```bash
# 使用远程服务器
export ARIA2_RPC_URL="http://192.168.1.100:6800/jsonrpc"
export ARIA2_RPC_SECRET="my-secret"

# 添加下载
python3 scripts/aria2_rpc.py add-uri "http://example.com/file.zip"
```

## 配置文件

创建 `~/.aria2/rpc_config.json`：

```json
{
  "rpc_url": "http://localhost:6800/jsonrpc",
  "rpc_secret": "your-secret-token",
  "timeout": 30
}
```

脚本会自动读取此配置文件。