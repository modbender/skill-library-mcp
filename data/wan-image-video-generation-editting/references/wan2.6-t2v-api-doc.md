# 万相2.6文生视频 (wan2.6-t2v) HTTP异步调用 API参考

> 来源：https://help.aliyun.com/zh/model-studio/text-to-video-api-reference

万相文生视频模型基于文本提示词，生成一段流畅的视频。

## 模型信息

| 模型名称 | 默认分辨率 | 可选分辨率 | 说明 |
| --- | --- | --- | --- |
| wan2.6-t2v | 1920\*1080 (1080P) | 720P、1080P 对应的所有分辨率 | 支持自动配音、多镜头叙事 |

## 前提条件

已获取API Key并配置到环境变量 `DASHSCOPE_API_KEY`。

> **重要**：北京、新加坡和弗吉尼亚地域拥有独立的 API Key 与请求地址，不可混用。

## HTTP异步调用

文生视频任务耗时较长（通常1-5分钟），API采用异步调用。流程包含 **"创建任务 → 轮询获取"** 两个步骤。

---

## 步骤1：创建任务获取任务ID

### Endpoint

- 北京地域：`POST https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- 新加坡地域：`POST https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- 弗吉尼亚地域：`POST https://dashscope-us.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`

> 创建成功后使用返回的 `task_id` 查询结果，task_id 有效期24小时。请勿重复创建任务。

### curl 示例

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
-H 'X-DashScope-Async: enable' \
-H "Authorization: Bearer $DASHSCOPE_API_KEY" \
-H 'Content-Type: application/json' \
-d '{
  "model": "wan2.6-t2v",
  "input": {
    "prompt": "一只小猫在月光下奔跑"
  },
  "parameters": {
    "size": "1920*1080",
    "prompt_extend": true,
    "duration": 5
  }
}'
```

#### 多镜头叙事示例（仅wan2.6支持）

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
-H 'X-DashScope-Async: enable' \
-H "Authorization: Bearer $DASHSCOPE_API_KEY" \
-H 'Content-Type: application/json' \
-d '{
  "model": "wan2.6-t2v",
  "input": {
    "prompt": "一幅史诗级可爱的场景...",
    "audio_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250923/hbiayh/从军行.mp3"
  },
  "parameters": {
    "size": "1280*720",
    "prompt_extend": true,
    "duration": 10,
    "shot_type": "multi"
  }
}'
```

### 请求头（Headers）

| 参数 | 类型 | 必选 | 说明 |
| --- | --- | --- | --- |
| Content-Type | string | 是 | 必须设置为 `application/json` |
| Authorization | string | 是 | 身份认证。示例值：`Bearer sk-xxxx` |
| X-DashScope-Async | string | **是** | 必须设置为 `enable`。缺少将报错 "current user api does not support synchronous calls" |

### 请求体（Request Body）

#### model (string, 必选)

模型名称。示例值：`wan2.6-t2v`。

#### input (object, 必选)

| 参数 | 类型 | 必选 | 说明 |
| --- | --- | --- | --- |
| prompt | string | 是 | 文本提示词。支持中英文，长度不超过1500个字符（wan2.6），超过自动截断。 |
| negative_prompt | string | 否 | 反向提示词，描述不希望在视频中出现的内容。长度不超过500字符。 |
| audio_url | string | 否 | 音频文件URL（wan2.6支持）。格式：wav、mp3。时长：3~30s。文件≤15MB。不提供则自动配音。 |

#### parameters (object, 可选)

| 参数 | 类型 | 必选 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| size | string | 否 | `1920*1080` | 视频分辨率，格式`宽*高`。**必须为具体数值**，不能为480P等。wan2.6-t2v支持720P和1080P对应的所有分辨率。**size直接影响费用**。 |
| duration | integer | 否 | 5 | 视频时长（秒）。wan2.6-t2v取值范围：[1, 15]。**duration直接影响费用**。 |
| prompt_extend | bool | 否 | true | 是否开启提示词智能改写。 |
| shot_type | string | 否 | - | 设为 `multi` 启用多镜头叙事（仅wan2.6支持，需同时开启prompt_extend）。 |
| watermark | bool | 否 | false | 是否添加"AI生成"水印。 |
| seed | integer | 否 | 随机 | 随机数种子，取值[0, 2147483647]。 |

**wan2.6-t2v 可选分辨率（720P和1080P）：**

| 分辨率级别 | 可选值 |
| --- | --- |
| 720P | 1280\*720, 720\*1280, 960\*960 |
| 1080P | 1920\*1080, 1080\*1920, 1440\*1440 |

### 创建任务响应

#### 成功响应示例

```json
{
  "request_id": "xxxxx-xxxxx",
  "output": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "task_status": "PENDING"
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| request_id | string | 请求唯一标识 |
| output.task_id | string | 任务ID，用于轮询获取结果。有效期24小时。 |
| output.task_status | string | 任务状态：`PENDING` |

#### 异常响应

```json
{
  "request_id": "xxxxx",
  "code": "InvalidParameter",
  "message": "error details"
}
```

---

## 步骤2：轮询获取任务结果

### Endpoint

- 北京地域：`GET https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}`
- 新加坡地域：`GET https://dashscope-intl.aliyuncs.com/api/v1/tasks/{task_id}`
- 弗吉尼亚地域：`GET https://dashscope-us.aliyuncs.com/api/v1/tasks/{task_id}`

### curl 示例

```bash
curl -X GET "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}" \
-H "Authorization: Bearer $DASHSCOPE_API_KEY"
```

### 请求头（Headers）

| 参数 | 类型 | 必选 | 说明 |
| --- | --- | --- | --- |
| Authorization | string | 是 | 身份认证。示例值：`Bearer sk-xxxx` |

### 成功响应示例（任务完成）

```json
{
  "request_id": "xxxxx-xxxxx",
  "output": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "task_status": "SUCCEEDED",
    "task_metrics": {
      "TOTAL": 1,
      "SUCCEEDED": 1,
      "FAILED": 0
    },
    "video_url": "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/xxxx.mp4"
  },
  "usage": {
    "video_count": 1,
    "video_duration": 5,
    "video_ratio": "1920*1080"
  }
}
```

### 任务进行中响应示例

```json
{
  "request_id": "xxxxx-xxxxx",
  "output": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "task_status": "RUNNING",
    "task_metrics": {
      "TOTAL": 1,
      "SUCCEEDED": 0,
      "FAILED": 0
    }
  }
}
```

### 响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| request_id | string | 请求唯一标识 |
| output.task_id | string | 任务ID |
| output.task_status | string | 任务状态：`PENDING`、`RUNNING`、`SUCCEEDED`、`FAILED` |
| output.task_metrics | object | 任务统计（TOTAL/SUCCEEDED/FAILED） |
| output.video_url | string | 生成视频的URL（仅SUCCEEDED时返回），有效期24小时，请及时下载 |
| output.code | string | 错误码（仅FAILED时返回） |
| output.message | string | 错误信息（仅FAILED时返回） |
| usage.video_count | integer | 生成视频数量 |
| usage.video_duration | integer | 视频时长（秒） |
| usage.video_ratio | string | 视频分辨率 |
