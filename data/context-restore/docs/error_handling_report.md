# Context Restore 错误处理分析报告

**分析日期**: 2026-02-07  
**模块**: context-restore  
**版本**: 1.0.0

---

## 1. 当前错误处理机制分析

### 1.1 已实现的错误处理

| 场景 | 当前处理方式 | 状态 |
|------|-------------|------|
| 文件不存在 | 返回 `None` + 错误消息 | ✅ 良好 |
| 权限错误 | 返回 `None` + 错误消息 | ✅ 良好 |
| 无效 JSON | 降级为纯文本处理 | ✅ 良好 |
| OSError | 返回 `None` + 错误消息 | ✅ 良好 |
| 空文件 | 返回空字符串 | ⚠️ 部分 |
| 非法参数 | 抛出 `ValueError` | ✅ 良好 |

### 1.2 当前代码中的错误处理

```python
# load_compressed_context 中的错误处理
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print(f"{EMOJI['error']} Error: File not found: {filepath}")
    return None
except PermissionError:
    print(f"{EMOJI['error']} Error: Permission denied: {filepath}")
    return None
except OSError as e:
    print(f"{EMOJI['error']} Error reading file {filepath}: {e}")
    return None
except Exception as e:
    print(f"{EMOJI['error']} Unexpected error loading context: {e}")
    return None
```

---

## 2. 识别的边界情况和异常场景

### 2.1 高优先级问题

| ID | 场景 | 严重程度 | 影响 |
|----|------|---------|------|
| **BUG-01** | `extract_*` 函数传入 `None` | 高 | 抛出 `AttributeError` |
| **BUG-02** | 二进制数据传入文本函数 | 高 | 抛出 `TypeError` |
| **BUG-03** | 负数消息计数 | 中 | 解析为 `None` |
| **BUG-04** | 压缩率为 0 或负数 | 中 | 返回 `None`，但可能混淆 |
| **BUG-05** | 超大文件 (>10MB) | 中 | 内存问题，性能下降 |
| **BUG-06** | JSON 中缺少预期字段 | 低 | 静默失败，字段为 `None` |

### 2.2 中优先级问题

| ID | 场景 | 问题描述 |
|----|------|---------|
| **PERF-01** | 超长字符串处理 | `re.findall` 在超长文本上可能慢 |
| **PERF-02** | 重复正则匹配 | 每次调用都重新编译正则 |
| **PERF-03** | 无日志记录 | 错误仅打印到 stdout |

### 2.3 低优先级问题

| ID | 场景 | 问题描述 |
|----|------|---------|
| **DOC-01** | 错误代码不一致 | 部分返回 `None`，部分抛异常 |
| **DOC-02** | 缺少错误码体系 | 难以追踪问题来源 |

---

## 3. 边界情况测试用例

### 3.1 文件操作边界测试

```python
import tempfile
import os

# 空文件
def test_empty_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('')
    result = load_compressed_context(f.name)
    os.unlink(f.name)
    assert result == '' or result is not None

# 只含空白字符
def test_whitespace_only():
    content = '   \n\t  \n   '
    result = load_compressed_context_from_string(content)
    assert isinstance(result, str)

# 二进制数据
def test_binary_data():
    try:
        binary = b'\x00\x01\x02\xff\xfe'
        result = extract_recent_operations(binary)
        assert False, "Should raise TypeError"
    except TypeError:
        pass  # 预期行为
```

### 3.2 数据解析边界测试

```python
# 超大数值
def test_large_numbers():
    content = '原始消息数: 99999999999999999999'
    metadata = parse_metadata(content)
    # 应处理大整数或限制范围

# 负数
def test_negative_numbers():
    content = '原始消息数: -5'
    metadata = parse_metadata(content)
    assert metadata.get('original_count') is None or metadata.get('original_count') >= 0

# 零除问题
def test_zero_division():
    ratio = calculate_compression_ratio(0, 10)
    assert ratio is None  # 不能除以零

# 非数字值
def test_non_numeric():
    content = '原始消息数: abc\n压缩后消息数: def'
    metadata = parse_metadata(content)
    assert metadata.get('original_count') is None
```

