# Hacker News API Reference

Official API documentation: https://github.com/HackerNews/API

## Base URL
```
https://hacker-news.firebaseio.com/v0
```

## Endpoints

### Get Top Stories
```
GET /topstories.json
```
Returns: Array of ~500 story IDs (integers), ordered by rank

### Get Story Details
```
GET /item/{id}.json
```
Returns: Story object

Example response:
```json
{
  "by": "dhouston",
  "descendants": 71,
  "id": 8863,
  "kids": [9224, 8917, 8952, 8884, 8887, 8943, 8870, ...],
  "score": 104,
  "time": 1175714200,
  "title": "My YC app: Dropbox - Throw away your USB drive",
  "type": "story",
  "url": "http://www.getdropbox.com/u/2/screencast.html"
}
```

### Get New Stories
```
GET /newstories.json
```

### Get Ask Stories
```
GET /askstories.json
```

### Get Show Stories
```
GET /showstories.json
```

### Get Job Stories
```
GET /jobstories.json
```

## Data Types

### Item (Story/Comment/Job/Poll)
| Field | Type | Description |
|-------|------|-------------|
| id | int | Unique ID |
| type | string | "story", "comment", "job", "poll", "pollopt" |
| by | string | Username of submitter |
| time | int | Unix timestamp |
| title | string | Title (for stories/jobs) |
| text | string | Text content |
| url | string | URL (for stories) |
| score | int | Vote count |
| descendants | int | Comment count |
| kids | [int] | Child comment IDs |

## Rate Limiting

Officially: "There is no rate limit, but please be respectful."

Best practices:
- Cache results for at least 1-4 hours
- Don't request more data than needed
- Use gzip compression (add `Accept-Encoding: gzip` header)

## Python Example

```python
import requests

def get_top_stories(limit=10):
    """获取Top Stories"""
    response = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json"
    )
    story_ids = response.json()[:limit]
    return story_ids

def get_story(story_id):
    """获取单个Story详情"""
    response = requests.get(
        f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    )
    return response.json()

# 使用示例
story_ids = get_top_stories(5)
for sid in story_ids:
    story = get_story(sid)
    print(f"{story['title']} - {story.get('url', 'No URL')}")
```
