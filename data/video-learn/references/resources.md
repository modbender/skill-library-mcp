# 视频理解参考资料

## YouTube API

### 获取视频信息
```bash
curl "https://www.googleapis.com/youtube/v3/videos?id=VIDEO_ID&key=API_KEY&part=snippet,contentDetails"
```

### 响应字段
- snippet.title - 标题
- snippet.description - 描述
- contentDetails.duration - 时长 (ISO 8601)
- statistics.viewCount - 播放量
- statistics.likeCount - 点赞数

## Bilibili API

### 获取视频信息
```bash
# bv号转av号
curl "https://api.bilibili.com/x/web-interface/view?bvid=BV1xxx"

# av号获取
curl "https://api.bilibili.com/x/web-interface/view?aid=170001"
```

### 响应字段
- title - 标题
- desc - 描述
- duration - 时长（秒）
- owner.name - UP主
- stat.view - 播放量
- stat.like - 点赞数
- pages - 视频分P

## 视频下载工具

### yt-dlp (推荐)
```bash
# 安装
pip install yt-dlp

# 下载视频
yt-dlp "URL"

# 仅提取音频
yt-dlp -x "URL"

# 提取字幕
yt-dlp --write-subs "URL"
```

## 时长转换

ISO 8601 转秒数：
```python
import re
from datetime import timedelta

def parse_duration(iso_duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, iso_duration)
    if match:
        h, m, s = match.groups()
        return int(h or 0) * 3600 + int(m or 0) * 60 + int(s or 0)
    return 0
```
