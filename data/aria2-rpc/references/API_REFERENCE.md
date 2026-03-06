# Aria2 RPC API 参考

## RPC 方法列表

| 方法 | 说明 |
|------|------|
| `aria2.addUri` | 添加 HTTP/FTP/Magnet 下载 |
| `aria2.addTorrent` | 添加 Torrent 下载 |
| `aria2.addMetalink` | 添加 Metalink 下载 |
| `aria2.tellActive` | 获取活动下载列表 |
| `aria2.tellWaiting` | 获取等待下载列表 |
| `aria2.tellStopped` | 获取已停止下载列表 |
| `aria2.tellStatus` | 获取任务详细信息 |
| `aria2.remove` | 删除任务 |
| `aria2.forceRemove` | 强制删除任务 |
| `aria2.pause` | 暂停任务 |
| `aria2.forcePause` | 强制暂停任务 |
| `aria2.unpause` | 继续任务 |
| `aria2.getGlobalStat` | 获取全局统计 |
| `aria2.getOption` | 获取任务级配置 |
| `aria2.getGlobalOption` | 获取全局配置 |
| `aria2.changeOption` | 修改任务级配置 |
| `aria2.changeGlobalOption` | 修改全局配置 |

## 官方文档

详见 [aria2 RPC 官方文档](https://aria2.github.io/manual/en/html/aria2c.html#rpc-interface)

## GID 说明

每个下载任务有唯一的 GID（全局 ID），用于后续操作。GID 是 16 字符的十六进制字符串。

## 故障排除

### 连接被拒绝

```bash
# 检查 aria2 是否运行
ps aux | grep aria2

# 检查端口是否监听
netstat -tlnp | grep 6800

# 检查防火墙
sudo ufw allow 6800/tcp
```

### 认证失败

确保 `rpc-secret` 配置正确，调用时传入正确的 token：
```bash
python3 scripts/aria2_rpc.py add-uri "http://example.com/file.zip" --rpc-secret correct-token
```

### 下载失败

查看 aria2 日志：
```bash
tail -f ~/.aria2/aria2.log
```