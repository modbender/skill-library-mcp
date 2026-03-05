# Word Reader 技能测试

这是一个简单的测试文档，用于验证 Word Reader 技能的功能。

## 测试内容

### 1. 基本文本
这是一段测试文本，用于验证文本提取功能是否正常工作。

### 2. 表格测试

| 功能 | 状态 | 描述 |
|------|------|------|
| 文本提取 | ✅ | 能够提取文档中的所有文本内容 |
| 表格解析 | ✅ | 能够正确解析表格数据 |
| 元数据获取 | ✅ | 能够获取文档属性信息 |
| 多格式支持 | ✅ | 支持 .docx 和 .doc 格式 |
| 输出格式 | ✅ | 支持 JSON、Text、Markdown 格式 |

### 3. 列表测试

- 第一项：文本提取功能
- 第二项：表格解析功能
- 第三项：图片信息获取
- 第四项：文档元数据读取

### 4. 代码块示例

```python
def read_word_document(file_path):
    """读取 Word 文档"""
    reader = WordReader(file_path)
    if file_path.endswith('.docx'):
        reader.read_docx()
    else:
        reader.read_doc()
    return reader.extract_all()
```

## 测试完成

如果这个技能能够正确读取并解析上述内容，说明功能正常。