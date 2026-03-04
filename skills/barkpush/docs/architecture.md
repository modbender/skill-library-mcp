# Bark Push Skill - Python 模块架构设计

## 模块概览

Bark Push Skill 采用模块化架构设计，将功能划分为 7 个独立模块，每个模块负责特定的职责，通过清晰的接口进行交互。

### 模块关系图

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                   (命令行入口 CLI Entry)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  command_handler.py                          │
│                   (命令处理器 Command Handler)                 │
│  解析命令 → 路由到相应模块 → 整合结果 → 返回格式化输出          │
└────┬────────┬─────────┬─────────┬─────────┬────────┬────────┘
     │        │         │         │         │        │
     ▼        ▼         ▼         ▼         ▼        ▼
┌─────────┐ ┌────────┐ ┌───────┐ ┌────────┐ ┌──────┐ ┌──────┐
│ config  │ │content │ │ user  │ │history │ │bark  │ │utils │
│_manager │ │_parser │ │_mgr   │ │_manager│ │_api  │ │      │
└─────────┘ └────────┘ └───────┘ └────────┘ └──────┘ └──────┘
     │                     │         │         │
     └─────────────────────┴─────────┴─────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │   config.json           │
              │   history.json          │
              │   (数据持久化)           │
              └─────────────────────────┘
```

## 模块职责详细设计

### 1. main.py - 主入口模块

**职责**：
- 作为命令行工具的入口点
- 解析命令行参数（使用 argparse）
- 调用 CommandHandler 处理用户命令
- 格式化输出结果到控制台
- 处理全局异常和错误日志

**主要功能**：
```
- parse_arguments() - 解析命令行参数
- main() - 主函数入口
- format_output() - 格式化输出结果
- handle_exception() - 全局异常处理
```

**依赖关系**：
- 依赖：command_handler.py, utils.py
- 被依赖：无（顶层模块）

**设计要点**：
- 使用 argparse 构建清晰的命令行接口
- 支持 --help, --version 等标准参数
- 提供友好的错误提示和使用示例
- 支持详细日志模式（--verbose）

---

### 2. command_handler.py - 命令处理器模块

**职责**：
- 解析用户命令类型（push, update, delete, list, help）
- 验证命令参数的完整性和有效性
- 调度相应模块处理具体业务逻辑
- 整合各模块返回的结果
- 返回统一格式的结果对象

**主要功能**：
```
CommandHandler 类：
- handle(command, args) - 主处理函数
- handle_push(args) - 处理推送命令
- handle_update(args) - 处理更新命令
- handle_delete(args) - 处理删除命令
- handle_list(args) - 处理列表查询命令
- handle_help(args) - 处理帮助命令
- validate_args(command, args) - 验证参数
- build_result(status, message, data) - 构建结果对象
```

**依赖关系**：
- 依赖：config_manager, content_parser, user_manager, history_manager, bark_api, utils
- 被依赖：main.py

**设计要点**：
- 命令路由采用字典映射实现（command -> handler_method）
- 参数验证独立于业务逻辑，便于测试
- 结果对象统一格式：{ success, message, data, error_details }
- 支持批量操作（多用户推送）

**命令类型枚举**：
```python
class CommandType(Enum):
    PUSH = "push"           # 推送新消息
    UPDATE = "update"       # 更新已推送的消息
    DELETE = "delete"       # 删除已推送的消息
    LIST_USERS = "list_users"       # 列出所有用户
    LIST_GROUPS = "list_groups"     # 列出所有分组
    LIST_HISTORY = "list_history"   # 列出历史记录
    HELP = "help"           # 显示帮助信息
