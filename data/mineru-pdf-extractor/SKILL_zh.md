---
name: mineru-pdf-extractor
description: 使用 MinerU API 将 PDF 解析为 Markdown，支持公式、表格、OCR。提供本地文件和在线 URL 两种解析方式。
author: Community
version: 1.0.0
homepage: https://mineru.net/
source: https://github.com/opendatalab/MinerU
env:
  - name: MINERU_TOKEN
    description: "MinerU API 认证令牌（主要方式）"
    required: true
  - name: MINERU_API_KEY
    description: "备选 API 令牌（当 MINERU_TOKEN 未设置时使用）"
    required: false
  - name: MINERU_BASE_URL
    description: "API 基础地址（可选，默认为 https://mineru.net/api/v4）"
    required: false
    default: "https://mineru.net/api/v4"
tools:
  required:
    - name: curl
      description: "HTTP 客户端，用于 API 请求和文件下载"
    - name: unzip
      description: "压缩包解压工具，用于解压结果 ZIP 文件"
  optional:
    - name: jq
      description: "JSON 处理器，用于增强解析和安全性（推荐安装）"
---

# MinerU PDF Extractor

使用 MinerU API 将 PDF 文档解析为结构化 Markdown，支持公式识别、表格提取和 OCR。

> **注意**：这是一个社区技能，非 MinerU 官方产品。你需要从 [MinerU](https://mineru.net/) 获取自己的 API 密钥。

---

## 📁 技能结构

```
mineru-pdf-extractor/
├── SKILL.md                          # 英文版说明文档
├── SKILL_zh.md                       # 中文版说明文档（本文件）
├── docs/                             # 参考资料
│   ├── Local_File_Parsing_Guide.md   # 本地 PDF 解析详细指南（英文）
│   ├── Online_URL_Parsing_Guide.md   # 在线 PDF 解析详细指南（英文）
│   ├── MinerU_本地文档解析完整流程.md  # 本地解析完整流程（中文）
│   └── MinerU_在线文档解析完整流程.md  # 在线解析完整流程（中文）
└── scripts/                          # 可执行脚本
    ├── local_file_step1_apply_upload_url.sh    # 本地解析步骤 1
    ├── local_file_step2_upload_file.sh         # 本地解析步骤 2
    ├── local_file_step3_poll_result.sh         # 本地解析步骤 3
    ├── local_file_step4_download.sh            # 本地解析步骤 4
    ├── online_file_step1_submit_task.sh        # 在线解析步骤 1
    └── online_file_step2_poll_result.sh        # 在线解析步骤 2
```

---

## 🔧 环境要求

### 必需环境变量

脚本会自动从环境变量中读取 MinerU Token（二选一）：

```bash
# 方式 1：设置 MINERU_TOKEN
export MINERU_TOKEN="your_api_token_here"

# 方式 2：设置 MINERU_API_KEY
export MINERU_API_KEY="your_api_token_here"
```

### 必需命令行工具

- `curl` - 用于 HTTP 请求（系统通常自带）
- `unzip` - 用于解压结果（系统通常自带）

### 可选工具

- `jq` - 用于增强 JSON 解析和安全性（推荐但非必需）
  - 如未安装，脚本将使用备用方法
  - 安装：`apt-get install jq`（Debian/Ubuntu）或 `brew install jq`（macOS）

### 可选配置

```bash
# 设置 API 基础地址（默认已配置）
export MINERU_BASE_URL="https://mineru.net/api/v4"
```

> 💡 **获取 Token**：访问 https://mineru.net/apiManage/docs 注册并获取 API 密钥

---

## 📄 功能一：解析本地 PDF 文档

适用于本地存储的 PDF 文件，需要 4 个步骤。

### 快速开始

```bash
cd scripts/

# 步骤 1：申请上传 URL
./local_file_step1_apply_upload_url.sh /path/to/your.pdf
# 输出：BATCH_ID=xxx UPLOAD_URL=xxx

# 步骤 2：上传文件
./local_file_step2_upload_file.sh "$UPLOAD_URL" /path/to/your.pdf

# 步骤 3：轮询结果
./local_file_step3_poll_result.sh "$BATCH_ID"
# 输出：FULL_ZIP_URL=xxx

# 步骤 4：下载结果
./local_file_step4_download.sh "$FULL_ZIP_URL" result.zip extracted/
```

### 脚本说明

#### local_file_step1_apply_upload_url.sh

申请上传 URL 和 batch_id。

**用法：**
```bash
./local_file_step1_apply_upload_url.sh <pdf文件路径> [语言] [布局模型]
```

**参数：**
- `语言`：`ch`（中文）、`en`（英文）、`auto`（自动），默认 `ch`
- `布局模型`：`doclayout_yolo`（快速）、`layoutlmv3`（精准），默认 `doclayout_yolo`

**输出：**
```
BATCH_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
UPLOAD_URL=https://mineru.oss-cn-shanghai.aliyuncs.com/...
```

---

#### local_file_step2_upload_file.sh

上传 PDF 文件到预签名 URL。

**用法：**
```bash
./local_file_step2_upload_file.sh <upload_url> <pdf文件路径>
```

---

#### local_file_step3_poll_result.sh

轮询提取结果，直到完成或失败。

**用法：**
```bash
./local_file_step3_poll_result.sh <batch_id> [最大重试次数] [重试间隔秒数]
```

**输出：**
```
FULL_ZIP_URL=https://cdn-mineru.openxlab.org.cn/pdf/.../xxx.zip
```

---

#### local_file_step4_download.sh

下载结果 ZIP 并解压。

**用法：**
```bash
./local_file_step4_download.sh <zip_url> [输出zip文件名] [解压目录名]
```

**输出文件结构：**
```
extracted/
├── full.md              # 📄 Markdown 文档（主要结果）
├── images/              # 🖼️ 提取的图片
├── content_list.json    # 结构化内容
└── layout.json          # 版面分析数据
```

### 详细文档

📚 **完整流程文档**：见 `docs/MinerU_本地文档解析完整流程.md`

---

## 🌐 功能二：解析在线 PDF 文档（URL 方式）

适用于已在线的 PDF 文件（如 arXiv、网站等），只需 2 个步骤，更简洁高效。

### 快速开始

```bash
cd scripts/

# 步骤 1：提交解析任务（直接提供 URL）
./online_file_step1_submit_task.sh "https://arxiv.org/pdf/2410.17247.pdf"
# 输出：TASK_ID=xxx

# 步骤 2：轮询结果并自动下载解压
./online_file_step2_poll_result.sh "$TASK_ID" extracted/
```

### 脚本说明

#### online_file_step1_submit_task.sh

提交在线 PDF 的解析任务。

**用法：**
```bash
./online_file_step1_submit_task.sh <pdf_url> [语言] [布局模型]
```

**参数：**
- `pdf_url`：在线 PDF 的完整 URL（必填）
- `语言`：`ch`（中文）、`en`（英文）、`auto`（自动），默认 `ch`
- `布局模型`：`doclayout_yolo`（快速）、`layoutlmv3`（精准），默认 `doclayout_yolo`

**输出：**
```
TASK_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

#### online_file_step2_poll_result.sh

轮询提取结果，完成后自动下载并解压。

**用法：**
```bash
./online_file_step2_poll_result.sh <task_id> [输出目录] [最大重试次数] [重试间隔秒数]
```

**输出文件结构：**
```
extracted/
├── full.md              # 📄 Markdown 文档（主要结果）
├── images/              # 🖼️ 提取的图片
├── content_list.json    # 结构化内容
└── layout.json          # 版面分析数据
```

### 详细文档

📚 **完整流程文档**：见 `docs/MinerU_在线文档解析完整流程.md`

---

## 📊 两种解析方式对比

| 特性 | **本地 PDF 解析** | **在线 PDF 解析** |
|------|-------------------|-------------------|
| **步骤数** | 4 步 | 2 步 |
| **是否需要上传** | ✅ 是 | ❌ 否 |
| **平均耗时** | 30-60 秒 | 10-20 秒 |
| **适用场景** | 本地文件 | 文件已在线（arXiv、网站等） |
| **文件大小限制** | 200MB | 受限于源服务器 |

---

## ⚙️ 高级用法

### 批量处理本地文件

```bash
for pdf in /path/to/pdfs/*.pdf; do
    echo "处理：$pdf"
    
    # 步骤 1
    result=$(./local_file_step1_apply_upload_url.sh "$pdf" 2>&1)
    batch_id=$(echo "$result" | grep BATCH_ID | cut -d= -f2)
    upload_url=$(echo "$result" | grep UPLOAD_URL | cut -d= -f2)
    
    # 步骤 2
    ./local_file_step2_upload_file.sh "$upload_url" "$pdf"
    
    # 步骤 3
    zip_url=$(./local_file_step3_poll_result.sh "$batch_id" | grep FULL_ZIP_URL | cut -d= -f2)
    
    # 步骤 4
    filename=$(basename "$pdf" .pdf)
    ./local_file_step4_download.sh "$zip_url" "${filename}.zip" "${filename}_extracted"
done
```

### 批量处理在线文件

```bash
for url in \
  "https://arxiv.org/pdf/2410.17247.pdf" \
  "https://arxiv.org/pdf/2409.12345.pdf"; do
    echo "处理：$url"
    
    # 步骤 1
    result=$(./online_file_step1_submit_task.sh "$url" 2>&1)
    task_id=$(echo "$result" | grep TASK_ID | cut -d= -f2)
    
    # 步骤 2
    filename=$(basename "$url" .pdf)
    ./online_file_step2_poll_result.sh "$task_id" "${filename}_extracted"
done
```

---

## ⚠️ 注意事项

1. **Token 配置**：脚本优先读取 `MINERU_TOKEN`，如不存在则读取 `MINERU_API_KEY`
2. **Token 安全**：不要将 Token 硬编码在脚本中，建议通过环境变量传入
3. **URL 可访问性**：在线解析时，确保提供的 URL 是公开可访问的
4. **文件限制**：单文件建议不超过 200MB，最多 600 页
5. **网络稳定**：上传大文件时确保网络稳定
6. **安全性**：本技能包含输入验证和清理，以防止 JSON 注入和目录遍历攻击
7. **可选 jq**：安装 `jq` 可提供增强的 JSON 解析和额外的安全检查

---

## 📚 参考文档

| 文档 | 说明 |
|------|------|
| `docs/MinerU_本地文档解析完整流程.md` | 本地 PDF 解析的详细 curl 命令和参数说明（中文） |
| `docs/MinerU_在线文档解析完整流程.md` | 在线 PDF 解析的详细 curl 命令和参数说明（中文） |
| `docs/Local_File_Parsing_Guide.md` | 本地 PDF 解析详细指南（英文） |
| `docs/Online_URL_Parsing_Guide.md` | 在线 PDF 解析详细指南（英文） |

外部资源：
- 🏠 **MinerU 官网**：https://mineru.net/
- 📖 **API 文档**：https://mineru.net/apiManage/docs
- 💻 **GitHub 仓库**：https://github.com/opendatalab/MinerU

---

*技能版本：1.0.0*  
*发布日期：2026-02-18*  
*社区技能 - 非 MinerU 官方产品*
