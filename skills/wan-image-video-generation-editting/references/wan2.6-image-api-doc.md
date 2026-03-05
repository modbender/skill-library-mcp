# 万相2.6图像编辑 (wan2.6-image) HTTP同步调用 API参考

> 来源：https://help.aliyun.com/zh/model-studio/wan-image-generation-api-reference

万相图像生成模型支持图像编辑、图文混排输出，满足多样化生成与集成需求。

## 模型信息

| 模型名称 | 模型简介 | 输出图像规格 |
| --- | --- | --- |
| wan2.6-image | 万相2.6 image，支持图像编辑和图文混排输出 | 图片格式：PNG。分辨率参见size参数。 |

## 前提条件

已获取API Key并配置到环境变量 `DASHSCOPE_API_KEY`。

> **重要**：北京、新加坡和弗吉尼亚地域拥有独立的 API Key 与请求地址，不可混用。

## HTTP同步调用

一次请求即可获得结果，流程简单，推荐大多数场景使用。

### Endpoint

- 北京地域：`POST https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`
- 新加坡地域：`POST https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`
- 弗吉尼亚地域：`POST https://dashscope-us.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`

### curl 示例 — 图像编辑

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--data '{
  "model": "wan2.6-image",
  "input": {
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "text": "参考图1的风格和图2的背景，生成番茄炒蛋"
          },
          {
            "image": "https://cdn.wanx.aliyuncs.com/tmp/pressure/umbrella1.png"
          },
          {
            "image": "https://img.alicdn.com/imgextra/i3/O1CN01SfG4J41UYn9WNt4X1_!!6000000002530-49-tps-1696-960.webp"
          }
        ]
      }
    ]
  },
  "parameters": {
    "prompt_extend": true,
    "watermark": false,
    "n": 1,
    "enable_interleave": false,
    "size": "1280*1280"
  }
}'
```

### 请求头（Headers）

| 参数 | 类型 | 必选 | 说明 |
| --- | --- | --- | --- |
| Content-Type | string | 是 | 必须设置为 `application/json` |
| Authorization | string | 是 | 身份认证。示例值：`Bearer sk-xxxx` |
| X-DashScope-Sse | string | 否 | 仅当 `enable_interleave=true`（图文混排模式）时必须设为 `enable`，其他情况忽略 |

### 请求体（Request Body）

#### model (string, 必选)

模型名称。设置为 `wan2.6-image`。

#### input (object, 必选)

- **messages** (array, 必选)：请求内容数组。仅支持单轮对话。
  - **role** (string, 必选)：固定设置为 `user`。
  - **content** (array, 必选)：消息内容数组。
    - **text** (string, 必选)：正向提示词。支持中英文，长度不超过2000个字符。content数组中**必须且只能**包含一个text对象。
    - **image** (string, 可选)：输入图像的URL或Base64编码字符串。
      - 图像格式：JPEG、JPG、PNG（不支持透明通道）、BMP、WEBP
      - 图像分辨率：宽高范围均为 [384, 5000] 像素
      - 文件大小：不超过10MB
      - 图像数量限制：
        - `enable_interleave=false`（图像编辑）：必须输入 1~4 张图像
        - `enable_interleave=true`（图文混排）：可输入 0~1 张图像
      - 多张图像时，在content数组中传入多个image对象，按数组顺序定义图像顺序

#### parameters (object, 可选)

| 参数 | 类型 | 必选 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| negative_prompt | string | 否 | - | 反向提示词，描述不希望出现的内容。长度不超过500字符。 |
| size | string | 否 | - | 输出图像分辨率，格式`宽*高`。总像素在[768\*768, 1280\*1280]之间，宽高比[1:4, 4:1]。 |
| enable_interleave | bool | 否 | false | `false`=图像编辑模式（多图输入），`true`=图文混排模式（0~1张图输入） |
| n | integer | 否 | 4 | 图像编辑模式下生成图片数量，1~4。图文混排模式下必须为1。 |
| max_images | integer | 否 | 5 | 仅 `enable_interleave=true` 时生效。生成图像的最大数量，1~5。 |
| prompt_extend | bool | 否 | true | 仅图像编辑模式下生效。是否开启提示词智能改写。 |
| stream | bool | 否 | false | 是否流式输出。图文混排模式下必须设为true。 |
| watermark | bool | 否 | false | 是否添加"AI生成"水印（右下角）。 |
| seed | integer | 否 | 随机 | 随机数种子，取值[0, 2147483647]。 |

**常见比例推荐分辨率（图像编辑模式）：**

| 比例 | 分辨率 |
| --- | --- |
| 1:1 | 1280\*1280 或 1024\*1024 |
| 2:3 | 800\*1200 |
| 3:2 | 1200\*800 |
| 3:4 | 960\*1280 |
| 4:3 | 1280\*960 |
| 9:16 | 720\*1280 |
| 16:9 | 1280\*720 |
| 21:9 | 1344\*576 |

**输出图像尺寸规则：**

- **指定 size**：系统以指定宽高为目标，将实际输出调整为不大于指定值的最大16的倍数。
- **未指定 size**：
  - `enable_interleave=true` 且输入图像总像素 ≤ 1280\*1280 时，输出总像素与输入一致
  - `enable_interleave=false` 时，输出总像素固定为 1280\*1280
  - 宽高比：单图输入与输入一致；多图输入与最后一张输入一致

### 响应参数

#### 成功响应示例（图像编辑模式）

```json
{
  "output": {
    "choices": [
      {
        "finish_reason": "stop",
        "message": {
          "content": [
            {
              "image": "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/xxxx.png?Expires=xxx",
              "type": "image"
            }
          ],
          "role": "assistant"
        }
      }
    ],
    "finished": true
  },
  "usage": {
    "image_count": 1,
    "input_tokens": 0,
    "output_tokens": 0,
    "size": "1280*1280",
    "total_tokens": 0
  },
  "request_id": "xxxxx-xxxxx"
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| output.choices | array | 模型生成的输出内容 |
| output.choices[].finish_reason | string | 停止原因，自然停止为 `stop` |
| output.choices[].message.role | string | 固定为 `assistant` |
| output.choices[].message.content[].image | string | 生成图像URL（PNG格式），有效期24小时，请及时下载 |
| output.choices[].message.content[].type | string | 固定为 `image` |
| output.finished | boolean | 任务是否结束 |
| usage.image_count | integer | 生成图像张数 |
| usage.size | string | 生成图像分辨率 |
| request_id | string | 请求唯一标识 |

#### 异常响应示例

```json
{
  "request_id": "xxxxx-xxxxx",
  "code": "InvalidParameter",
  "message": "error details"
}
```