```

---

### 3. config_manager.py - 配置管理模块

**职责**：
- 加载和解析 config.json 配置文件
- 验证配置文件的完整性和有效性
- 提供配置项的读取接口
- 支持配置文件不存在时创建默认配置
- 提供配置热更新功能（可选）

**主要功能**：
```
ConfigManager 类：
- load_config(config_path) - 加载配置文件
- validate_config() - 验证配置完整性
- get_default_push_url() - 获取默认推送地址
- get_users() - 获取用户别名映射
- get_user_device_key(alias) - 获取指定用户的 device_key
- get_defaults() - 获取默认参数字典
- get_groups() - 获取分组列表
- get_ciphertext() - 获取加密密文
- get_history_limit() - 获取历史记录限制
- is_update_enabled() - 检查是否启用更新功能
- create_default_config(path) - 创建默认配置文件
```

**依赖关系**：
- 依赖：utils.py（用于文件操作和 JSON 解析）
- 被依赖：command_handler, user_manager, bark_api, history_manager

**设计要点**：
- 单例模式确保配置只加载一次
- 配置加载失败时提供友好的错误提示和默认配置示例
- 支持环境变量覆盖配置项（如 BARK_PUSH_URL）
- 配置验证使用 JSON Schema 验证器

**配置路径优先级**：
```
1. 命令行参数指定的路径（--config）
2. 当前工作目录的 config.json
3. ~/.bark-push/config.json（用户主目录）
4. 如果都不存在，创建默认配置到 ~/.bark-push/config.json
```

---

### 4. bark_api.py - Bark API 调用模块

**职责**：
- 封装 Bark API 的 HTTP 请求逻辑
- 构建推送 URL（包含所有参数）
- 处理 URL 编码和特殊字符转义
- 发送 HTTP GET 请求并解析响应
- 实现重试机制和超时控制
- 处理网络异常和 API 错误

**主要功能**：
```
BarkAPI 类：
- push(device_key, title, body, **params) - 发送推送
- build_url(device_key, title, body, **params) - 构建推送 URL
- send_request(url, retries=3, timeout=10) - 发送 HTTP 请求
- parse_response(response) - 解析 API 响应
- handle_error(error) - 处理请求错误
```

**依赖关系**：
- 依赖：requests 库, utils.py
- 被依赖：command_handler

**设计要点**：
- 使用 urllib.request 发送 HTTP POST JSON 请求
- 请求体使用 JSON 编码并设置 Content-Type
- 重试策略：指数退避（1s, 2s, 4s），最多 3 次
- 超时设置：连接超时 5s，读取超时 10s
- 响应状态码处理：200 成功，400 参数错误，500 服务器错误

**Bark API 参数映射**：
```python
BARK_PARAMS = {
    'title': str,           # 标题
    'body': str,            # 正文
    'level': str,           # 级别
    'badge': int,           # 角标
    'sound': str,           # 声音
    'icon': str,            # 图标 URL
    'group': str,           # 分组
    'url': str,             # 点击后打开的 URL
    'image': str,           # 图片 URL
    'copy': str,            # 复制内容
    'autoCopy': bool,       # 自动复制
    'call': bool,           # 呼叫
    'isArchive': bool,      # 归档
    'volume': int,          # 音量
    'ciphertext': str,      # 加密密文
}
```

**请求示例**：
```
POST https://api.day.app/push
Content-Type: application/json; charset=utf-8

{"device_key":"xxx","title":"标题","body":"内容"}
```

---

### 5. content_parser.py - 内容识别模块

**职责**：
- 识别用户输入的内容类型（纯图片、纯链接、纯文本、混合）
- 提取内容中的图片 URL、链接 URL 和文本片段
- 对混合内容生成 Markdown 格式输出
- 提供自动标题生成功能（基于内容摘要）
- 为不同内容类型选择最优推送方式

**主要功能**：
```
ContentParser 类：
- parse(raw_content) - 解析原始内容
- detect_content_type(content) - 检测内容类型
- extract_images(content) - 提取图片 URL
- extract_urls(content) - 提取链接 URL
- extract_text(content) - 提取文本内容
- format_as_markdown(images, urls, text) - 格式化为 Markdown
- generate_title(content) - 自动生成标题
- generate_subtitle(content) - 自动生成副标题
```

**依赖关系**：
- 依赖：utils.py（正则表达式工具）
- 被依赖：command_handler

**设计要点**：
- 使用正则表达式识别 URL 和图片 URL 模式
- 图片 URL 模式：`https?://.*\.(jpg|jpeg|png|gif|webp|bmp)`
- 链接 URL 模式：`https?://[^\s]+`
- 内容类型优先级：纯图片 > 纯链接 > 纯文本 > 混合
- 标题生成：取内容前 20 字符（中文）或前 50 字符（英文）
- Markdown 格式化：图片使用 `![](url)`，链接使用 `[](url)`

