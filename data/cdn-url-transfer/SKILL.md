---
name: cdn-url-transfer
description: 将模型配置中的外部示例 URL（fal.media、googleapis 等）转存到速推 CDN（cdn-video.51sux.com），并更新代码和校验 API 返回。当用户提到"转存 CDN"、"替换示例链接"、"转存链接"、"CDN 地址"、"示例 URL 替换"时使用此 skill。
---

# 模型示例 URL 转存 CDN

将模型配置中的外部文件链接（fal.media、googleapis 等）转存到速推 CDN，确保示例资源稳定可访问。

## 需替换的 URL 位置

每个模型最多有 **3 处** URL 需要替换，全部在 `model_registry.py` 中：

| 位置 | 字段 | 说明 |
|------|------|------|
| 1 | `parameters[].examples` | 输入参数的示例值（图片/视频 URL） |
| 2 | `output_example` | 输出结果示例中的媒体 URL |
| 3 | executor 的 `get_params_schema()` | 执行器中的参数 schema（与位置 1 保持同步） |

**关键文件：**
- **主数据源**（docs API 读取）：`translate_api/app/api/v3/transports/mcp/model_registry.py`
- **执行器**（运行时使用）：`translate_api/app/api/v3/executors/` 下对应的 executor 文件

## 操作流程

### Step 1: 扫描目标模型的外部 URL

用 Grep 在 `model_registry.py` 中搜索目标模型相关的外部域名：

```
搜索模式: fal\.media|googleapis\.com|其他外部域名
范围: model_registry.py 中目标模型的注册块
```

同时搜索对应 executor 文件中的 `examples` 字段。

### Step 2: 上传文件到 CDN

#### 方案 A：MCP `upload_image` 工具（仅限小图片 base64）

> **已知问题**：`upload_image` 的 `image_url` 参数（URL 转存模式）**经常失败**，返回空错误。
> 仅 `image_data`（base64 模式）可靠，但受工具参数大小限制，仅适合 **< 100KB** 的小图片。

```
upload_image(
  image_data="<base64字符串>",
  file_name="模型名_用途.png",
  folder="模型名-examples"
)
```

#### 方案 B：curl 下载 + TOS Python SDK 直传（推荐）

这是最可靠的方案，支持**任意文件类型和大小**（图片、音频、视频）。

**第一步：用 curl 下载到本地**（curl 不走 Python 代理，更稳定）

```bash
curl -sL -o /tmp/文件名.png "原始外部URL"
curl -sL -o /tmp/文件名.mp3 "原始外部URL"
```

**第二步：用 TOS SDK 上传到 CDN**

```python
import tos

TOS_CONFIG = {
    'access_key': 'AKLTZTBhMDdlYTdlODdlNGFlNGFjNTliOGEwOWFkNzk0Mjk',
    'secret_key': 'TnpVMk9EUmtNREkzWmpjNU5EazVNVGxsTkRnMk9XUXlZMk15WldRNVpqUQ==',
    'endpoint': 'tos-cn-guangzhou.volces.com',
    'region': 'cn-guangzhou',
    'bucket_name': 'fal-task',
    'public_domain': 'https://cdn-video.51sux.com'
}

client = tos.TosClientV2(
    TOS_CONFIG['access_key'],
    TOS_CONFIG['secret_key'],
    TOS_CONFIG['endpoint'],
    TOS_CONFIG['region']
)

# 读取本地文件并上传
with open('/tmp/文件名.png', 'rb') as f:
    data = f.read()

object_key = '{模型名}-examples/{文件名}.png'
client.put_object(
    bucket=TOS_CONFIG['bucket_name'],
    key=object_key,
    content=data,
    content_type='image/png'  # 按实际类型设置
)

cdn_url = f"{TOS_CONFIG['public_domain']}/{object_key}"
print(cdn_url)
```

#### 方案 C：catbox 中转（备选）

当 Google Cloud Storage 等外部链接从本机无法直接访问时，可先用 catbox 做跳板：

```bash
# 1. 先用 curl 下载（如果 curl 能访问的话）
curl -sL -o /tmp/文件.png "原始外部URL"
# 2. 上传到 catbox 获取临时链接
curl -sF "reqtype=fileupload" -F "fileToUpload=@/tmp/文件.png" https://catbox.moe/user/api.php
# 3. 再从 catbox 链接走方案 B 上传到 TOS
```

> catbox 链接仅做中转用，最终必须传到 TOS CDN。catbox 文件可能过期。

**CDN 存储路径命名规范：**

