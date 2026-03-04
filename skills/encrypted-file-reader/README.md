# encrypted-file-reader

读取本地加密/受保护的文件内容，支持企业安全策略环境。

## 功能

- 读取文本文件（.txt, .md, .java, .py, .js 等）
- 读取 Word 文档（.docx）
- 读取 Excel 表格（.xlsx）
- 自动处理特殊编码文件的解码问题
- 支持企业安全策略环境下的文件读取
- 适用于通过授权应用程序可访问的加密文件

## 安装

Skill 已安装到：`D:\ai\skills\encrypted-file-reader`

## 使用方法

### 命令行调用

```bash
python D:\ai\skills\encrypted-file-reader\read_file.py <文件路径>
```

### 示例

```bash
# 读取文本文件
python D:\ai\skills\encrypted-file-reader\read_file.py E:\data\test.txt

# 读取 Word 文档
python D:\ai\skills\encrypted-file-reader\read_file.py E:\data\test.docx

# 读取 Excel 表格
python D:\ai\skills\encrypted-file-reader\read_file.py E:\data\test.xlsx

# 读取代码文件
python D:\ai\skills\encrypted-file-reader\read_file.py E:\project\src\Main.java
```

## 支持的扩展名

| 类型 | 扩展名 |
|------|--------|
| **文本类** | .txt, .md, .markdown, .log, .csv, .tsv |
| **代码类** | .java, .py, .js, .ts, .jsx, .tsx, .c, .cpp, .h, .cs, .go, .rs, .rb, .php, .vue, .svelte |
| **配置类** | .json, .json5, .xml, .yaml, .yml, .toml, .ini, .cfg, .conf, .properties, .gradle, .config, .env |
| **Web 前端** | .html, .htm, .css, .scss, .sass, .less, .styl |
| **脚本类** | .sh, .bash, .bat, .cmd, .ps1, .sql, .graphql |
| **Git 相关** | .gitignore, .gitattributes, .gitmodules, .editorconfig |
| **构建配置** | .dockerfile, .dockerignore, .makefile, .cmake |
| **其他** | .diff, .patch, .readme, .license, .changelog |
| **Word 文档** | .docx |
| **Excel 表格** | .xlsx |

## 输出

- **成功**: 输出文件内容（UTF-8 编码）到 stdout
- **失败**: 输出错误信息到 stderr，退出码为 1

## 技术原理

- **文本文件**: 直接读取二进制后用 UTF-8 解码
- **Office 文件 (.docx/.xlsx)**: 使用 zipfile 解压后提取 XML 中的文本字节
- **加密/受保护文件**: 通过正确的字节处理方式处理通过授权应用程序可访问的文件内容

## 依赖

- Python 3.x
- 标准库（zipfile, re, sys, os）- 无需额外安装

## 在 AI 智能体中使用

```python
import subprocess

def read_file(file_path):
    result = subprocess.run(
        ['python', r'D:\ai\skills\encrypted-file-reader\read_file.py', file_path],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    if result.returncode != 0:
        raise Exception(result.stderr)
    return result.stdout

# 使用示例
content = read_file(r'E:\data\test.docx')
print(content)
```

## 注意事项

1. 文件路径使用绝对路径或正确的相对路径
2. 路径中的反斜杠需要转义或使用原始字符串
3. 不支持加密的 .doc 和 .xls（仅支持 .docx 和 .xlsx）
4. 本工具仅读取用户有权限访问的本地文件
5. 适用于企业环境中授权的文件读取场景
6. 文件需要能通过系统授权的应用程序（如 Word、Excel）正常打开

## 法律说明

- 本工具仅用于读取用户有合法访问权限的本地文件
- 不支持绕过任何合法的文件访问控制或权限管理
- 用户应确保使用本工具符合所在组织的政策和法律法规
- 本工具通过正确的编码处理方式读取文件，不涉及破解或绕过加密
- 如果文件无法通过授权应用程序（如 Word、Excel）打开，本工具也无法读取
