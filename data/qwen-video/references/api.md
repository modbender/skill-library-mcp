# DashScope Wan 文生视频 (t2v) API notes

## Submit (Async)

Endpoint:

`POST https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`

Headers:
- `Authorization: Bearer $DASHSCOPE_API_KEY`
- `Content-Type: application/json`
- `X-DashScope-Async: enable`

Body (example):
```json
{
  "model": "wan2.6-t2v",
  "input": {
    "prompt": "4秒赛博朋克雨夜城市镜头...",
    "audio_url": "https://...mp3" 
  },
  "parameters": {
    "size": "1280*720",
    "prompt_extend": true,
    "duration": 4,
    "shot_type": "single"
  }
}
```

Response (example):
```json
{
  "request_id": "...",
  "output": {
    "task_id": "...",
    "task_status": "PENDING"
  }
}
```

## Poll / Get Result

Endpoint:

`GET https://dashscope.aliyuncs.com/api/v1/tasks/<task_id>`

Response on success (example):
- `output.task_status = SUCCEEDED`
- `output.video_url` contains the signed mp4 URL.

## Common issues

- TLS errors (`unexpected eof while reading`): often proxy/TLS interception. Try temporarily unsetting proxy env vars or using `-k` for debugging.
- `InvalidApiKey`: key lacks permissions for video service, or wrong key is being used.
