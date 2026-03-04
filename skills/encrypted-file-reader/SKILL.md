# encrypted-file-reader

读取本地加密/受保护的文件内容，支持企业安全策略环境。

## 功能

- 读取文本文件（.txt, .md, .java, .py, .js 等）
- 读取 Word 文档（.docx）
- 读取 Excel 表格（.xlsx）
- 自动处理特殊编码文件的解码问题
- 支持企业安全策略环境下的文件读取
- 适用于通过授权应用程序可访问的加密文件

## 使用方法

### 通过 Python 脚本调用

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
```

## 支持的扩展名

- **文本类**: .txt, .md, .markdown, .rst, .log, .csv, .tsv
- **代码类**: .java, .py, .js, .ts, .jsx, .tsx, .c, .cpp, .h, .cs, .go, .rs, .rb, .php, .vue
- **配置类**: .json, .xml, .yaml, .yml, .toml, .ini, .cfg, .properties, .gradle, .config, .env
- **样式类**: .html, .htm, .css, .scss, .sass, .less
- **脚本类**: .sh, .bash, .bat, .cmd, .ps1, .sql
- **Word 文档**: .docx
- **Excel 表格**: .xlsx

## 输出

- 成功：输出文件内容（UTF-8 编码）
- 失败：输出错误信息

## 技术原理

- **文本文件**: 直接读取二进制后用 UTF-8 解码
- **Office 文件**: 使用 zipfile 解压后提取 XML 中的文本内容
- **加密/受保护文件**: 通过正确的字节处理方式处理通过授权应用程序可访问的文件内容

## 依赖

- Python 3.x
- 标准库（zipfile, re, sys, os）

## 注意事项

- 本工具仅读取用户有权限访问的本地文件
- 不支持绕过合法的文件访问控制
- 适用于企业环境中授权的文件读取场景
- 文件需要能通过系统授权的应用程序（如 Word、Excel）正常打开

## 法律说明

- 本工具仅用于读取用户有合法访问权限的本地文件
- 不支持绕过任何合法的文件访问控制或权限管理
- 用户应确保使用本工具符合所在组织的政策和法律法规
- 本工具通过正确的编码处理方式读取文件，不涉及破解或绕过加密
