---
name: pywayne-data-structure
description: Data structure toolkit for logical condition trees, union-find operations, and XML file I/O. Use when working with tree-based data structures, set operations, union-find algorithms, or XML parsing and serialization.
---

# Pywayne Data Structure

数据结构工具集，提供逻辑条件树、并查集和 XML 文件读写功能。

## Quick Start

```python
from pywayne.data_structure import ConditionTree, UnionFind, XmlIO

# 逻辑条件树
tree = ConditionTree("root")
tree.append_by_path([{'tag': 'if', 'attrib': {}, 'text': '条件1'}])
tree.append_by_path([{'tag': 'else', 'attrib': {}, 'text': '条件2'}])

# 并查集操作
uf = UnionFind(10)
rep = uf.find(3)  # 返回集合标识
uf.union(1, 2)  # 合并两个集合

# XML 读写
xml_io = XmlIO("config.xml", "output.xml")
tree = xml_io.read()
xml_io.write("root", tree)
```

## ConditionTree - 逻辑条件树

用于存储和管理条件表达式的树形结构。

### 初始化

```python
from pywayne.data_structure import ConditionTree

tree = ConditionTree("root")
```

### 添加节点

通过路径列表添加节点。

```python
# 根节点
tree.append_by_path([{'tag': 'if', 'attrib': {}, 'text': '条件1'}])

# 子节点
path = [{'tag': 'if', 'attrib': {}, 'text': '条件1-1'}]
tree.append_by_path(path)
```

**节点字典格式**：`{'tag': 标签名, 'attrib': 属性字典, 'text': 文本内容}`

### 查找节点

**按标签名查找**：`find(nick_name)` - 查找指定标签名的节点

```python
tree.find("if")  # 返回 if 节点
```

**按路径查找**：`find_by_path(path)` - 沿给定路径查找节点

```python
node = tree.find_by_path(["root", "if", "条件1-1"])
```

### 打印树路径

打印从根到所有叶子的完整路径。

```python
tree.print_path()
```

## UnionFind - 并查集

并查集数据结构，支持按秩合并与路径压缩。

### 初始化

```python
from pywayne.data_structure import UnionFind

uf = UnionFind(10)  # N 个元素
```

### 查找集合标识

```python
rep = uf.find(3)  # 返回元素 3 所在集合的标识（整数）
```

### 合并集合

```python
uf.union(1, 2)  # 合并集合 1 和 2
```

### 检查连接性

```python
uf.connected(1, 2)  # 检查元素 1 和 2 是否在同一集合
```

### 元素计数

```python
count = uf.count()  # 返回集合中元素数量
```

## XmlIO - XML 读写

用于 XML 文件的读取和写入，支持与 ConditionTree 互转。

### 初始化

```python
from pywayne.data_structure import XmlIO

xml_io = XmlIO("input.xml", "output.xml")
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `file_read` | str | 待读取的 XML 文件路径 |
| `file_write` | str | 待输出的 XML 文件路径 |

### 读取 XML

```python
tree = xml_io.read()
```

**返回**：解析得到的 `ConditionTree` 对象

### 写入 XML

```python
xml_io.write("root", tree)
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `root_name` | str | 根节点名称，将作为 XML 根标签 |

## 应用场景

| 场景 | 使用类 |
|------|------|
| 决策树逻辑 | `ConditionTree` |
| 网络连接管理 | `UnionFind` |
| 配置文件处理 | `XmlIO` |
