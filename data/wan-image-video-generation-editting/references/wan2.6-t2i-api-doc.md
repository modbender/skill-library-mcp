# 万相2.6文生图 (wan2.6-t2i) HTTP同步调用 API参考

> 来源：https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference

万相-文生图模型基于文本生成图像，支持多种艺术风格与写实摄影效果，满足多样化创意需求。

## 模型信息

| 模型名称 | 模型简介 | 输出图像格式 |
| --- | --- | --- |
| wan2.6-t2i | 万相2.6，支持在总像素面积与宽高比约束内自由选尺寸 | 图像分辨率：总像素在[1280\*1280, 1440\*1440]之间；宽高比：[1:4, 4:1]；格式：png |

**说明**：wan2.6模型支持HTTP同步调用、HTTP异步调用、Dashscope Python SDK调用和Dashscope Java SDK调用。

## 前提条件

在调用前，先获取API Key，再配置API Key到环境变量 `DASHSCOPE_API_KEY`。

> **重要**：北京、新加坡和弗吉尼亚地域拥有独立的 API Key 与请求地址，不可混用。

## HTTP同步调用

一次请求即可获得结果，流程简单，推荐大多数场景使用。

### Endpoint

- 北京地域：`POST https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`
- 新加坡地域：`POST https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`
- 弗吉尼亚地域：`POST https://dashscope-us.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`

### curl 示例

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--data '{
  "model": "wan2.6-t2i",
  "input": {
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "text": "一间有着精致窗户的花店，漂亮的木质门，摆放着花朵"
          }
        ]
      }
    ]
  },
  "parameters": {
    "prompt_extend": true,
    "watermark": false,
    "n": 1,
    "negative_prompt": "",
    "size": "1280*1280"
  }
}'
```

### 请求头（Headers）

| 参数 | 类型 | 必选 | 说明 |
| --- | --- | --- | --- |
| Content-Type | string | 是 | 必须设置为 `application/json` |
| Authorization | string | 是 | 身份认证。示例值：`Bearer sk-xxxx` |

### 请求体（Request Body）

#### model (string, 必选)

模型名称。示例值：`wan2.6-t2i`。

#### input (object, 必选)

输入的基本信息。

- **messages** (array, 必选)：请求内容数组。仅支持单轮对话。
  - **role** (string, 必选)：必须设置为 `user`。
  - **content** (array, 必选)：消息内容数组。
    - **text** (string, 必选)：正向提示词，用于描述期望生成的图像内容、风格和构图。支持中英文，长度不超过2100个字符，超过部分自动截断。**注意**：仅支持传入一个text。

#### parameters (object, 可选)

图像处理参数。

| 参数 | 类型 | 必选 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| negative_prompt | string | 否 | - | 反向提示词，描述不希望出现的内容。长度不超过500字符。 |
| size | string | 否 | `1280*1280` | 输出图像分辨率，格式为`宽*高`。总像素在[1280\*1280, 1440\*1440]之间，宽高比[1:4, 4:1]。 |
| n | integer | 否 | 4 | 生成图片数量，取值1~4。**按张计费**，测试建议设为1。 |
| prompt_extend | bool | 否 | true | 是否开启提示词智能改写。开启后增加3-4秒耗时。 |
| watermark | bool | 否 | false | 是否添加"AI生成"水印（右下角）。 |
| seed | integer | 否 | 随机 | 随机数种子，取值[0, 2147483647]。相同seed可使生成内容保持相对稳定。 |

**常见比例推荐分辨率：**

| 比例 | 分辨率 |
| --- | --- |
| 1:1 | 1280\*1280 |
| 3:4 | 1104\*1472 |
| 4:3 | 1472\*1104 |
| 9:16 | 960\*1696 |
| 16:9 | 1696\*960 |

### 响应参数

#### 成功响应示例

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
  "request_id": "815505c6-7c3d-49d7-b197-xxxxx"
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
  "request_id": "a4d78a5f-655f-9639-8437-xxxxxx",
  "code": "InvalidParameter",
  "message": "num_images_per_prompt must be 1"
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 错误码（成功时不返回） |
| message | string | 错误详细信息（成功时不返回） |
