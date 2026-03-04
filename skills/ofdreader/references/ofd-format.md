# OFD 文件格式参考

## 概述

OFD（Open Fixed-layout Document）是中国国家标准的版式文档格式（GB/T 33190-2016），类似于 PDF，但采用 XML 和 ZIP 技术。

## 文件结构

```
document.ofd (ZIP 文件)
├── OFD.xml           # 文档清单，描述文档结构
├── Doc_0/            # 文档内容目录
│   ├── Document.xml  # 文档根元素
│   ├── Pages/        # 页面目录
│   │   ├── Page_0/   # 第 1 页内容
│   │   └── Page_1/   # 第 2 页内容
│   └── ...
└── ...
```

## XML 命名空间

标准命名空间：`http://www.ofdspec.org/2016`

## 关键元素

### TextCode
存储文本内容：
```xml
<ofd:TextCode>文本内容</ofd:TextCode>
```

### Paragraph
段落元素，包含格式和文本：
```xml
<ofd:Paragraph>
    <ofd:TextCode>段落文本</ofd:TextCode>
</ofd:Paragraph>
```

### Table
表格结构：
```xml
<ofd:Table>
    <ofd:Row>
        <ofd:Cell>
            <ofd:TextCode>单元格内容</ofd:TextCode>
        </ofd:Cell>
    </ofd:Row>
</ofd:Table>
```

## 应用场景

- 电子公文
- 数字证照
- 电子发票
- 档案存储
- 电子出版

## 与 PDF 的区别

| 特性 | OFD | PDF |
|------|-----|-----|
| 标准来源 | 中国国家标准 | 国际标准 |
| 内部格式 | XML + ZIP | 二进制 |
| 可扩展性 | 高 | 中 |
| 中文支持 | 原生支持 | 依赖字体 |
