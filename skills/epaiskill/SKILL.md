---
name: epai
description: EPAI 平台管理技能，通过 CLI 操作知识库、文档和目录。
env:
  - EPAI_API_BASE=your_api_base
  - EPAI_API_KEY=your_api_key_here
  - EPAI_ACCOUNT=yourname
  - EPAI_VERIFY_TLS=true
permissions:
  - type: file-read
    description: 上传文档时会读取本地文件
---

# EPAI Skill

此 Skill 封装了 EPAI 平台的管理操作，所有接口都通过 `scripts/epaiclt.py` 调用。

## 使用示例

### 列出所有知识库

```bash
python scripts/epaiclt.py --method kb_list
```

### 创建知识库（必须指定 catalog_id）

```bash
python scripts/epaiclt.py   --method kb_create   --name "知识库名称"   --description "知识库描述"   --catalog_id <目录ID>
```

### 删除知识库

```bash
python scripts/epaiclt.py   --method kb_delete   --kb_ids kb_id1 kb_id2 ...
```

### 上传文件到知识库

```bash
python scripts/epaiclt.py   --method document_upload   --kb_id <知识库ID>   --file ./file1.pdf ./file2.docx
```

### 获取目录列表

```bash
python scripts/epaiclt.py --method catalog_list
```

### 创建目录（必须指定 parent_id）

```bash
python scripts/epaiclt.py   --method catalog_create   --name "目录名称"   --parent_id <父目录ID>
```

### 删除目录

```bash
python scripts/epaiclt.py   --method catalog_delete   --catalog_id <目录ID>
```

### 获取知识库文档列表

```bash
python scripts/epaiclt.py   --method document_list   --kb_id <知识库ID>
```

### 批量删除知识库文档

```bash
python scripts/epaiclt.py   --method document_delete   --doc_ids doc_id1 doc_id2 ...
```


