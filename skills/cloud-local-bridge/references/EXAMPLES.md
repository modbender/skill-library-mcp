# Cloud-Local Bridge 使用示例

## 场景：云端分析 + 本地执行

假设你有一个需求：让云端 OpenClaw 接收用户请求，分析后让本地 OpenClaw 执行定时任务。

### 步骤 1：在本地启动 Bridge 服务

```bash
cd /root/.openclaw/workspace/skills/cloud-local-bridge/scripts

# 生成一个安全的 token
TOKEN=$(openssl rand -hex 32)
echo "Token: $TOKEN"

# 启动服务（端口 8080）
python3 bridge_server.py --port 8080 --token $TOKEN
```

### 步骤 2：在云端配置连接信息

创建 `~/.openclaw/cloud-bridge.json`：

```json
{
  "local_server": "http://192.168.1.100:8080",
  "token": "YOUR_GENERATED_TOKEN"
}
```

### 步骤 3：云端发送命令

在云端 OpenClaw 中，使用 HTTP 请求：

```bash
# 示例：让本地添加一个定时提醒
curl -X POST http://192.168.1.100:8080/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "command": "openclaw cron add --name \\"喝水提醒\\" --at \\"30m\\" --message \\"该喝水啦！\\" --session isolated --delete-after-run",
    "timeout": 60
  }'
```

### 步骤 4：使用 Python 客户端

```python
from bridge_client import BridgeClient

client = BridgeClient(
    server_url="http://192.168.1.100:8080",
    token="YOUR_TOKEN"
)

# 获取本地状态
status = client.get_status()
print(status)

# 执行命令
result = client.execute("openclaw cron list")
print(result)

# 读取本地文件
content = client.read_file("/root/.openclaw/memory/2026-02-20.md")
print(content)
```

## 场景 2：文件同步

### 上传本地文件到云端存储

```bash
# 在本地
python3 bridge_client.py --server http://localhost:8080 --token TOKEN upload /path/to/screenshot.png
```

### 从云端拉取配置

```python
# 在云端
import requests

response = requests.post(
    "http://LOCAL_IP:8080/file",
    json={
        "action": "read",
        "path": "/root/.openclaw/config.json"
    },
    headers={"Authorization": "Bearer TOKEN"}
)

config = response.json()
print(config)
```

## 场景 3：多设备协同

```
用户 → 云端 OpenClaw → (分析) → 本地 OpenClaw 1 (执行任务)
                                   ↓
                              本地 OpenClaw 2 (另一台设备)
```

## 完整工作流示例

```python
import json
import requests

LOCAL_SERVER = "http://192.168.1.100:8080"
TOKEN = "your-secure-token"

def execute_on_local(command):
    """在本地执行命令"""
    response = requests.post(
        f"{LOCAL_SERVER}/execute",
        json={"command": command, "timeout": 60},
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    return response.json()

def get_local_memory(date):
    """读取本地某天的记忆文件"""
    response = requests.post(
        f"{LOCAL_SERVER}/file",
        json={"action": "read", "path": f"/root/.openclaw/memory/{date}.md"},
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    return response.json()

# 1. 查询本地已有的提醒
print("=== 本地定时任务 ===")
result = execute_on_local("openclaw cron list")
print(json.dumps(result, indent=2))

# 2. 读取本地记忆
print("\n=== 本地记忆 ===")
memory = get_local_memory("2026-02-20")
print(memory.get('content', '无'))

# 3. 让本地执行新任务
print("\n=== 添加新任务 ===")
result = execute_on_local(
    'openclaw cron add --name "测试" --at "1h" --message "来自云端的提醒" --session isolated --delete-after-run'
)
print(json.dumps(result, indent=2))
```

## 注意事项

1. **网络连通性**：确保云端能访问到本地的 IP 和端口
2. **安全**：使用强 Token，生产环境建议加 HTTPS
3. **防火墙**：本地需要开放对应端口
4. **权限**：确保运行 Bridge 的用户有足够的权限执行命令