**内容类型判断逻辑**：
```python
def detect_content_type(content: str) -> ContentType:
    images = extract_images(content)
    urls = extract_urls(content)
    text = extract_text(content)
    
    if images and not urls and not text:
        return ContentType.IMAGE_ONLY
    elif urls and not images and not text:
        return ContentType.URL_ONLY
    elif text and not images and not urls:
        return ContentType.TEXT_ONLY
    else:
        return ContentType.MIXED
```

**ParsedContent 数据结构**：
```python
@dataclass
class ParsedContent:
    content_type: ContentType    # 内容类型
    images: List[str]            # 图片 URL 列表
    urls: List[str]              # 链接 URL 列表
    text: str                    # 文本内容
    markdown: Optional[str]      # Markdown 格式（混合内容时）
    auto_title: str              # 自动生成的标题
    auto_subtitle: str           # 自动生成的副标题
```

---

### 6. history_manager.py - 历史记录管理模块

**职责**：
- 加载和保存 history.json 历史记录文件
- 实现推送记录的增加、查询、更新和删除操作
- 维护 FIFO 队列，超过限制自动删除最旧记录
- 提供按 push_id 和 device_key 的快速查询
- 维护内存索引，提高查询性能

**主要功能**：
```
HistoryManager 类：
- load_history(history_path) - 加载历史记录
- save_history() - 保存历史记录到文件
- add_record(record) - 添加新记录
- get_record(push_id) - 根据 ID 获取记录
- update_record(push_id, updates) - 更新记录
- delete_record(push_id) - 删除记录
- query_by_user(user_alias) - 查询指定用户的记录
- query_by_time_range(start, end) - 查询时间范围内的记录
- get_recent_records(limit) - 获取最近的记录
- cleanup_old_records() - 清理超过限制的旧记录
- build_index() - 构建内存索引
```

**依赖关系**：
- 依赖：utils.py, config_manager.py
- 被依赖：command_handler

**设计要点**：
- FIFO 策略：按 timestamp 排序，删除最旧的记录
- 内存索引：维护 push_id -> record 和 user_alias -> [push_ids] 的映射
- 文件操作：使用文件锁避免并发写入冲突
- 性能优化：查询操作优先使用索引，避免全表扫描
- 数据一致性：每次修改后立即保存到文件

**FIFO 清理逻辑**：
```python
def cleanup_old_records(self):
    """清理超过限制的旧记录"""
    limit = self.config_manager.get_history_limit()
    if len(self.records) > limit:
        # 按时间戳排序，删除最旧的记录
        self.records.sort(key=lambda r: r['timestamp'])
        removed_count = len(self.records) - limit
        self.records = self.records[removed_count:]
        self.build_index()  # 重建索引
        self.save_history()
```

**记录 ID 生成策略**：
```python
def generate_push_id() -> str:
    """生成唯一的推送 ID"""
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"push_{timestamp}_{random_str}"
```

---

### 7. user_manager.py - 用户管理模块

**职责**：
- 解析用户别名和 device_key
- 支持单用户、多用户（逗号分隔）和全员推送（"all"）
- 验证用户存在性
- 返回用户列表供选择
- 提供别名到 device_key 的映射功能

**主要功能**：
```
UserManager 类：
- parse_users(user_input) - 解析用户输入
- get_device_keys(user_aliases) - 获取用户的 device_key 列表
- validate_users(user_aliases) - 验证用户是否存在
- list_users() - 列出所有用户
- is_all_users(user_input) - 判断是否为全员推送
- resolve_alias(alias) - 解析单个用户别名
```

**依赖关系**：
- 依赖：config_manager.py, utils.py
- 被依赖：command_handler

**设计要点**：
- 支持多种输入格式：单用户（alice）、多用户（alice,bob,charlie）、全员（all）
- 别名查找优先级：精确匹配 > 模糊匹配 > 报错
- 用户不存在时返回可用用户列表和友好提示
- 支持 device_key 直接推送（无需配置别名）

**用户解析逻辑**：
```python
def parse_users(self, user_input: str) -> List[Tuple[str, str]]:
    """
    解析用户输入，返回 (alias, device_key) 的列表
    
    Args:
        user_input: 用户输入字符串（alice, alice,bob, all, device_key_xxx）
        
    Returns:
        [(alias, device_key), ...] 列表
        
    Raises:
        ValueError: 用户不存在或输入格式错误
    """
    if user_input.lower() == 'all':
        return self.get_all_users()
    
    user_aliases = [u.strip() for u in user_input.split(',')]
    result = []
    
    for alias in user_aliases:
        device_key = self.resolve_alias(alias)
        if device_key:
            result.append((alias, device_key))
        else:
            raise ValueError(f"用户 '{alias}' 不存在，可用用户：{self.list_users()}")
    
    return result
```

