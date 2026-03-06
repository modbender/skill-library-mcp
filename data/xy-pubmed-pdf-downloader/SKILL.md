---
name: xy-pubmed-pdf-downloader
description: Download PDFs from PubMed Central (PMC) and Europe PMC. Use when the user needs to download open-access academic papers from PubMed Central using PMC ID, PubMed URL, PMID, or DOI. Supports single download and batch download modes. Created by xuyuan0805.
---

# XY PubMed PDF Downloader

下载 PubMed Central (PMC) 和 Europe PMC 开放获取论文的 PDF 文件。

## 功能

- 支持多种输入格式：PMC ID、PubMed URL、DOI
- 自动从 URL 中提取 PMC ID
- DOI 自动转换为 PMC ID
- 批量下载支持
- 自动回退到 Europe PMC

## 使用方法

### 单文件下载

```bash
python3 scripts/download_pmc_pdf.py <identifier>
```

支持的 identifier 格式：
- PMC ID: `PMC12345678` 或 `12345678`
- PubMed URL: `https://pmc.ncbi.nlm.nih.gov/articles/PMC12345678/`
- DOI: `10.3389/fcvm.2024.1368022`

### 批量下载

创建文本文件 `pmc_list.txt`，每行一个 ID：
```
PMC12345678
PMC87654321
10.3389/fcvm.2024.1368022
https://pmc.ncbi.nlm.nih.gov/articles/PMC56789012/
```

运行：
```bash
python3 scripts/download_pmc_pdf.py --batch pmc_list.txt
```

### 选项

- `-o, --output <dir>`: 指定输出目录 (默认: `./downloads`)
- `-f, --filename <name>`: 自定义文件名
- `--batch <file>`: 从文件批量下载

## 示例

```bash
# 下载单个 PDF
python3 scripts/download_pmc_pdf.py PMC12867338

# 指定输出目录
python3 scripts/download_pmc_pdf.py PMC12867338 -o ./papers

# 自定义文件名
python3 scripts/download_pmc_pdf.py PMC12867338 -f coronary_prediction.pdf

# 批量下载
python3 scripts/download_pmc_pdf.py --batch id_list.txt -o ./batch_downloads
```

## 注意事项

1. **仅支持开放获取 (Open Access)** 的文章
2. 如果 PMC 下载失败，会自动尝试 Europe PMC
3. 批量下载时默认有 1 秒延迟，避免对服务器造成压力
4. 需要 `requests` 库：`pip install requests`

## 输出

下载的 PDF 文件保存在指定目录，默认命名格式：
- `PMC{ID}.pdf` (如 `PMC12867338.pdf`)

## 错误处理

- `404`: 文章不存在或不是开放获取
- `DOI 转换失败`: 该 DOI 没有对应的 PMC 记录
- 其他网络错误会显示详细错误信息
