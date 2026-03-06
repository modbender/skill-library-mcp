# MinerU 在线文档解析完整流程（URL 方式，安全加固版本）

> 直接使用 MinerU API 解析在线 PDF（无需本地上传），支持公式、表格、OCR 识别
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

## 🚀 完整流程（2 个步骤）

在线文档解析比本地上传**更简洁**，只需 **2 步**！

### Step 1: 提交解析任务（提供 URL）

**命令：**
```bash
curl -X POST "${MINERU_BASE_URL}/extract/task" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${MINERU_TOKEN}" \
    -d '{
        "url": "https://example.com/path/to/your.pdf",
        "enable_formula": true,
        "language": "ch",
        "enable_table": true,
        "layout_model": "doclayout_yolo"
    }'
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | ✅ **是** | 在线 PDF 的完整 URL（支持 http/https） |
| `enable_formula` | bool | 否 | 启用公式识别，默认 true |
| `enable_table` | bool | 否 | 启用表格识别，默认 true |
| `language` | string | 否 | 语言：`ch`(中文)/`en`(英文)/`auto` |
| `layout_model` | string | 否 | 版面模型：`doclayout_yolo`(快)/`layoutlmv3`(准) |

**成功返回值：**
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  }
}
```

**提取关键字段：**
- `task_id`：任务 ID，用于后续查询结果

---

### Step 2: 轮询提取结果

**命令：**
```bash
curl -X GET "${MINERU_BASE_URL}/extract/task/YOUR_TASK_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${MINERU_TOKEN}"
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `YOUR_TASK_ID` | Step 1 返回的 `task_id` |

**轮询策略：**
- 首次查询前等待 5 秒
- 每隔 5 秒查询一次
- 最多轮询 60 次（约 5 分钟）

**返回值状态说明：**

| state | 含义 | 操作 |
|-------|------|------|
| `done` | ✅ 提取完成 | 获取 `full_zip_url` 下载结果 |
| `running` | 🔄 正在处理 | 继续轮询 |
| `pending` | ⏳ 排队中 | 继续轮询 |
| `failed` | ❌ 提取失败 | 查看 `err_msg` 错误信息 |

**成功返回值（done 状态）：**
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "state": "done",
    "err_msg": "",
    "full_zip_url": "https://cdn-mineru.openxlab.org.cn/pdf/.../xxxx.zip"
  }
}
```

**提取关键字段：**
- `full_zip_url`：结果 ZIP 包下载地址

---

### Step 3: 下载并解压结果

**命令：**
```bash
# 下载 ZIP 包
curl -L -o "result.zip" \
  "YOUR_FULL_ZIP_URL_FROM_STEP2"

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

### 在线文档解析脚本（online_parse.sh）

```bash
#!/bin/bash
# MinerU 在线文档解析脚本（安全加固版本）
# 用法: ./online_parse.sh <PDF_URL> [输出目录]
#
# 本脚本实现以下安全措施：
# - 通过输入清理防止 JSON 注入攻击
# - 通过路径验证防止目录遍历攻击
# - 通过 URL 验证防止恶意 URL 攻击

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