---

### 8. utils.py - 工具函数模块

**职责**：
- 提供通用的工具函数
- 避免代码重复
- 封装常用的字符串处理、时间转换、URL 编码等功能

**主要功能**：
```
工具函数：
- generate_title_from_content(content, max_length) - 自动生成标题
- format_markdown(images, urls, text) - 格式化 Markdown
- timestamp_to_datetime(timestamp) - 时间戳转日期时间
- datetime_to_timestamp(datetime_str) - 日期时间转时间戳
- url_encode(text) - URL 编码
- truncate_text(text, length) - 截断文本
- validate_url(url) - 验证 URL 格式
- validate_email(email) - 验证邮箱格式
- parse_json_safely(json_str) - 安全解析 JSON
- format_file_size(size_bytes) - 格式化文件大小
- get_config_path() - 获取配置文件路径
- ensure_dir_exists(path) - 确保目录存在
```

**依赖关系**：
- 依赖：标准库（re, json, datetime, pathlib 等）
- 被依赖：所有模块

**设计要点**：
- 所有函数都是纯函数，无副作用
- 提供详细的文档字符串和类型注解
- 异常处理：返回默认值或抛出明确的异常
- 单元测试覆盖率 100%

---

## 模块交互流程

### 推送消息流程

```
1. main.py 接收命令行参数
   ↓
2. CommandHandler.handle_push() 处理推送命令
   ↓
3. ContentParser.parse() 识别内容类型
   ↓
4. UserManager.parse_users() 解析用户
   ↓
5. ConfigManager.get_defaults() 获取默认参数
   ↓
6. BarkAPI.push() 发送推送（循环多个用户）
   ↓
7. HistoryManager.add_record() 保存历史记录
   ↓
8. 返回结果给 main.py 格式化输出
```

### 更新消息流程

```
1. main.py 接收更新命令参数
   ↓
2. CommandHandler.handle_update() 处理更新命令
   ↓
3. HistoryManager.get_record() 查询历史记录
   ↓
4. 验证 push_id 和 user 是否匹配
   ↓
5. ContentParser.parse() 解析新内容
   ↓
6. BarkAPI.push() 发送新推送（使用原参数）
   ↓
7. HistoryManager.update_record() 更新历史记录
   ↓
8. 返回结果给 main.py 格式化输出
```

### 查询用户列表流程

```
1. main.py 接收列表命令
   ↓
2. CommandHandler.handle_list() 处理列表命令
   ↓
3. UserManager.list_users() 获取用户列表
   ↓
4. 返回用户列表给 main.py 格式化输出
```

## 错误处理策略

### 异常分类

```python
class BarkPushError(Exception):
    """基础异常类"""
    pass

class ConfigError(BarkPushError):
    """配置相关错误"""
    pass

class NetworkError(BarkPushError):
    """网络请求错误"""
    pass

class ValidationError(BarkPushError):
    """参数验证错误"""
    pass

class HistoryError(BarkPushError):
    """历史记录操作错误"""
    pass

class UserError(BarkPushError):
    """用户管理错误"""
    pass
```

### 错误处理原则

1. **配置错误**：提供详细的错误信息和默认配置示例，引导用户修正
2. **网络错误**：实现重试机制，记录失败详情，部分失败不影响其他用户
3. **验证错误**：返回清晰的参数错误信息和正确格式示例
4. **历史记录错误**：容错处理，记录损坏时重建索引或恢复默认状态
5. **用户错误**：返回可用用户列表，提示正确的输入格式

## 性能优化策略

### 1. 配置缓存
- ConfigManager 使用单例模式，配置只加载一次
- 配置修改后支持热更新，无需重启程序

### 2. 历史记录索引
- 维护内存索引：push_id -> record, user_alias -> [push_ids]
- 查询复杂度从 O(n) 降低到 O(1)