### 3.3 编码和格式边界测试

```python
# UTF-8 特殊字符
def test_utf8_special_chars():
    content = '测试中文 🎉 emoji'
    result = extract_key_projects(content)
    assert isinstance(result, list)

# JSON 损坏
def test_corrupted_json():
    json_str = '{"valid": true, "incomplete":'
    result = load_compressed_context_from_string(json_str)
    # 应该降级为字符串处理

# 混合编码
def test_mixed_encoding():
    content = 'Hello 世界 مرحبا'
    result = extract_memory_highlights(content)
    assert isinstance(result, list)
```

---

## 4. 健壮性改进建议

### 4.1 核心改进方案

#### 改进 1: 输入验证装饰器

```python
from functools import wraps
import re

def validate_input(func):
    """输入验证装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 检查 None
        if args and args[0] is None:
            return func(*args, **kwargs) if func.__name__ in ['extract_memory_highlights'] else []
        
        # 检查类型
        for arg in args:
            if isinstance(arg, (bytes, bytearray)):
                raise TypeError(f"{func.__name__} expects str, got bytes")
        
        return func(*args, **kwargs)
    return wrapper

@validate_input
def extract_recent_operations(content: str) -> list[str]:
    ...
```

#### 改进 2: 正则表达式预编译

```python
# 在模块顶部预编译
_METADATA_PATTERNS = {
    'original': re.compile(r'原始消息数:\s*(\d+)'),
    'compressed': re.compile(r'压缩后消息数:\s*(\d+)'),
    'timestamp': re.compile(r'上下文压缩于\s*([\d\-T:.]+)'),
    'checkmark': re.compile(r'✅\s*(.+?)(?:\n|$)'),
    'cron': re.compile(r'(\d+)个?cron任务.*?已转为'),
}

def parse_metadata(content: str) -> dict:
    metadata = {}
    if match := _METADATA_PATTERNS['original'].search(content):
        original = int(match.group(1))
        metadata['original_count'] = original if original >= 0 else None
    # ...
```

#### 改进 3: 统一错误码体系

```python
from enum import Enum, auto

class ContextErrorCode(Enum):
    """上下文恢复错误码"""
    SUCCESS = auto()
    FILE_NOT_FOUND = auto()
    PERMISSION_DENIED = auto()
    INVALID_JSON = auto()
    EMPTY_CONTENT = auto()
    PARSE_ERROR = auto()
    UNEXPECTED_ERROR = auto()

class ContextRestoreError(Exception):
    """上下文恢复异常"""
    def __init__(self, code: ContextErrorCode, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
```

#### 改进 4: 数据验证函数

```python
def validate_message_count(value: Any, field_name: str) -> Optional[int]:
    """验证消息计数字段"""
    if value is None:
        return None
    if not isinstance(value, (int, str)):
        return None
    try:
        num = int(value)
        if num < 0:
            return None  # 负数无效
        if num > 10_000_000:  # 设置合理上限
            return 10_000_000
        return num
    except (ValueError, TypeError):
        return None

def calculate_compression_ratio(original: int, compressed: int) -> Optional[float]:
    """带验证的压缩率计算"""
    original = validate_message_count(original, 'original')
    compressed = validate_message_count(compressed, 'compressed')
    
    if original is None or compressed is None:
        return None
    if original == 0:
        return None  # 避免除零
    if original < compressed:
        return None  # 压缩后不应该比原始大
    
    return round((compressed / original) * 100, 2)
```

### 4.2 改进优先级

| 优先级 | 改进项 | 工作量 | 影响范围 |
|--------|--------|--------|----------|
| P0 | 输入验证装饰器 | 小 | 所有提取函数 |
| P0 | 错误码体系 | 中 | CLI 和 API |
| P1 | 正则预编译 | 小 | 解析性能 |
| P1 | 数据验证函数 | 小 | 解析准确性 |
| P2 | 详细日志记录 | 中 | 可观测性 |
| P2 | 性能监控 | 中 | 生产环境 |

