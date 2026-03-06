---
name: pywayne-helper
description: Project configuration management helper for YAML config files. Use when projects need cross-process/cross-file parameter sharing via a centralized config file. Supports automatic project root detection, nested config key management, and waiting mechanism for values set by other processes.
---

# Pywayne Helper

项目配置管理辅助工具，实现跨进程、跨文件的参数共享机制。

## Quick Start

```python
from pywayne.helper import Helper

# 初始化（自动检测调用者所在目录作为项目根目录）
helper = Helper()

# 进程 A：写入配置
helper.set_module_value('database', 'host', value='127.0.0.1')

# 进程 B：读取配置（自动等待直到值存在）
db_host = helper.get_module_value('database', 'host', max_waiting_time=10)
print(f"数据库主机: {db_host}")
```

## 跨进程/跨文件参数共享

Helper 通过项目根目录下的 YAML 配置文件实现参数共享：

```
project_root/
├── common_info.yaml          # 配置文件，自动创建
├── module_a/              # 模块 A
└── module_b/              # 模块 B
```

**工作原理**：
1. 任何模块初始化 Helper 实例，自动定位到项目根目录
2. 配置文件统一位于 `{project_root}/common_info.yaml`
3. 各模块通过 `set_module_value` 写入配置
4. 各模块通过 `get_module_value` 读取配置
5. 支持等待机制，确保读取到其他进程写入的值

**适用场景**：

| 场景 | 说明 |
|------|------|
| 多进程协作 | 进程 A 写配置，进程 B 读配置 |
| 分布式任务 | 主进程设置参数，子进程读取执行 |
| 配置传递 | 程序启动时写入配置，后续模块读取 |
| 动态参数 | 模块间共享动态生成的参数（如 token、临时 ID） |

## Initialization

```python
# 使用调用者所在目录作为项目根目录（推荐）
helper = Helper('./')

# 指定项目根目录
helper = Helper('/path/to/project')

# 自定义配置文件名
helper = Helper('/path/to/project', config_file_name='shared_config.yaml')
```

## Methods

### set_module_value

设置嵌套配置键的值。

```python
# 写入数据库配置
helper.set_module_value('database', 'host', value='127.0.0.1')
helper.set_module_value('database', 'port', value=5432)

# 写入 API 配置
helper.set_module_value('api', 'token', value='abc123')
helper.set_module_value('api', 'endpoint', value='https://api.example.com')

# 写入共享临时参数
helper.set_module_value('shared', 'temp_id', value='temp_123')
helper.set_module_value('shared', 'status', value='running')
```

**参数说明**：
- `*keys`: 按嵌套层级排列的键
- `value`: 要设置的值

### get_module_value

获取嵌套配置键的值，支持等待机制。

```python
# 基本获取
host = helper.get_module_value('database', 'host')

# 等待最多 10 秒，直到值存在（跨进程场景）
host = helper.get_module_value('database', 'host', max_waiting_time=10)

# 禁用调试输出
host = helper.get_module_value('database', 'host', debug=False)

# 未找到时返回 None
if host is None:
    print("配置未找到")
```

**参数说明**：
- `*keys`: 按嵌套层级排列的键
- `max_waiting_time` (可选): 最大等待时间（秒），轮询配置文件直到值存在
- `debug` (可选): 是否启用调试信息，默认 True

**返回值**：
- 找到值：返回配置值
- 超时：返回 None

### delete_module_value

删除嵌套配置键的值。

```python
# 删除指定键
helper.delete_module_value('database', 'host')

# 删除整个分支
helper.delete_module_value('database')

# 清除临时参数
helper.delete_module_value('shared', 'temp_id')
```

**参数说明**：
- `*keys`: 按嵌套层级排列的键

### get_proj_root

获取项目根目录路径。

```python
root = helper.get_proj_root()
print(f"项目根目录: {root}")
```

### get_config_path

获取配置文件路径。

```python
config_path = helper.get_config_path()
print(f"配置文件: {config_path}")
```

## 使用模式

### 模式 1：主进程配置，子进程读取

```python
# main.py - 主进程
from pywayne.helper import Helper

helper = Helper()
helper.set_module_value('task', 'config', value={'param1': 1, 'param2': 2})

# 启动子进程
import subprocess
subprocess.run(['python', 'worker.py'])
```

```python
# worker.py - 子进程
from pywayne.helper import Helper

helper = Helper()
config = helper.get_module_value('task', 'config', max_waiting_time=5)
print(f"收到配置: {config}")
```

### 模式 2：模块间共享参数

```python
# module_a.py
from pywayne.helper import Helper

helper = Helper()
helper.set_module_value('shared', 'data_file', value='/path/to/data.csv')
```

```python
# module_b.py
from pywayne.helper import Helper

helper = Helper()
data_file = helper.get_module_value('shared', 'data_file', max_waiting_time=10)
with open(data_file, 'r') as f:
    # 处理文件
    pass
```

### 模式 3：动态参数传递

```python
# sender.py
from pywayne.helper import Helper

helper = Helper()
temp_id = generate_temp_id()
helper.set_module_value('shared', 'temp_id', value=temp_id)

# 通知接收者...
```

```python
# receiver.py
from pywayne.helper import Helper

helper = Helper()
temp_id = helper.get_module_value('shared', 'temp_id', max_waiting_time=60)
if temp_id:
    # 使用 temp_id
    pass
```

## 配置文件结构

Helper 操作的配置文件为 YAML 格式，示例结构：

```yaml
database:
  host: 127.0.0.1
  port: 5432
api:
  token: abc123
  endpoint: https://api.example.com
shared:
  temp_id: temp_123
  status: running
```

## 注意事项

1. **统一配置文件**: 所有模块共享同一个 `common_info.yaml`（或自定义文件名）
2. **自动创建**: 配置文件不存在时，初始化会自动创建空文件
3. **路径检测**: 未指定 `project_root` 时，自动根据调用者所在文件目录确定项目根目录
4. **等待机制**: `max_waiting_time` 用于等待其他进程写入的配置值
5. **并发安全**: YAML 写入使用 update 模式，减少并发冲突风险
