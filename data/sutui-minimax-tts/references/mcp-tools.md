# MCP 工具参考

本 skill 使用 `user-速推AI` MCP 服务器提供的语音合成工具。

## list_voices

获取所有可用音色列表。

### 调用方式

```json
{
  "server": "user-速推AI",
  "toolName": "list_voices",
  "arguments": {}
}
```

### 返回示例

```json
{
  "voices": [
    {
      "voice_id": "male-qn-qingse",
      "name": "青涩青年音色",
      "gender": "male"
    },
    {
      "voice_id": "female-shaonv",
      "name": "少女音色",
      "gender": "female"
    }
  ]
}
```

## text_to_audio

将文本转换为语音。

### 调用方式

```json
{
  "server": "user-速推AI",
  "toolName": "text_to_audio",
  "arguments": {
    "text": "要转换的文本",
    "voice_id": "音色ID",
    "model": "speech-2.8-hd",
    "output_format": "url",
    "language_boost": "Chinese"
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|-----|
| text | string | 是 | 要转换的文本内容 |
| voice_id | string | 是 | 音色 ID |
| model | string | 否 | 模型版本，推荐 `speech-2.8-hd` |
| output_format | string | 否 | 输出格式，`url` 返回音频链接 |
| language_boost | string | 否 | 语言增强，中文使用 `Chinese` |

### 返回示例

```json
{
  "audio_url": "https://example.com/audio/xxx.mp3",
  "duration": 3.5
}
```

## 计费说明

- 每 1000 字符消耗 1 积分
- 每段对话独立计费
- 语气词标签 `(laughs)` 等不计入字符数

## 注意事项

1. **文本长度限制**：单次请求建议不超过 500 字符
2. **音频格式**：默认返回 MP3 格式
3. **并发限制**：建议串行调用，避免并发过高
4. **超时处理**：长文本合成可能需要较长时间，注意设置合理的超时
