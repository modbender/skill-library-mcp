# 抖音关键词搜索抓取技能

通过浏览器自动化抓取抖音搜索结果页面的文章数据。

## 文件说明

| 文件 | 说明 |
|------|------|
| `douyin_keyword_search.py` | Python 主脚本 |
| `douyin_keyword_search.sh` | Shell 包装脚本 |
| `requirements.txt` | Python 依赖列表 |

## 安装依赖

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## 使用方法

### 命令行调用

```bash
# 基本使用
python douyin_keyword_search.py --keyword "关键词"

# 指定输出格式和数量
python douyin_keyword_search.py -k "科技新闻" -o json -l 30

# 保存到文件
python douyin_keyword_search.py -k "美食" -o csv -f results.csv

# 无头模式（后台运行）
python douyin_keyword_search.py -k "新闻" --headless
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keyword, -k` | 搜索关键词（必填） | - |
| `--output, -o` | 输出格式：json/csv/txt | json |
| `--limit, -l` | 抓取数量限制 | 20 |
| `--headless` | 无头模式，不显示浏览器窗口 | false |
| `--output-file, -f` | 输出文件路径 | 控制台输出 |

### Claude Code 技能调用

在 Claude Code 中配置后可使用：

```bash
/skill douyin-keyword-search --keyword "人工智能"
```

## 输出示例

```json
[
  {
    "title": "视频标题",
    "author": "作者名称",
    "url": "https://www.douyin.com/video/xxx",
    "stats": ["10万点赞", "5000评论"],
    "keyword": "搜索关键词",
    "crawl_time": "2024-01-01T12:00:00"
  }
]
```

## 注意事项

1. 首次使用需要安装 Playwright 和 Chromium 浏览器
2. 抖音需要登录才能查看完整搜索结果，建议首次运行时不使用 `--headless` 参数
3. 请遵守抖音的使用条款和 robots.txt 规则
4. 建议控制抓取频率，避免对服务器造成压力

## 许可证

MIT License