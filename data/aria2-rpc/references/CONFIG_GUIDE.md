# aria2 配置管理指南

本文档介绍如何使用 aria2-rpc 获取和修改 aria2 的配置选项。

## 命令概览

| 命令 | 说明 | 作用范围 |
|------|------|---------|
| `get-global-option` | 获取全局配置 | 所有下载任务 |
| `set-global-option` | 修改全局配置 | 所有下载任务 |
| `get-option` | 获取任务配置 | 单个下载任务 |
| `set-option` | 修改任务配置 | 单个下载任务 |

---

## 全局配置管理

### 获取全局配置

```bash
# 查看所有常用配置
python3 scripts/aria2_rpc.py get-global-option

# 查看特定配置项
python3 scripts/aria2_rpc.py get-global-option --key max-overall-download-limit

# 查看所有配置（包括不常用的）
python3 scripts/aria2_rpc.py get-global-option --verbose
```

### 修改全局配置

```bash
# 修改单个配置
python3 scripts/aria2_rpc.py set-global-option max-overall-download-limit=10M

# 修改多个配置
python3 scripts/aria2_rpc.py set-global-option \
  max-overall-download-limit=50M \
  max-connection-per-server=16 \
  split=16

# 带认证的远程修改
python3 scripts/aria2_rpc.py set-global-option \
  max-overall-download-limit=100M \
  --rpc-url http://192.168.1.100:6800/jsonrpc \
  --rpc-secret mytoken
```

### 常用全局配置项

#### 速度限制
- `max-overall-download-limit` - 全局最大下载速度（如：10M, 100K）
- `max-overall-upload-limit` - 全局最大上传速度
- `max-download-limit` - 每个任务的最大下载速度

#### 并发控制
- `max-concurrent-downloads` - 最大同时下载数（默认：5）
- `max-connection-per-server` - 每服务器最大连接数（默认：1）
- `split` - 文件分块数（默认：5）

#### 连接设置
- `timeout` - 超时时间（秒）
- `connect-timeout` - 连接超时时间（秒）
- `max-tries` - 最大重试次数（0 为无限）
- `retry-wait` - 重试等待时间（秒）

#### 下载路径
- `dir` - 默认下载目录

#### 其他常用
- `continue` - 断点续传（true/false）
- `user-agent` - 用户代理字符串
- `all-proxy` - 代理服务器设置
- `save-session` - 会话保存路径

---

## 任务级配置管理

### 获取任务配置

```bash
# 查看任务的常用配置
python3 scripts/aria2_rpc.py get-option <GID>

# 查看任务的所有配置
python3 scripts/aria2_rpc.py get-option <GID> --verbose
```

### 修改任务配置

```bash
# 修改任务的下载速度限制
python3 scripts/aria2_rpc.py set-option <GID> max-download-limit=5M

# 修改任务的分块数
python3 scripts/aria2_rpc.py set-option <GID> split=8

# 修改任务的下载目录
python3 scripts/aria2_rpc.py set-option <GID> dir=/path/to/new/dir

# 同时修改多个配置
python3 scripts/aria2_rpc.py set-option <GID> \
  split=16 \
  max-connection-per-server=8 \
  max-download-limit=20M
```

### 任务级配置 vs 全局配置

- **任务级配置**只影响指定的下载任务
- **全局配置**影响所有新创建的下载任务
- 任务级配置优先级高于全局配置
- 修改全局配置不会影响已在运行的任务

---

## 实用场景

### 场景 1：临时限速

```bash
# 下载时临时降低速度，避免影响其他网络活动
python3 scripts/aria2_rpc.py set-global-option max-overall-download-limit=1M

# 恢复不限速
python3 scripts/aria2_rpc.py set-global-option max-overall-download-limit=0
```

### 场景 2：为重要任务分配更多资源

```bash
# 为特定任务增加连接数和分块数
python3 scripts/aria2_rpc.py set-option <GID> \
  max-connection-per-server=16 \
  split=32
```

### 场景 3：批量修改等待中任务的配置

```bash
# 获取所有等待中的任务
GIDS=$(python3 scripts/aria2_rpc.py tell-waiting | grep -oP '\[GID: \K[a-f0-9]+')

# 批量修改
for gid in $GIDS; do
  python3 scripts/aria2_rpc.py set-option $gid split=16
done
```

### 场景 4：查看当前配置状态

```bash
# 查看当前下载速度限制
python3 scripts/aria2_rpc.py get-global-option --key max-overall-download-limit

# 查看当前并发数设置
python3 scripts/aria2_rpc.py get-global-option --key max-concurrent-downloads
```

---

## 配置项参考

### 完整配置项列表

运行以下命令查看所有可用的配置项：

```bash
python3 scripts/aria2_rpc.py get-global-option --verbose
```

### 部分重要配置项说明

| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| `dir` | 下载文件保存目录 | `/home/user/downloads` |
| `max-overall-download-limit` | 全局下载速度限制 | `10M`, `100K`, `0`(不限) |
| `max-concurrent-downloads` | 最大同时下载数 | `5` |
| `split` | 文件分块数 | `16` |
| `max-connection-per-server` | 每服务器连接数 | `16` |
| `min-split-size` | 最小分块大小 | `10M` |
| `user-agent` | 用户代理 | `Mozilla/5.0...` |
| `all-proxy` | 代理服务器 | `http://proxy:8080` |
| `timeout` | 超时时间（秒） | `60` |
| `continue` | 断点续传 | `true` |
| `enable-rpc` | 启用 RPC | `true` |
| `rpc-listen-port` | RPC 监听端口 | `6800` |
| `save-session` | 会话保存路径 | `/path/aria2.session` |

---

## 注意事项

1. **配置持久性**
   - 通过 RPC 修改的配置只在 aria2 运行期间有效
   - 重启 aria2 后会恢复配置文件中的设置
   - 如需永久修改，请编辑 `aria2.conf` 配置文件

2. **配置生效时间**
   - 全局配置修改后，对新创建的任务立即生效
   - 已在运行的任务不受全局配置修改影响
   - 任务级配置修改后立即对该任务生效

3. **配置值格式**
   - 速度限制可以使用 K（KB/s）或 M（MB/s）后缀
   - 布尔值使用 `true` 或 `false`
   - 数字直接使用阿拉伯数字

4. **错误处理**
   - 如果修改失败，检查配置项名称是否正确
   - 某些配置项在任务运行后无法修改
   - 使用 `get-global-option` 查看当前有效配置

---

## 示例工作流

```bash
# 1. 查看当前全局配置
python3 scripts/aria2_rpc.py get-global-option

# 2. 添加一个下载任务
GID=$(python3 scripts/aria2_rpc.py add-uri "http://example.com/largefile.zip" | grep GID | grep -oP '[a-f0-9]+')

# 3. 为该任务设置高速下载
python3 scripts/aria2_rpc.py set-option $GID split=32 max-connection-per-server=16

# 4. 监控下载进度
python3 scripts/aria2_rpc.py tell-status $GID

# 5. 下载完成后，恢复全局配置
python3 scripts/aria2_rpc.py set-global-option max-overall-download-limit=0
```

---

## 更多信息

- [aria2 官方文档 - RPC 方法](https://aria2.github.io/manual/en/html/aria2c.html#rpc-interface)
- [aria2 官方文档 - 配置选项](https://aria2.github.io/manual/en/html/aria2c.html#id3)
