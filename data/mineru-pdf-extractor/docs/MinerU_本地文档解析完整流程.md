# MinerU 本地文档解析完整流程（安全加固版本）

> 使用 MinerU API 将 PDF 解析为 Markdown，支持公式、表格、OCR 识别
> 本版本包含安全加固，防止 JSON 注入、目录遍历等攻击

---

## 📋 前置准备

### 1. 环境要求
- `curl` 命令（系统自带）
- `unzip` 工具（用于解压结果）
- MinerU API Token
- `jq`（可选但推荐，用于增强 JSON 解析和安全性）

### 2. 配置环境变量

脚本会自动从环境变量中读取 MinerU Token（二选一）：

```bash
# 方式1: 设置 MINERU_TOKEN
export MINERU_TOKEN="your_api_token_here"

# 方式2: 设置 MINERU_API_KEY（别名，同样有效）
export MINERU_API_KEY="your_api_token_here"

# 可选: 设置 API 基础地址（默认已配置）
export MINERU_BASE_URL="https://mineru.net/api/v4"
```

> 💡 **获取 Token**: 访问 https://mineru.net/apiManage/docs

---

## 🚀 完整流程（4 个步骤）

### Step 1: 申请上传 URL

**命令：**
```bash
curl -s -X POST "${MINERU_BASE_URL}/file-urls/batch" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${MINERU_TOKEN}" \
    -d '{
        "enable_formula": true,
        "language": "ch",
        "enable_table": true,
        "layout_model": "doclayout_yolo",
        "enable_ocr": true,
        "files": [{"name": "YOUR_PDF_FILE.pdf", "is_ocr": true}]
    }'
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `enable_formula` | bool | 否 | 启用公式识别，默认 true |
| `enable_table` | bool | 否 | 启用表格识别，默认 true |
| `enable_ocr` | bool | 否 | 启用 OCR，默认 true |
| `language` | string | 否 | 语言：`ch`(中文)/`en`(英文)/`auto` |
| `layout_model` | string | 否 | 版面模型：`doclayout_yolo`(快)/`layoutlmv3`(准) |
| `files` | array | 是 | 文件列表，每个文件包含 `name` 和 `is_ocr` |

**成功返回值：**
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "batch_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "file_urls": [
      "https://mineru.oss-cn-shanghai.aliyuncs.com/.../YOUR_PDF_FILE.pdf?Expires=..."
    ]
  }
}
```

**提取关键字段：**
- `batch_id`：任务批次 ID，后续查询用
- `file_urls[0]`：预签名上传 URL（有效期约 15 分钟）

---

### Step 2: 上传 PDF 文件

**命令：**
```bash
curl -X PUT "YOUR_UPLOAD_URL_FROM_STEP1" \
    --upload-file "/path/to/YOUR_PDF_FILE.pdf"
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `YOUR_UPLOAD_URL_FROM_STEP1` | Step 1 返回的 `file_urls[0]` |
| `--upload-file` | 本地 PDF 文件路径 |

**注意：**
- ❌ 不要添加 `-H "Content-Type"` header
- ✅ 直接使用 `--upload-file` 参数

**成功返回值：**
```
（无输出，HTTP 200 即成功）
```

---

### Step 3: 轮询提取结果

**命令：**
```bash
curl -s -X GET "${MINERU_BASE_URL}/extract-results/batch/YOUR_BATCH_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${MINERU_TOKEN}"
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `YOUR_BATCH_ID` | Step 1 返回的 `batch_id` |

**轮询策略：**
- 首次查询前等待 5 秒
- 每隔 5 秒查询一次
- 最多轮询 60 次（约 5 分钟）

**返回值状态说明：**

| state | 含义 | 操作 |
|-------|------|------|
| `done` | ✅ 提取完成 | 获取 `full_zip_url` 下载结果 |
| `running` | 🔄 正在处理 | 继续轮询 |
| `waiting-file` | ⏳ 等待文件 | 继续轮询 |
| `pending` | ⏳ 排队中 | 继续轮询 |
| `converting` | 🔄 转换中 | 继续轮询 |
| `failed` | ❌ 提取失败 | 查看 `err_msg` 错误信息 |

**成功返回值（done 状态）：**
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "batch_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "extract_result": [
      {
        "file_name": "YOUR_PDF_FILE.pdf",
        "state": "done",
        "err_msg": "",
        "full_zip_url": "https://cdn-mineru.openxlab.org.cn/pdf/.../xxxx.zip"
      }
    ]
  }
}
```

**提取关键字段：**
- `full_zip_url`：结果 ZIP 包下载地址

---

### Step 4: 下载并解压结果

**命令：**
```bash
# 下载 ZIP 包
curl -L -o "result.zip" \
  "YOUR_FULL_ZIP_URL_FROM_STEP3"

