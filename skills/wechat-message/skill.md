---
name: wechat-rpa
description: 基于桌面端UI自动化的微信操作工具，支持Windows/macOS双平台，可实现微信窗口管理、联系人操作、消息收发、聊天记录提取及自动化智能回复.
---
# 微信桌面自动化工具

基于桌面端UI自动化的微信操作工具，支持Windows/macOS双平台，可实现微信窗口管理、联系人操作、消息收发、聊天记录提取及自动化智能回复。

⚠️ **重要声明**：本工具仅用于个人合法合规的微信操作自动化，请勿用于批量群发、骚扰他人等违规场景。使用前请确保遵守微信用户协议及相关法律法规。

## 支持平台

- ✅ Windows (支持微信Windows版所有主流版本)
- ✅ macOS (支持微信macOS版)
- ❌ Linux (暂不支持)

## 前提条件

### 1. 环境依赖安装
```bash
# 基础核心依赖
pip install pyautogui pillow opencv-python numpy pyperclip requests psutil

# Windows 额外依赖
pip install pywin32

# macOS 额外依赖
pip install pyobjc-framework-Quartz pyobjc-core pyobjc
```

### 2. 权限配置
- **Windows**：无需额外权限，确保微信已安装并登录
- **macOS**：授予终端/IDE"辅助功能"和"屏幕录制"权限：
  系统设置 → 隐私与安全 → 辅助功能 → 添加终端/IDE
  系统设置 → 隐私与安全 → 屏幕录制 → 添加终端/IDE

### 3. 微信准备
- 确保微信已安装并完成登录
- 建议将微信窗口最大化运行（提升定位准确性）
- 关闭微信的"消息免打扰"等可能影响界面显示的设置

### 4. 自动回复的Authentication

All requests require the CHAT_API_KEY in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

**Environment Variable:** Set your API key as `CHAT_API_KEY`:

```bash
export CHAT_API_KEY="YOUR_API_KEY"
```
## 使用方法

### 启动微信
```bash
py wechat.py start
```

### 激活微信窗口
```bash
py wechat.py activate
```

### 搜索联系人并发送消息
```bash
py wechat.py search_and_send --contact 张三 --message "你好，这是自动发送的消息"
```

### 获取聊天记录
```bash
py wechat.py get_history --contact 李四 --limit 10
```

### 自动处理联系人消息（智能回复）
```bash
# 基础用法
py wechat.py auto_process --api_key "你的AI接口密钥"

# 自定义轮询次数和API地址
py wechat.py auto_process --polling_times 20 --api_url "http://127.0.0.1:8000/api/chat/message" --api_key "密钥"
```

### 查看帮助
```bash
py wechat.py help
```

## 命令参考

| 命令 | 功能 | 示例 |
|------|------|------|
| `start` | 启动微信客户端 | `py wechat.py start` |
| `activate` | 激活并最大化微信窗口 | `py wechat.py activate --title 微信` |
| `search_and_send` | 搜索联系人并发送消息 | `py wechat.py search_and_send --contact 张三 --message 您好` |
| `get_history` | 获取指定联系人聊天记录 | `py wechat.py get_history --contact 李四 --limit 15` |
| `auto_process` | 自动轮询联系人并智能回复 | `py wechat.py auto_process --polling_times 10 --api_key xxx` |
| `help` | 查看帮助信息 | `py wechat.py help` |

## 核心功能说明

### 1. 微信进程与窗口管理
| 功能 | 说明 |
|------|------|
| 进程检测 | 自动检测微信是否正在运行 |
| 自动启动 | 查找微信安装路径并启动，支持多路径适配 |
| 窗口激活 | 定位微信窗口并激活，支持最大化、前置显示 |
| 区域定位 | 自动识别微信界面各功能区域（输入框、发送按钮等） |

### 2. 联系人操作
| 功能 | 说明 |
|------|------|
| 精准搜索 | 通过搜索框定位联系人，支持剪贴板输入避免输入失败 |
| 列表点击 | 按索引点击联系人列表，支持边界检查 |
| 状态记忆 | 记录当前打开的联系人，避免重复操作 |

### 3. 消息处理
| 功能 | 说明 |
|------|------|
| 安全输入 | 支持剪贴板粘贴和逐字符输入，避免输入异常 |
| 消息发送 | 精准点击发送按钮，支持自然鼠标移动轨迹 |
| 记录提取 | 通过OCR和右键复制提取聊天记录，区分收发方向 |
| 新消息检测 | 自动识别最新收到的消息，过滤自己发送的内容 |

### 4. 自动化回复
| 功能 | 说明 |
|------|------|
| 轮询检测 | 循环检查多个联系人的新消息 |
| AI接口集成 | 调用自定义AI接口获取回复内容 |
| 批量发送 | 支持多条回复依次发送，可自定义发送间隔 |
| 异常处理 | 失败自动重试，错误日志完整记录 |