# 函数: validate_url
# 用途: 验证 PDF URL 格式并防止恶意 URL
# 安全: 确保 URL 指向 PDF 文件并使用 http/https 协议
# 参数:
#   $1 - 输入 URL
# 返回: 验证后的 URL
# 退出: 如果 URL 无效
validate_url() {
    local url="$1"
    
    # 安全检查: 验证 URL 格式
    # 必须以 http:// 或 https:// 开头，以 .pdf 结尾
    # 这可以防止：
    # - 文件协议攻击 (file:///etc/passwd)
    # - JavaScript 协议攻击 (javascript:alert(1))
    # - 其他恶意协议
    if [[ ! "$url" =~ ^https?://[a-zA-Z0-9.-]+/.*\.pdf$ ]]; then
        echo "❌ 错误: 无效的 URL 格式。必须是 http(s)://.../...pdf" >&2
        exit 1
    fi
    
    echo "$url"
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

# 从参数获取 PDF URL
PDF_URL="${1:-}"
if [ -z "$PDF_URL" ]; then
    echo "❌ 错误: 请提供 PDF URL 地址"
    echo "用法: $0 <PDF_URL> [输出目录]"
    echo ""
    echo "示例:"
    echo "  $0 \"https://arxiv.org/pdf/2410.17247.pdf\""
    exit 1
fi

# 安全: 验证 URL 格式防止恶意 URL
PDF_URL=$(validate_url "$PDF_URL")

# 创建 JSON 安全版本的 URL
SAFE_URL=$(escape_json "$PDF_URL")

# 获取输出目录，使用默认值
OUTPUT_DIR="${2:-online_result}"

# 安全: 验证输出目录防止目录遍历
OUTPUT_DIR=$(validate_dirname "$OUTPUT_DIR")

# 轮询配置
MAX_RETRIES=60          # 最大状态检查次数
RETRY_INTERVAL=5        # 检查间隔秒数

# ============================================================================
# 步骤 1: 提交解析任务
# ============================================================================

echo "=== 步骤 1: 提交解析任务 ==="
echo "PDF URL: ${PDF_URL:0:60}..."

# 安全构建 JSON 数据
# 安全: 如可用使用 jq 进行正确的 JSON 构建
if command -v jq &> /dev/null; then
    # jq 方法: 使用正确转义安全构建 JSON
    JSON_PAYLOAD=$(jq -n \
        --arg url "$SAFE_URL" \
        --arg lang "ch" \
        '{
            url: $url,
            enable_formula: true,
            language: $lang,
            enable_table: true,
            layout_model: "doclayout_yolo"
        }')
else
    # 备用方法: 使用预转义的 URL
    JSON_PAYLOAD="{
        \"url\": \"$SAFE_URL\",
        \"enable_formula\": true,
        \"language\": \"ch\",
        \"enable_table\": true,
        \"layout_model\": \"doclayout_yolo\"
    }"
fi

# 发送请求到 MinerU API
STEP1_RESPONSE=$(curl -s -X POST "${MINERU_BASE_URL}/extract/task" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${MINERU_TOKEN}" \
    -d "$JSON_PAYLOAD")

# ============================================================================
# 响应解析（安全方式）
# ============================================================================

# 安全: 如可用使用 jq 进行安全 JSON 解析
if command -v jq &> /dev/null; then
    CODE=$(echo "$STEP1_RESPONSE" | jq -r '.code // 1')
    TASK_ID=$(echo "$STEP1_RESPONSE" | jq -r '.data.task_id // empty')
else
    CODE=$(echo "$STEP1_RESPONSE" | grep -o '"code":[0-9]*' | head -1 | cut -d':' -f2)
    TASK_ID=$(echo "$STEP1_RESPONSE" | grep -o '"task_id":"[^"]*"' | head -1 | cut -d'"' -f4)
fi

if [ "$CODE" != "0" ] || [ -z "$TASK_ID" ]; then
    echo "❌ 提交任务失败"
    exit 1
fi

echo "✅ 任务提交成功"
echo "Task ID: $TASK_ID"
echo ""

# ============================================================================
# 步骤 2: 轮询提取结果
# ============================================================================

echo "=== 步骤 2: 轮询提取结果 ==="
echo "等待 5 秒让系统开始处理..."
sleep 5

# 轮询直到完成或达到最大重试次数
for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
    echo "[尝试 $attempt/$MAX_RETRIES] 查询中..."
    
    # 查询提取状态
    RESPONSE=$(curl -s -X GET "${MINERU_BASE_URL}/extract/task/${TASK_ID}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${MINERU_TOKEN}")
    
    # 从响应解析状态
    if command -v jq &> /dev/null; then
        STATE=$(echo "$RESPONSE" | jq -r '.data.state // empty')
    else
        STATE=$(echo "$RESPONSE" | grep -o '"state":"[^"]*"' | head -1 | cut -d'"' -f4)
    fi
    
    echo "状态: $STATE"
    
    # 检查提取状态
    if [ "$STATE" = "done" ]; then
        # 提取 ZIP URL
        if command -v jq &> /dev/null; then
            ZIP_URL=$(echo "$RESPONSE" | jq -r '.data.full_zip_url // empty')
        else
            ZIP_URL=$(echo "$RESPONSE" | grep -o '"full_zip_url":"[^"]*"' | head -1 | cut -d'"' -f4)
        fi
        echo "✅ 提取完成!"
        break
    elif [ "$STATE" = "failed" ]; then
        # 提取错误信息
        if command -v jq &> /dev/null; then
            ERR_MSG=$(echo "$RESPONSE" | jq -r '.data.err_msg // "未知错误"')
        else
            ERR_MSG=$(echo "$RESPONSE" | grep -o '"err_msg":"[^"]*"' | head -1 | cut -d'"' -f4)
        fi
        echo "❌ 提取失败: $ERR_MSG"
        exit 1
    fi
    
    # 下次检查前等待
    sleep $RETRY_INTERVAL
done

# 验证是否获取到 ZIP URL
if [ -z "$ZIP_URL" ]; then
    echo "❌ 轮询超时"
    exit 1
fi

# 安全: 验证 ZIP URL 确保来自官方 CDN
if [[ ! "$ZIP_URL" =~ ^https://cdn-mineru\.openxlab\.org\.cn/ ]]; then
    echo "❌ 错误: 无效的 ZIP URL"
    exit 1
fi

# ============================================================================
# 下载并解压结果
# ============================================================================

echo ""
echo "=== 下载并解压结果 ==="

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 下载结果 ZIP
curl -L -o "${OUTPUT_DIR}/result.zip" "$ZIP_URL"

# 安全: 解压前验证 ZIP 文件
if ! unzip -t "${OUTPUT_DIR}/result.zip" &>/dev/null; then
    echo "❌ 错误: 无效的 ZIP 文件"
    rm -f "${OUTPUT_DIR}/result.zip"
    exit 1
fi

# 解压 ZIP 内容
echo "解压中..."
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

### 1. URL 验证
- **格式检查**: 确保 URL 以 http:// 或 https:// 开头，以 .pdf 结尾
- **协议白名单**: 防止 file://、javascript:// 等危险协议
- **模式匹配**: 使用严格正则验证 URL 结构

### 2. 输入清理
- **目录验证**: 通过 `..` 序列防止目录遍历
- **路径限制**: 阻止可能逃离工作目录的绝对路径
- **JSON 转义**: 正确转义特殊字符防止 JSON 注入

### 3. 文件操作
- **ZIP 验证**: 解压前测试 ZIP 完整性
- **URL 白名单**: 只接受来自官方 MinerU CDN 的下载
- **安全解析**: 可用时使用 jq 进行安全 JSON 解析

---

## 🔧 使用示例

### 示例 1: 解析 arXiv 论文

```bash
export MINERU_TOKEN="your_token_here"

./online_parse.sh "https://arxiv.org/pdf/2410.17247.pdf"
```

### 示例 2: 解析在线 PDF

```bash
export MINERU_TOKEN="your_token_here"

./online_parse.sh \
  "https://www.example.com/documents/report.pdf" \
  "my_report"
```

### 示例 3: 手动执行各步骤

```bash
export MINERU_TOKEN="your_token_here"

# 步骤 1: 提交任务
curl -X POST "https://mineru.net/api/v4/extract/task" \
  -H "Authorization: Bearer $MINERU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://arxiv.org/pdf/2410.17247.pdf",
    "enable_formula": true,
    "language": "en"
  }'
# 返回: {"task_id": "xxx"}

# 步骤 2: 轮询结果（循环直到 state=done）
curl "https://mineru.net/api/v4/extract/task/xxx" \
  -H "Authorization: Bearer $MINERU_TOKEN"

# 步骤 3: 下载解压
curl -L -o result.zip "https://cdn-mineru.openxlab.org.cn/pdf/.../xxx.zip"
unzip -q result.zip -d extracted/
```

---

## 📊 在线解析 vs 本地上传对比

| 特性 | **在线 URL 解析** | **本地上传解析** |
|------|-------------------|------------------|
| **步骤数** | 2 步 | 4 步 |
| **是否需要上传** | ❌ 否 | ✅ 是 |
| **平均耗时** | 10-20 秒 | 30-60 秒 |
| **网络要求** | 只需下载结果 | 需要上传+下载 |
| **适用场景** | 文件已在线（arXiv、网站等） | 本地文件 |
| **文件大小限制** | 受限于源服务器 | 200MB |

---

## ⚠️ 注意事项

1. **URL 可访问性**: 确保提供的 URL 是公开可访问的，MinerU 服务器需要能下载该文件
2. **URL 编码**: 如果 URL 包含中文或特殊字符，确保已正确编码
3. **Token 安全**: 不要将 MINERU_TOKEN 硬编码在脚本中
4. **文件限制**: 源文件大小建议不超过 200MB

---

## 📚 参考文档

| 文档 | 说明 |
|------|------|
| `MinerU_本地文档解析完整流程.md` | 本地 PDF 解析的详细 curl 命令和参数说明（中文） |

外部资源:
- MinerU 官网: https://mineru.net/
- API 文档: https://mineru.net/apiManage/docs
- GitHub: https://github.com/opendatalab/MinerU

---

*文档版本: 1.0.0*  
*发布日期: 2026-02-18*
