# LSP 协议详解

## 什么是 LSP

**Language Server Protocol (LSP)** 是由 Microsoft 开发的开放协议，用于编辑器/IDE 与语言服务器之间的通信。

## 核心架构

```
┌─────────────────┐         JSON-RPC         ┌─────────────────┐
│   编辑器/客户端   │ ←──────────────────────→ │   语言服务器     │
│  (VSCode/Nvim)  │      (stdin/stdout)      │  (pylsp/ts 等)  │
└─────────────────┘                          └─────────────────┘
```

## JSON-RPC 消息格式

### 请求格式

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "textDocument/completion",
  "params": {
    "textDocument": {"uri": "file:///path/to/file.py"},
    "position": {"line": 0, "character": 0}
  }
}
```

### 响应格式

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "isIncomplete": false,
    "items": [...]
  }
}
```

### 通知格式 (无响应)

```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didOpen",
  "params": {...}
}
```

## LSP 消息头

```
Content-Length: <length>\r\n
\r\n
<message-body>
```

## 核心能力

| 功能 | 方法 | 说明 |
|------|------|------|
| 自动补全 | `textDocument/completion` | 获取代码补全建议 |
| 跳转定义 | `textDocument/definition` | 查找符号定义 |
| 查找引用 | `textDocument/references` | 查找所有引用 |
| 悬停提示 | `textDocument/hover` | 获取符号信息 |
| 诊断检查 | `textDocument/publishDiagnostics` | 错误/警告通知 |
| 符号搜索 | `workspace/symbol` | 工作区符号搜索 |
| 格式化 | `textDocument/formatting` | 代码格式化 |
| 重命名 | `textDocument/rename` | 符号重命名 |
| 代码动作 | `textDocument/codeAction` | 快速修复等 |

## 生命周期

### 1. Initialize

客户端发送能力协商:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "processId": 12345,
    "rootUri": "file:///path/to/workspace",
    "capabilities": {...},
    "trace": "off"
  }
}
```

### 2. Initialized

服务器确认就绪:

```json
{
  "jsonrpc": "2.0",
  "method": "initialized",
  "params": {}
}
```

### 3. Document Open

文件打开时通知服务器:

```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didOpen",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/file.py",
      "languageId": "python",
      "version": 1,
      "text": "..."
    }
  }
}
```

### 4. Document Change

内容变更时同步:

```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didChange",
  "params": {
    "textDocument": {"uri": "...", "version": 2},
    "contentChanges": [{"text": "..."}]
  }
}
```

### 5. Shutdown

优雅退出:

```json
{"jsonrpc": "2.0", "id": 99, "method": "shutdown", "params": {}}
{"jsonrpc": "2.0", "method": "exit"}
```

## 文档同步模式

- **Full Sync**: 每次变更发送完整内容
- **Incremental Sync**: 只发送变更范围 (range + text)
- **None**: 服务器自行读取文件

## pylsp 特定实现

### 启动 pylsp

```bash
pylsp  # 默认 stdio 模式
```

### 诊断通知

诊断通过通知推送，而非响应:

```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/publishDiagnostics",
  "params": {
    "uri": "file:///path/to/file.py",
    "diagnostics": [
      {
        "source": "pyflakes",
        "range": {"start": {"line": 0, "character": 0}, "end": {...}},
        "message": "'os' imported but unused",
        "severity": 2
      }
    ]
  }
}
```

## 补全项类型

| kind | 类型 |
|------|------|
| 1 | 文本 |
| 2 | 方法 |
| 3 | 函数 |
| 4 | 构造器 |
| 5 | 字段 |
| 6 | 变量 |
| 7 | 类 |
| 8 | 接口 |
| 9 | 模块 |
| 10 | 属性 |

## 诊断严重性

| severity | 级别 |
|----------|------|
| 1 | Error |
| 2 | Warning |
| 3 | Information |
| 4 | Hint |

## 实现示例

### Python 客户端

```python
import subprocess
import json

def send_request(pylsp, method, params, req_id=None):
    request = {"jsonrpc": "2.0", "method": method, "params": params}
    if req_id:
        request["id"] = req_id
    
    content = json.dumps(request)
    header = f"Content-Length: {len(content)}\r\n\r\n"
    pylsp.stdin.write(header.encode() + content.encode())
    pylsp.stdin.flush()

def read_response(pylsp):
    content_length = 0
    while True:
        line = pylsp.stdout.readline()
        if line.startswith(b'Content-Length:'):
            content_length = int(line.split(b':')[1])
        if line == b'\r\n':
            break
    
    if content_length > 0:
        return json.loads(pylsp.stdout.read(content_length))
    return None
```

## 参考资料

- [LSP 官方文档](https://microsoft.github.io/language-server-protocol/)
- [JSON-RPC 2.0 规范](https://www.jsonrpc.org/specification)
- [pylsp GitHub](https://github.com/python-lsp/python-lsp-server)