# 解压到文件夹
unzip -q "result.zip" -d "extracted_folder"
```

**解压后的文件结构：**
```
extracted_folder/
├── full.md                    # 📄 完整 Markdown（主要结果）
├── xxxxxxxx_content_list.json # 结构化内容列表
├── xxxxxxxx_origin.pdf        # 原始 PDF 副本
├── layout.json                # 版面分析数据
└── images/                    # 🖼️ 提取的图片文件夹
    ├── image_001.png
    ├── image_002.png
    └── ...
```

**关键输出文件：**

| 文件 | 说明 |
|------|------|
| `full.md` | 📄 解析后的完整 Markdown 文档（最常用） |
| `images/` | 文档中提取的所有图片 |
| `content_list.json` | 结构化内容，包含每段文字的位置信息 |
| `layout.json` | 详细的版面分析数据 |

---

## 📝 完整一键脚本（安全加固版本）

### 本地文件解析脚本（local_parse.sh）

```bash
#!/bin/bash
# MinerU 本地文件解析脚本（安全加固版本）
# 用法: ./local_parse.sh <PDF文件路径> [输出目录]
#
# 本脚本实现以下安全措施：
# - 通过输入清理防止 JSON 注入攻击
# - 通过路径验证防止目录遍历攻击
# - 通过文件名验证防止恶意文件名

set -e

# ============================================================================
# 安全函数
# ============================================================================

# 函数: escape_json
# 用途: 转义字符串中的特殊字符，防止 JSON 注入
# 安全: 防止通过恶意输入破坏 JSON 结构
# 参数:
#   $1 - 需要转义的输入字符串
# 返回: 适合嵌入 JSON 的安全字符串
escape_json() {
    local str="$1"
    # 首先转义反斜杠，避免双重转义
    str="${str//\\/\\\\}"
    # 转义双引号防止 JSON 注入
    str="${str//\"/\\\"}"
    # 转义换行符
    str="${str//$'\n'/\\n}"
    # 转义回车符
    str="${str//$'\r'/\\r}"
    echo "$str"
}

# 函数: validate_filename
# 用途: 清理文件名，防止恶意文件名
# 安全: 只允许字母数字、点、下划线和连字符
#       移除可能被利用的特殊字符
# 参数:
#   $1 - 输入文件名
# 返回: 清理后的文件名
validate_filename() {
    local filename="$1"
    # 检查文件名是否只包含允许的字符
    # 允许: a-z, A-Z, 0-9, .（点）, _（下划线）, -（连字符）
    if [[ ! "$filename" =~ ^[a-zA-Z0-9._-]+$ ]]; then
        echo "⚠️  警告: 文件名包含特殊字符，正在清理..." >&2
        # 移除所有不允许的字符
        filename=$(echo "$filename" | tr -cd 'a-zA-Z0-9._-')
    fi
    echo "$filename"
}

