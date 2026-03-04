# 抖音 API 参考文档

## 概述

本文档提供抖音开放平台 API 的调用方法和示例代码。

## 认证方式

### Cookie 认证

抖音使用 session cookie 进行认证。获取方法：

1. 在浏览器中登录抖音网页版 (https://www.douyin.com)
2. 打开开发者工具 (F12)
3. 进入 Network 标签
4. 刷新页面，找到任意请求
5. 复制 Request Headers 中的 `cookie` 字段

### Cookie 格式

```
sessionid=xxx; sessionid_ss=xxx; sid_guard=xxx; uid_tt=xxx; ...
```

## API 端点

### 获取评论列表

```
GET https://www.douyin.com/aweme/v1/web/comment/list/
```

**参数：**
- `aweme_id`: 视频 ID
- `cursor`: 分页游标
- `count`: 每页数量 (默认 20)

**响应示例：**
```json
{
  "status_code": 0,
  "comments": [
    {
      "cid": "7123456789",
      "text": "怎么买？",
      "user": {
        "uid": "MS4wLjABAAAA...",
        "nickname": "用户昵称"
      },
      "create_time": 1704067200
    }
  ],
  "cursor": 20,
  "has_more": 1
}
```

### 回复评论

```
POST https://www.douyin.com/aweme/v1/web/comment/publish/
```

**参数：**
- `aweme_id`: 视频 ID
- `comment_id`: 要回复的评论 ID
- `text`: 回复内容
- `tags`: 标签 (可选)

**响应示例：**
```json
{
  "status_code": 0,
  "comment": {
    "cid": "7123456790",
    "text": "亲，已私信您购买链接啦~ 😊",
    "create_time": 1704067260
  }
}
```

### 发送私信

```
POST https://www.douyin.com/aweme/v1/web/im/send/msg/
```

**参数：**
- `to_user_id`: 接收用户 ID
- `content`: 消息内容
- `msg_type`: 消息类型 (1=文本)

**响应示例：**
```json
{
  "status_code": 0,
  "msg_id": "7123456791"
}
```

## Python 调用示例

### 基础请求类

```python
import requests
import json

class DouyinAPI:
    def __init__(self, cookie):
        self.session = requests.Session()
        self.session.headers.update({
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.douyin.com/'
        })
        self.base_url = 'https://www.douyin.com/aweme/v1/web'
    
    def get_comments(self, video_id, cursor=0, count=20):
        """获取视频评论"""
        url = f'{self.base_url}/comment/list/'
        params = {
            'aweme_id': video_id,
            'cursor': cursor,
            'count': count
        }
        response = self.session.get(url, params=params)
        return response.json()
    
    def reply_comment(self, video_id, comment_id, text):
        """回复评论"""
        url = f'{self.base_url}/comment/publish/'
        data = {
            'aweme_id': video_id,
            'comment_id': comment_id,
            'text': text
        }
        response = self.session.post(url, data=data)
        return response.json()
    
    def send_message(self, user_id, content):
        """发送私信"""
        url = f'{self.base_url}/im/send/msg/'
        data = {
            'to_user_id': user_id,
            'content': content,
            'msg_type': 1
        }
        response = self.session.post(url, data=data)
        return response.json()
```

### 使用示例

```python
# 初始化 API
api = DouyinAPI(cookie='your_cookie_here')

# 获取评论
comments = api.get_comments(video_id='7123456789')

# 回复评论
result = api.reply_comment(
    video_id='7123456789',
    comment_id='7123456790',
    text='亲，已私信您购买链接啦~ 😊'
)

# 发送私信
result = api.send_message(
    user_id='MS4wLjABAAAA...',
    content='您好！这是您需要的信息...'
)
```

## 注意事项

### 频率限制

- 评论回复：每分钟不超过 10 条
- 私信发送：每分钟不超过 5 条
- 评论获取：每分钟不超过 30 次

### 内容限制

- 回复内容不超过 200 字
- 避免敏感词汇
- 不要包含外部链接（容易被屏蔽）

### 风控策略

1. **新号限制**: 新注册账号功能受限
2. **行为模式**: 避免固定时间间隔操作
3. **内容重复**: 避免完全相同的回复内容
4. **账号异常**: 大量操作可能触发验证

## 常见问题

### Q: Cookie 失效怎么办？
A: Cookie 有效期约 7-30 天，失效后重新获取即可。

### Q: 提示"操作频繁"？
A: 降低操作频率，增加延迟时间。

### Q: 私信发送失败？
A: 检查是否被对方拉黑，或对方设置了隐私权限。

### Q: 如何获取视频 ID？
A: 视频 URL 中的数字部分，如：
   https://www.douyin.com/video/7123456789
   视频 ID 为：7123456789

## 相关资源

- 抖音开放平台：https://open.douyin.com/
- API 文档：https://open.douyin.com/platform/doc
- 开发者社区：https://developers.douyin.com/
