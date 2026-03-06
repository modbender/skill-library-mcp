# Bilibili API 参考指南

## 安装
```bash
pip install bilibili-api-python
```

## 质量代码 (qn参数)
| 代码 | 清晰度 |
|------|--------|
| 127 | 8K |
| 126 | 杜比视界 |
| 125 | 1080P+ |
| 120 | 1080P60 |
| 116 | 4K |
| 112 | 1080P |
| 80 | 1080P |
| 74 | 720P |
| 64 | 480P |
| 32 | 360P |

## 常用操作

### 获取视频信息
```python
from bilibili_api import video, sync
v = video.Video(bvid='BV1xx411c7m2')
info = sync(v.get_info())
```

### 下载视频
```python
sync(v.download(output='./video.mp4'))
```

### 获取下载链接
```python
url_info = v.get_download_url(qn=125)  # 1080P+
```

### 获取字幕列表
```python
subtitles = sync(v.get_subtitle())
```

### 下载字幕
```python
sub_info = sync(v.get_subtitle(subtitle_id))
```

### 获取封面
```python
cover_url = v.get_cover()
```

## Cookie 设置
需要登录的操作需要设置 SESSDATA:
```bash
export BILIBILI_SESSDATA='your_cookie_value'
```

或在代码中:
```python
import os
os.environ['BILIBILI_SESSDATA'] = 'your_cookie_value'
```

## 错误处理
- 403: Cookie无效或过期
- -404: 视频不存在
- -403: 需要登录