### 3. 并发推送
- 使用 ThreadPoolExecutor 并发向多个用户推送
- 推送时间从 O(n) 降低到 O(1)（相对于用户数）

### 4. 请求优化
- 使用 requests.Session() 复用 HTTP 连接
- 设置合理的超时时间，避免长时间等待

### 5. 文件 I/O 优化
- 历史记录批量写入，避免频繁磁盘操作
- 使用 JSON 压缩存储，减少文件大小

## 测试策略

### 单元测试

每个模块独立测试，覆盖率目标 90%+：

- **test_config_manager.py**：测试配置加载、验证、默认值处理
- **test_content_parser.py**：测试内容识别、Markdown 生成、标题生成
- **test_user_manager.py**：测试用户解析、别名解析、全员推送
- **test_history_manager.py**：测试记录增删改查、FIFO 清理、索引构建
- **test_bark_api.py**：使用 mock 测试 HTTP 请求、重试机制、响应解析
- **test_utils.py**：测试所有工具函数的边界条件

### 集成测试

测试模块间的协作：

- **test_push_workflow.py**：测试完整的推送流程
- **test_update_workflow.py**：测试消息更新流程
- **test_error_handling.py**：测试各种错误场景的处理

### 端到端测试

模拟真实用户场景：

- 推送单个用户
- 推送多个用户
- 推送全部用户
- 更新已推送的消息
- 删除已推送的消息
- 查询历史记录

## 扩展性设计

### 插件接口

预留插件接口，支持未来扩展：

```python
class BarkPushPlugin:
    """插件基类"""
    def on_before_push(self, data):
        """推送前钩子"""
        pass
    
    def on_after_push(self, result):
        """推送后钩子"""
        pass
    
    def on_error(self, error):
        """错误处理钩子"""
        pass
```

### 扩展功能建议

- **Webhook 支持**：推送结果回调到指定 URL
- **定时推送**：支持 cron 表达式定时推送
- **模板消息**：支持消息模板，快速发送常用消息
- **推送统计**：统计推送成功率、失败率、用户活跃度
- **多账户支持**：支持多个 Bark 账户管理
- **消息队列**：支持消息队列，异步推送，提高性能

## 安全配置说明

为解决敏感信息（如 device_key、ciphertext）在配置文件中明文存储的安全风险，Bark Push Skill 支持通过环境变量配置敏感信息。

### 环境变量优先级

环境变量的优先级高于 `config.json` 配置文件。如果环境变量中存在对应配置，将覆盖配置文件中的值。

### 支持的环境变量

| 环境变量名 | 描述 | 示例 |
| --- | --- | --- |
| `BARK_USERS` | JSON 格式的用户配置字符串，用于覆盖 `users` 字段 | `'{"alice": "device_key_xxx", "bob": "device_key_yyy"}'` |
| `BARK_CIPHERTEXT` | 加密推送所需的密钥，覆盖 `ciphertext` 字段 | `"my_secret_key"` |

### 配置示例

在 Linux/macOS 中：

```bash
export BARK_USERS='{"alice": "key1", "bob": "key2"}'
export BARK_CIPHERTEXT="secret"
python main.py push alice "Hello"
```

在 Windows PowerShell 中：

```powershell
$env:BARK_USERS='{"alice": "key1", "bob": "key2"}'
$env:BARK_CIPHERTEXT="secret"
python main.py push alice "Hello"
```

## 发布与安装

### 发布到 ClawHub

前置条件：仓库根目录包含 SKILL.md，并填写完整元数据。

```bash
npm i -g clawhub
clawhub login
clawhub publish ./bark_bot --slug barkpush --name "barkpush" --version 1.2.0 --changelog "更新说明"
```

### 安装到 OpenClaw

推荐使用 npx 方式：

```bash
npx clawhub@latest install barkpush
```

或使用已安装的 CLI：

```bash
clawhub install barkpush
```

## 总结

该架构设计遵循以下原则：

1. **单一职责**：每个模块只负责一个功能领域
2. **低耦合**：模块间通过接口交互，依赖关系清晰
3. **高内聚**：相关功能集中在同一模块
4. **可测试**：每个模块可独立测试
5. **可扩展**：预留扩展接口，支持插件化
6. **可维护**：代码结构清晰，注释完整

通过这种架构设计，Bark Push Skill 具备良好的可维护性、可扩展性和性能表现。
