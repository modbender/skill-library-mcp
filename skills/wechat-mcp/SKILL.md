---
name: wechat-mcp
version: 1.0.0
description: Windows 电脑端微信消息监控与发送 MCP，实现在微信上给指定联系人发送消息
---

# WeChat MCP

Windows 电脑端微信消息监控与发送 MCP。

## 功能

- 📸 截取微信窗口截图
- 👤 搜索并打开联系人聊天窗口
- ✉️ 给指定联系人发送消息
- 🔍 支持独立聊天窗口识别和消息发送

## 安装

需要先安装 Python 依赖：

```bash
pip install pyautogui pygetwindow pillow pyperclip opencv-python
```

## 使用方法

### 1. 发送消息到指定联系人

```python
from server import send_message_to_contact

# 给指定联系人发送消息（完整流程：搜索->打开聊天->发送）
send_message_to_contact("联系人名称", "消息内容")
```

### 2. 给当前聊天窗口发送消息

```python
from server import send_message_to_current

# 给当前已打开的聊天窗口发送消息
send_message_to_current("消息内容")
```

### 3. 获取微信状态

```python
from server import get_wechat_status

status = get_wechat_status()
print(status)
# {'status': 'running', 'title': '微信', 'position': {'x': 0, 'y': 0}, 'size': {'width': 1920, 'height': 1080}}
```

## MCP 工具

如果通过 MCP 协议调用：

```json
{
  "tools": [
    {
      "name": "wechat_get_status",
      "description": "获取微信窗口状态"
    },
    {
      "name": "wechat_send_message",
      "description": "给当前聊天窗口发送消息",
      "inputSchema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "description": "消息内容"}
        },
        "required": ["message"]
      }
    }
  ]
}
```

## 注意事项

1. 微信窗口需要保持打开状态
2. 发送消息时会自动激活微信窗口
3. 中文输入需要确保系统中文输入法正常工作
4. 支持给独立聊天窗口（单独打开的 Dragon 窗口）发送消息

## 文件结构

```
wechat-mcp/
├── server.py          # MCP 服务器主程序
├── test_wechat.py    # 测试工具
├── requirements.txt   # Python 依赖
└── README.md         # 说明文档
```