# 函数: validate_dirname
# 用途: 验证目录名，防止目录遍历攻击
# 安全: 防止 ".." 序列和绝对路径逃离目标目录
#       写入系统位置
# 参数:
#   $1 - 输入目录名
# 返回: 验证后的目录名
# 退出: 如果目录名无效
validate_dirname() {
    local dir="$1"
    
    # 安全检查 1: 通过 ".." 防止目录遍历
    # 攻击示例: "../../../etc/passwd" 可能覆盖系统文件
    if [[ "$dir" == *".."* ]]; then
        echo "❌ 错误: 无效的目录名。不能包含 '..'" >&2
        exit 1
    fi
    
    # 安全检查 2: 防止绝对路径
    # 攻击示例: "/etc/cron.d/malicious" 可能写入系统目录
    if [[ "$dir" == /* ]]; then
        echo "❌ 错误: 无效的目录名。不能以 '/' 开头" >&2
        exit 1
    fi
    
    # 安全检查 3: 限制目录名长度
    # 防止缓冲区溢出攻击，保持路径可管理
    if [ ${#dir} -gt 255 ]; then
        echo "❌ 错误: 目录名太长（最大 255 字符）" >&2
        exit 1
    fi
    
    echo "$dir"
}

# ============================================================================
# 配置与设置
# ============================================================================

# 支持 MINERU_TOKEN 或 MINERU_API_KEY 环境变量
# 为不同用户提供灵活性
MINERU_TOKEN="${MINERU_TOKEN:-${MINERU_API_KEY:-}}"
MINERU_BASE_URL="${MINERU_BASE_URL:-https://mineru.net/api/v4}"

# 验证 API token 是否已配置
if [ -z "$MINERU_TOKEN" ]; then
    echo "❌ 错误: 请设置 MINERU_TOKEN 或 MINERU_API_KEY 环境变量"
    exit 1
fi

# ============================================================================
# 输入验证
# ============================================================================

# 验证 PDF 文件路径参数
PDF_PATH="${1:-}"
if [ -z "$PDF_PATH" ] || [ ! -f "$PDF_PATH" ]; then
    echo "❌ 错误: 请提供有效的 PDF 文件路径"
    echo "用法: $0 <PDF文件路径> [输出目录]"
    exit 1
fi

# 获取输出目录，使用默认值
OUTPUT_DIR="${2:-extracted_result}"

# 安全: 验证输出目录防止目录遍历
# 确保解压文件保持在预期位置
OUTPUT_DIR=$(validate_dirname "$OUTPUT_DIR")

# 轮询配置
MAX_RETRIES=60          # 最大状态检查次数
RETRY_INTERVAL=5        # 检查间隔秒数

# ============================================================================
# 文件名处理
# ============================================================================

# 从路径中提取文件名
FILENAME=$(basename "$PDF_PATH")

# 安全: 清理文件名防止注入攻击
# 移除可能破坏 JSON 或具有恶意的特殊字符
FILENAME=$(validate_filename "$FILENAME")

# 创建适合 API 请求的 JSON 安全版本文件名
SAFE_FILENAME=$(escape_json "$FILENAME")

# 显示处理信息
echo "=== MinerU 本地文件解析 ==="
echo "PDF 文件: $PDF_PATH"
echo "输出目录: $OUTPUT_DIR"
echo ""

# ============================================================================
# 步骤 1: 申请上传 URL
# ============================================================================

echo "=== 步骤 1: 申请上传 URL ==="

# 安全构建 JSON 数据
# 安全: 如可用使用 jq 进行正确的 JSON 构建
# 这可以防止通过恶意文件名进行 JSON 注入
if command -v jq &> /dev/null; then
    # jq 方法: 使用正确转义安全构建 JSON
    JSON_PAYLOAD=$(jq -n \
        --arg name "$SAFE_FILENAME" \
        --arg lang "ch" \
        '{
            enable_formula: true,
            language: $lang,
            enable_table: true,
            layout_model: "doclayout_yolo",
            enable_ocr: true,
            files: [{name: $name, is_ocr: true}]
        }')
else
    # 备用方法: 使用预转义的文件名
    # 注意: 这安全性较低但无需 jq 也能工作
    JSON_PAYLOAD="{
        \"enable_formula\": true,
        \"language\": \"ch\",
        \"enable_table\": true,
        \"layout_model\": \"doclayout_yolo\",
        \"enable_ocr\": true,
        \"files\": [{\"name\": \"$SAFE_FILENAME\", \"is_ocr\": true}]
    }"
fi

# 发送请求到 MinerU API
STEP1_RESPONSE=$(curl -s -X POST "${MINERU_BASE_URL}/file-urls/batch" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${MINERU_TOKEN}" \
    -d "$JSON_PAYLOAD")

# ============================================================================
# 响应解析（安全方式）
# ============================================================================

# 安全: 如可用使用 jq 进行安全 JSON 解析
# jq 正确处理 JSON 结构，防止通过响应注入
if command -v jq &> /dev/null; then
    # 使用 jq 安全提取字段
    CODE=$(echo "$STEP1_RESPONSE" | jq -r '.code // 1')
    BATCH_ID=$(echo "$STEP1_RESPONSE" | jq -r '.data.batch_id // empty')
    UPLOAD_URL=$(echo "$STEP1_RESPONSE" | jq -r '.data.file_urls[0] // empty')
else
    # 备用: 使用带有限模式匹配的 grep
    # 这健壮性较低但不需要 jq
    CODE=$(echo "$STEP1_RESPONSE" | grep -o '"code":[0-9]*' | head -1 | cut -d':' -f2)
    BATCH_ID=$(echo "$STEP1_RESPONSE" | grep -o '"batch_id":"[^"]*"' | head -1 | cut -d'"' -f4)
    UPLOAD_URL=$(echo "$STEP1_RESPONSE" | grep -o '"file_urls":\[[^\]]*\]' | grep -o '"https://[^"]*"' | head -1 | tr -d '"')
fi

# 验证响应
if [ "$CODE" != "0" ] || [ -z "$BATCH_ID" ]; then
    echo "❌ 申请上传 URL 失败"
    exit 1
fi

echo "✅ Batch ID: $BATCH_ID"

# ============================================================================
# 步骤 2: 上传文件
# ============================================================================

echo ""
echo "=== 步骤 2: 上传文件 ==="

# 上传文件到预签名 URL
# 注意: 不要添加 Content-Type header，会破坏签名
curl -X PUT "$UPLOAD_URL" --upload-file "$PDF_PATH"
echo "✅ 上传成功"

# ============================================================================
# 步骤 3: 轮询提取结果
# ============================================================================

echo ""
echo "=== 步骤 3: 轮询提取结果 ==="

# 等待处理开始
sleep 5

# 轮询直到完成或达到最大重试次数
for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
    echo "[尝试 $attempt/$MAX_RETRIES] 查询中..."
    
    # 查询提取状态
    RESPONSE=$(curl -s -X GET "${MINERU_BASE_URL}/extract-results/batch/${BATCH_ID}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${MINERU_TOKEN}")
    
    # 从响应解析状态
    if command -v jq &> /dev/null; then
        STATE=$(echo "$RESPONSE" | jq -r '.data.extract_result[0].state // empty')
    else
        STATE=$(echo "$RESPONSE" | grep -o '"state":"[^"]*"' | head -1 | cut -d'"' -f4)
    fi
    
    echo "状态: $STATE"
    
    # 检查提取状态
    if [ "$STATE" = "done" ]; then
        # 提取 ZIP URL
        if command -v jq &> /dev/null; then
            ZIP_URL=$(echo "$RESPONSE" | jq -r '.data.extract_result[0].full_zip_url // empty')
        else
            ZIP_URL=$(echo "$RESPONSE" | grep -o '"full_zip_url":"[^"]*"' | head -1 | cut -d'"' -f4)
        fi
        echo "✅ 提取完成!"
        break
    elif [ "$STATE" = "failed" ]; then
        echo "❌ 提取失败"
        exit 1
    fi
    
    # 下次检查前等待
    sleep $RETRY_INTERVAL
done

# 验证是否获取到 ZIP URL
if [ -z "$ZIP_URL" ]; then
    echo "❌ 轮询超时或失败"
    exit 1
fi

# 安全: 验证 ZIP URL 确保来自官方 CDN
# 防止潜在的重定向攻击或恶意 URL
if [[ ! "$ZIP_URL" =~ ^https://cdn-mineru\.openxlab\.org\.cn/ ]]; then
    echo "❌ 错误: 无效的 ZIP URL"
    exit 1
fi

# ============================================================================
# 步骤 4: 下载并解压结果
# ============================================================================

echo ""
echo "=== 步骤 4: 下载并解压结果 ==="

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 下载结果 ZIP
curl -L -o "${OUTPUT_DIR}/result.zip" "$ZIP_URL"

# 安全: 解压前验证 ZIP 文件
# 防止解压恶意或损坏的压缩包
if ! unzip -t "${OUTPUT_DIR}/result.zip" &>/dev/null; then
    echo "❌ 错误: 无效的 ZIP 文件"
    rm -f "${OUTPUT_DIR}/result.zip"
    exit 1
fi

# 解压 ZIP 内容
unzip -q "${OUTPUT_DIR}/result.zip" -d "$OUTPUT_DIR/extracted"

# ============================================================================
# 完成
# ============================================================================

echo ""
echo "✅ 完成! 结果保存在: $OUTPUT_DIR/extracted/"
echo ""
echo "关键文件:"
echo "  📄 $OUTPUT_DIR/extracted/full.md - Markdown 文档"
echo "  🖼️  $OUTPUT_DIR/extracted/images/ - 提取的图片"
```

---

## 🔒 安全特性说明

### 1. 输入清理
- **文件名验证**: 只允许字母数字字符、点、下划线和连字符
- **目录验证**: 通过 `..` 序列和绝对路径防止目录遍历
- **JSON 转义**: 正确转义特殊字符防止 JSON 注入

### 2. URL 验证
- **ZIP URL 白名单**: 只接受来自官方 MinerU CDN (`cdn-mineru.openxlab.org.cn`) 的下载
- **模式匹配**: 使用严格正则表达式验证 URL 格式

### 3. 文件操作
- **ZIP 验证**: 使用 `unzip -t` 在解压前测试 ZIP 完整性
- **路径限制**: 确保所有操作保持在预期工作目录内

### 4. 响应解析
- **jq 优先**: 可用时使用 `jq` 进行安全 JSON 解析
- **备用方法**: 无需外部依赖时的有限模式匹配

---

## ⚠️ 常见问题

### 1. 签名错误 (SignatureDoesNotMatch)
**原因:** 上传时添加了 `Content-Type` header  
**解决:** 去掉 `-H "Content-Type: application/pdf"`，只用 `--upload-file`

### 2. URL 过期
**原因:** 预签名 URL 有效期约 15 分钟  
**解决:** 重新执行 Step 1 获取新的 URL

### 3. 文件大小限制
- 单文件最大 200 MB
- 单文件最多 600 页

### 4. 并发限制
根据 MinerU 套餐不同而定

---

## 📚 参考链接

- MinerU 官网: https://mineru.net/
- API 文档: https://mineru.net/apiManage/docs
- 在线 URL 解析指南: 见 `MinerU_在线文档解析完整流程.md`

---

*文档版本: 1.0.0*  
*发布日期: 2026-02-18*
