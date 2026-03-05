# PEP8 代码风格指南

## 核心规则

### 1. 缩进

- 使用 **4 个空格** 作为缩进
- 不要使用 Tab
- 续行使用悬挂缩进

```python
# 正确
def long_function_name(
        var_one, var_two, var_three,
        var_four):
    print(var_one)

# 错误
def long_function_name(
    var_one, var_two, var_three,
    var_four):
    print(var_one)
```

### 2. 空行

- 顶层函数/类定义之间：**2 个空行**
- 方法定义之间：**1 个空行**
- 函数内逻辑段落：**1 个空行**

```python
# 正确
class MyClass:
    def method_one(self):
        pass
    
    def method_two(self):
        pass


def function_one():
    pass


def function_two():
    pass

# 错误 (E302)
def function_one():
    pass
def function_two():  # 缺少 2 个空行
    pass
```

### 3. 导入

- 放在文件顶部
- 按顺序分组：标准库 → 第三方 → 本地
- 每组之间 1 个空行

```python
# 正确
import os
import sys

import requests
import numpy as np

from . import local_module
from .utils import helper
```

### 4. 行长度

- 最大 **79 字符** (代码)
- 最大 **99 字符** (文档/注释)

```python
# 正确 (使用括号隐式续行)
result = (
    some_long_variable_name +
    another_long_variable_name
)

# 错误 (E501)
result = some_long_variable_name + another_long_variable_name + yet_another_one
```

### 5. 空白字符

- 行尾不要有空格 (W293)
- 空行不要有空格

```bash
# 清理行尾空格
sed -i 's/[[:space:]]*$//' file.py
```

### 6. 命名约定

| 类型 | 风格 | 示例 |
|------|------|------|
| 函数/变量 | snake_case | `my_function`, `my_var` |
| 类 | PascalCase | `MyClass` |
| 常量 | UPPER_CASE | `MAX_SIZE` |
| 私有 | _prefix | `_internal` |

### 7. 布尔比较

```python
# 正确
if condition:
if not condition:

# 避免 (E712)
if condition is True:
if condition is False:
```

## 常见错误代码

### E 类错误 (Error)

| 代码 | 说明 | 修复 |
|------|------|------|
| E302 | 缺少 2 个空行 | 在函数/类前加空行 |
| E303 | 多余的空行 | 删除多余空行 |
| E305 | 类/函数后缺少 2 个空行 | 在定义后加空行 |
| E402 | 导入不在顶部 | 移动导入到文件开头 |
| E501 | 行太长 | 拆分长行 |
| E711 | 与 None 比较 | 使用 `if x is None` |
| E712 | 与 True/False 比较 | 使用 `if x` 或 `if not x` |
| E722 | 裸 except | 使用 `except Exception` |

### W 类警告 (Warning)

| 代码 | 说明 | 修复 |
|------|------|------|
| W291 | 行尾有空格 | 删除空格 |
| W293 | 空行有空格 | 删除空格 |
| W391 | 文件末尾多余空行 | 删除多余空行 |
| W503 | 运算符在行首 | 移到行尾 (或忽略) |

## 自动修复工具

### black

```bash
pip install black
black file.py
```

### autopep8

```bash
pip install autopep8
autopep8 --in-place --aggressive file.py
```

### autoflake

```bash
pip install autoflake
autoflake --remove-all-unused-imports --in-place file.py
```

### isort

```bash
pip install isort
isort file.py
```

## 完整修复流程

```bash
# 1. 备份
cp file.py file.py.backup

# 2. 清理导入
autoflake --remove-all-unused-imports --in-place file.py

# 3. 排序导入
isort file.py

# 4. 格式化
black file.py

# 5. 验证
pycodestyle file.py
```

## Pre-commit 配置

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
```

## 在 CI 中使用

GitHub Actions 示例:

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install tools
        run: |
          pip install black flake8 isort
      
      - name: Run black
        run: black --check .
      
      - name: Run isort
        run: isort --check-only .
      
      - name: Run flake8
        run: flake8 .
```

## 参考资料

- [PEP 8 官方文档](https://pep8.org/)
- [pycodestyle GitHub](https://github.com/PyCQA/pycodestyle)
- [black GitHub](https://github.com/psf/black)