## 配置说明

### 界面区域配置
- 首次运行`activate`命令会自动生成`config/wechat_regions.json`
- 包含微信界面各区域的坐标和尺寸参数
- 不同平台配置自动区分，避免混用

### 自定义参数
| 参数 | 功能 | 示例 |
|------|------|------|
| `--contact` | 指定联系人名称 | `--contact 张三` |
| `--message` | 发送的消息内容 | `--message "您好"` |
| `--limit` | 聊天记录获取数量 | `--limit 10` |
| `--polling_times` | 自动轮询次数 | `--polling_times 20` |
| `--api_url` | AI接口地址 | `--api_url http://localhost:8000/api/chat/message` |
| `--api_key` | AI接口密钥 | `--api_key "your-api-key"` |
| `--title` | 微信窗口标题 | `--title "微信"` |

## 技术说明

### 核心技术点
- **跨平台适配**：通过`platform`模块区分Windows/macOS，适配不同的窗口管理API
- **精准定位**：基于微信界面固定布局计算各功能区域坐标，无需图像识别
- **人机模拟**：贝塞尔曲线模拟人类鼠标移动轨迹，随机偏移避免被检测
- **安全操作**：所有点击/输入操作均有异常处理，失败自动降级为基础操作
- **剪贴板管理**：使用前保存、使用后恢复剪贴板内容，避免覆盖用户数据

### 关键模块说明
| 模块 | 功能 |
|------|------|
| `WeChatRegion` | 数据类，定义微信界面所有区域的参数和坐标 |
| `WeChatAutomation` | 核心类，封装所有自动化操作方法 |
| `_safe_click` | 安全点击方法，模拟人类操作行为 |
| `_locate_message_bubbles` | 消息气泡定位，基于OpenCV识别消息区域 |
| `auto_process_contacts` | 自动化主方法，实现轮询和智能回复 |

### 日志与调试
- 日志文件：`wechat_automation.log`（包含详细操作记录）
- 调试目录：`debug/`（存储截图等调试信息）
- 所有关键操作均有日志输出，便于问题定位

## 常见问题

**错误：无法激活微信窗口**
→ 确认微信已运行并登录，或先执行`start`命令启动微信
→ macOS需授予辅助功能权限

**错误：点击位置不准确**
→ 确保微信窗口已最大化
→ 删除`config/wechat_regions.json`重新生成区域配置
→ 检查微信界面布局是否为默认样式

**错误：剪贴板操作失败**
→ Windows：安装`pywin32`库（`pip install pywin32`）
→ macOS：确保终端有剪贴板访问权限

**错误：消息发送成功但对方未收到**
→ 检查输入框是否真正获得焦点
→ 增加发送后的等待时间（修改代码中`time.sleep`参数）

**错误：AI接口调用失败**
→ 检查API地址和密钥是否正确
→ 确认接口支持POST请求，且返回格式符合要求
→ 检查网络连接和接口权限

**微信界面更新后工具失效**
→ 更新`WeChatRegion`中的尺寸参数
→ 重新运行`activate`生成新的区域配置

## 隐私与安全

- ✅ 所有操作均在本地完成，不上传任何数据到网络
- ✅ 仅访问微信界面，不读取微信数据库文件
- ✅ 剪贴板内容使用后自动恢复，避免信息泄露
- ✅ 操作日志仅保存在本地，可随时删除
- ⚠️ 自动化操作可能违反微信用户协议，请谨慎使用
- ⚠️ 请勿用于商业推广、垃圾信息发送等违规行为

## 扩展与定制

### 自定义联系人列表
修改`auto_process_contacts`调用处的`contact_list`参数：
```python
contact_list = ["客户A", "客户B", "工作群", "家人群"]
```

### 调整操作速度
修改`_safe_click`中的`move_duration`参数（单位：秒）：
```python
# 减慢移动速度（更接近人类）
self._safe_click(x, y, move_duration=0.8)

# 加快移动速度（提高效率）
self._safe_click(x, y, move_duration=0.2)
```

### 适配不同微信版本
修改`WeChatRegion`中的尺寸参数：
```python
# 调整侧边栏宽度
sidebar_width: int = 65  # 默认60

# 调整联系人高度
contact_item_height: int = 75  # 默认70
```

### 扩展功能
- 可添加文件发送功能（点击文件按钮→选择文件→确认发送）
- 可添加图片识别功能（结合OCR提取图片中的文字）
- 可添加定时发送功能（结合`schedule`库实现定时操作）

## 免责声明

本工具仅用于学习和研究目的，请勿用于商业或违规用途。使用本工具产生的一切后果由使用者自行承担，作者不承担任何责任。