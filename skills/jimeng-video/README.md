# 即梦视频生成 Skill - 快速参考

## 安装

已自动安装，无需额外操作。

## 使用方法

### 命令行方式

```bash
# 生成视频
~/.openclaw/skills/jimeng-video/jimeng-video generate \
  -p "你的提示词" \
  -o 输出文件.mp4

# 查询任务状态
~/.openclaw/skills/jimeng-video/jimeng-video status \
  -t 任务ID

# 查看可用模型
~/.openclaw/skills/jimeng-video/jimeng-video list-models
```

### Agent调用方式

Agent可以直接调用即梦视频生成功能：

```bash
# 生成视频
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "model": "doubao-seedance-1-0-lite-t2v-250428",
    "content": [
      {
        "type": "text",
        "text": "提示词内容"
      }
    ]
  }'

# 查询结果
curl -X GET "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}" \
  -H "Authorization: Bearer ${API_KEY}"
```

## 提示词示例

```
一匹马高高跃起，四个字从左到右书写，水墨风格，文字内容是马年大吉

夕阳下的海滩，金色的阳光洒在波浪上，电影级画质

赛博朋克风格的城市夜景，霓虹灯闪烁，未来感十足
```

## API凭证位置

`~/.openclaw/.credentials/volcengine-dreamina.env`

## 详细文档

查看完整文档：`~/.openclaw/skills/jimeng-video/SKILL.md`
