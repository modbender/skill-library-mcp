# ebook_to_md 测试样例

## 现有样例

| 类型 | 文件 | 预期输出 |
|------|------|----------|
| PDF | test_with_table.pdf | expected/test_with_table.md |
| PDF | test_with_pic.pdf | expected/test_with_pic.md |
| PNG | test_ocr.png | expected/test_ocr.md |
| JPEG | test_ocr.jpg | expected/test_ocr.md |
| EPUB | test_minimal.epub | expected/test_minimal.md |
| MOBI | test_minimal.mobi | expected/test_minimal.md（同 EPUB） |

## 生成样例

```bash
cd skills/ebook_to_md
python fixtures/create_fixtures.py
```

- **PNG/JPEG**：需 Pillow，生成含中文的 OCR 测试图
- **EPUB**：生成最小合法 EPUB 3
- **MOBI**：若已安装 Calibre，自动从 EPUB 转出