| 元素 | 规范 | 示例 |
|------|------|------|
| 文件夹 | `{模型简称}-examples/` | `omnihuman-examples/`、`dreamactor-examples/` |
| 文件名 | `{模型简称}_{用途}.{扩展名}` | `omnihuman_v15_input_image.png` |

**常见 content_type 对照：**

| 文件类型 | content_type |
|----------|-------------|
| PNG 图片 | `image/png` |
| JPEG 图片 | `image/jpeg` |
| MP4 视频 | `video/mp4` |
| MP3 音频 | `audio/mpeg` |
| WAV 音频 | `audio/wav` |

### Step 3: 替换代码中的 URL

按顺序替换以下位置：

1. **model_registry.py** 中 `parameters[].examples` 里的 URL
2. **model_registry.py** 中 `output_example` 里的 URL
3. **executor 文件** 中 `get_params_schema()` 里的 `examples` URL

使用 StrReplace 工具精确替换，每次替换一个 URL。

### Step 4: 重启服务并校验

> **注意**：`kill -HUP` 对 multiprocessing worker 进程无效。需要完整重启服务。

```bash
# 1. 找到 8002 端口进程
lsof -i :8002 -P | head -5

# 2. 杀掉旧进程
kill <PID>

# 3. 以 reload 模式重启（方便后续修改自动生效）
cd translate_api && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# 4. 等待启动完成
sleep 3

# 5. 请求 docs API 校验
curl -s "http://127.0.0.1:8002/api/v3/models/<URL编码的模型ID>/docs" \
  -H "Content-Type: application/json" | python3 -c "
import sys, json, re
data = json.load(sys.stdin)['data']
raw = json.dumps(data)

# 检查外部域名残留
external = re.findall(r'https?://(?:v3b?\.fal\.media|storage\.googleapis\.com)[^\"\s]*', raw)
if external:
    print('❌ 仍有外部链接残留：')
    for u in external:
        print(f'  {u}')
else:
    print('✅ 所有外部链接已替换为 CDN 地址')

# 展示当前所有 CDN 链接
cdns = re.findall(r'https?://cdn-video\.51sux\.com[^\"\s]*', raw)
if cdns:
    print(f'\n当前 CDN 链接（共 {len(cdns)} 个）：')
    for u in set(cdns):
        print(f'  ✅ {u}')
"

# 6. 验证 CDN 文件可访问
curl -sI "CDN链接" | head -3
# 应返回 HTTP/2 200 + 正确的 content-type
```

## 校验清单

- [ ] `model_registry.py` 中参数 examples 已替换
- [ ] `model_registry.py` 中 output_example 已替换
- [ ] executor 文件中 get_params_schema 的 examples 已替换
- [ ] 服务已重启（旧进程可能是 orphaned multiprocessing worker，PPID=1）
- [ ] docs API 返回无外部域名残留
- [ ] 每个 CDN 链接均返回 HTTP 200 + 正确 content-type

## 注意事项

### 1. MCP `upload_image` 工具的局限性

- **URL 转存模式（`image_url` 参数）不可靠**，经实测对 googleapis、catbox 等多种域名均返回空错误
- **base64 模式可用但有大小限制**，仅适合 < 100KB 的小文件
- **不支持非图片文件**（音频、视频），即使指定 content_type 也不行
- **推荐使用方案 B**（curl + TOS SDK），支持任意文件类型和大小

### 2. 网络/代理问题

- **Python `requests` 库**走系统代理，访问 catbox.moe 等外部站点会报 `ProxyError`
- **`curl` 命令**通常不受此影响，可正常下载外部文件
- 因此下载外部文件务必用 `curl`，不要用 Python `requests`

### 3. 服务重启

- API 进程可能是 **orphaned multiprocessing worker**（PPID=1），`kill -HUP` 无效
- 必须 `kill` 进程后手动重启
- 建议用 `--reload` 模式启动，后续代码修改自动生效
- 重启后需等待 2-3 秒再校验，确保模块加载完成

### 4. 存储信息

| 配置项 | 值 |
|--------|-----|
| 存储服务 | 火山 TOS（cn-guangzhou） |
| Bucket | `fal-task` |
| CDN 域名 | `https://cdn-video.51sux.com` |
| SDK | `import tos`（需 `pip install tos`） |
| 最终 URL 格式 | `https://cdn-video.51sux.com/{object_key}` |

### 5. 常见外部域名（需替换的源）

| 域名 | 来源 |
|------|------|
| `storage.googleapis.com/falserverless/` | fal.ai 官方示例 |
| `v3.fal.media/` | fal.ai 生成结果 |
| `v3b.fal.media/` | fal.ai 生成结果（备用） |
| `files.catbox.moe/` | catbox 临时图床（仅中转用） |
