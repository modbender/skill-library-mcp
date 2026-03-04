# academic-formula-converter

学术论文数学公式转换工具 - 将Markdown中的LaTeX公式转换为docx和html格式

## 功能

1. **LaTeX公式转Unicode** - 将LaTeX格式转换为可读性更好的Unicode符号
2. **生成Word文档** - 支持图片和公式的docx文件
3. **生成HTML文档** - 带样式的HTML文件

## 触发关键词

- "公式转换"
- "数学公式"
- "LaTeX转docx"
- "论文公式"
- "formula converter"
- "academic formula"

## 使用方法

### 命令行

```bash
# 基本转换
python3 /path/to/formula_converter.py input.md output.docx

# 转换为HTML
python3 /path/to/formula_converter.py input.md output.html

# 指定图片目录
python3 /path/to/formula_converter.py input.md output.docx --images /path/to/images/
```

### 支持的公式

- 行内公式: `$formula$`
- 块公式: `$$formula$$`

### LaTeX到Unicode转换示例

| LaTeX | Unicode |
|-------|---------|
| \times | × |
| \frac{a}{b} | (a)/(b) |
| \alpha | α |
| \sigma | σ |
| \leq | ≤ |
| \geq | ≥ |
| \sum | Σ |
| \sqrt{} | √() |
| \infty | ∞ |

## 依赖

```bash
pip install python-docx markdown
```