### 4.3 推荐的错误处理最佳实践

```python
# 推荐的函数签名模式
from typing import Union, Optional, Tuple

Result = Union[dict, list, str, None]

def safe_load_context(filepath: str) -> Tuple[Optional[Result], Optional[str]]:
    """
    安全加载上下文文件
    
    Returns:
        Tuple of (result, error_message)
        - result: Parsed content or None
        - error_message: Error description or None if successful
    """
    try:
        result = load_compressed_context(filepath)
        return result, None
    except Exception as e:
        return None, str(e)

# 使用示例
content, error = safe_load_context('context.json')
if error:
    logger.error(f"Failed to load context: {error}")
    handle_gracefully(error)
else:
    process_context(content)
```

---

## 5. 测试覆盖率建议

### 5.1 建议添加的测试用例

```python
# test_error_handling.py

class TestErrorHandling(unittest.TestCase):
    """错误处理测试"""
    
    def test_none_input_handling(self):
        """None 输入处理"""
        with self.assertRaises(TypeError):
            extract_recent_operations(None)
    
    def test_binary_input_handling(self):
        """二进制输入处理"""
        with self.assertRaises(TypeError):
            extract_key_projects(b'binary data')
    
    def test_empty_content_handling(self):
        """空内容处理"""
        result = extract_memory_highlights('')
        self.assertEqual(result, [])
    
    def test_large_file_handling(self):
        """大文件处理 (测试性能)"""
        large_content = 'Hermes Plan ' * 1_000_000
        start = time.time()
        result = extract_key_projects(large_content)
        elapsed = time.time() - start
        self.assertLess(elapsed, 5.0)  # 应在5秒内完成
    
    def test_special_char_handling(self):
        """特殊字符处理"""
        content = 'Test\t\n\r\x00\x1b'
        result = extract_recent_operations(content)
        self.assertIsInstance(result, list)
    
    def test_corrupted_json_recovery(self):
        """损坏 JSON 恢复"""
        corrupted = '{"incomplete":'
        result = load_compressed_context_from_string(corrupted)
        self.assertIsInstance(result, str)  # 降级为文本
```

### 5.2 性能测试建议

```python
import time

class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def test_metadata_parsing_performance(self):
        """元数据解析性能"""
        content = '原始消息数: 100\n压缩后消息数: 10\n' * 1000
        start = time.time()
        for _ in range(100):
            parse_metadata(content)
        elapsed = time.time() - start
        self.assertLess(elapsed, 1.0)  # 100次调用应在1秒内
    
    def test_project_extraction_performance(self):
        """项目提取性能"""
        content = ('Hermes Plan 是一个数据分析助手。' * 100 +
                   'Akasha Plan 是自主新闻系统。' * 100)
        start = time.time()
        for _ in range(100):
            extract_key_projects(content)
        elapsed = time.time() - start
        self.assertLess(elapsed, 1.0)
```

---

## 6. 总结

### 6.1 当前状态

- ✅ 基础错误处理已实现
- ✅ 文件 I/O 错误处理完善
- ⚠️ 输入验证不完整
- ⚠️ 边界情况处理不足
- ❌ 缺少统一错误码

### 6.2 行动计划

**立即执行 (P0)**:
1. 添加输入验证装饰器
2. 添加 `None` 和类型检查
3. 完善负数和零值处理

**短期执行 (P1)**:
1. 实现正则预编译
2. 添加数据验证函数
3. 建立错误码体系

**长期优化 (P2)**:
1. 添加详细日志
2. 性能监控和优化
3. 集成测试覆盖率工具

---

**报告生成时间**: 2026-02-07 17:59 UTC  
**分析者**: OpenClaw Context-Restore Analysis
