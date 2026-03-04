---
name: xiaohongshu-reply-assistant
description: >
  小红书智能回复助手 - 自动分析评论情感和意图，生成个性化回复建议。
  Use for: (1) Analyzing Xiaohongshu comment sentiment and intent, 
  (2) Generating personalized reply suggestions, 
  (3) Managing comment history and batch processing,
  (4) Monitoring notes for new comments.
  Supports both standalone offline analysis and API integration with real Xiaohongshu data.
triggers: xiaohongshu reply, rednote comments, 小红书回复, 评论监控, social media management
---

# 小红书智能回复助手 / Xiaohongshu Reply Assistant

Intelligent comment analysis and reply suggestion generator for Xiaohongshu (Little Red Book).

## Features

- 🧠 **Smart Analysis**: Automatically identify sentiment (positive/negative/neutral) and intent
- 💡 **Reply Suggestions**: Generate 3 personalized reply suggestions for each comment  
- 📊 **Batch Processing**: Process multiple comments at once
- 🔄 **History Management**: Avoid duplicate processing
- 🔌 **API Integration**: Optional connection to real Xiaohongshu API
- 📝 **Customizable Templates**: Configure your own reply templates

## Quick Start

### Option 1: Quick Analysis (No Setup Required)

```python
from reply_assistant import quick_analyze

result = quick_analyze(
    comment_text="这个地方真好看！想去打卡！",
    username="小美", 
    likes=15
)

print(f"Sentiment: {result['sentiment']}")  # 正面
print(f"Intent: {result['intent']}")        # 热门评论
print("Suggestions:")
for reply in result['reply_suggestions']:
    print(f"  - {reply}")
```

**Output:**
```
Sentiment: 正面
Intent: 热门评论
Suggestions:
  - @小美 谢谢您的喜欢！😊 欢迎常来互动~
  - @小美 感谢您的支持！会继续分享好内容的💪
  - @小美 太开心收到您的认可！有什么想看的可以告诉我~
```

### Option 2: Command Line Tool

```bash
# Analyze single comment
python3 scripts/xhs_reply_cli.py analyze \
  -t "门票多少钱？周末去人多吗？" \
  -u 旅行者

# Batch process from file
python3 scripts/xhs_reply_cli.py batch \
  -i comments.txt \
  -o report.txt

# View/edit configuration
python3 scripts/xhs_reply_cli.py config --show
```

### Option 3: Full Integration with Xiaohongshu API

Requires [xiaohongshu skill](https://github.com/xpzouying/xiaohongshu-mcp) or similar API access.

```python
import asyncio
from xhs_api_integration import XHSApiIntegration

async def monitor():
    integration = XHSApiIntegration(
        proxy=None,  # or "http://127.0.0.1:7890"
        web_session=None  # add your session cookie if needed
    )
    
    await integration.init_session()
    
    result = await integration.monitor_note(
        note_id="your_note_id",
        xsec_token="your_xsec_token",
        note_title="My Note"
    )
    
    report = integration.assistant.generate_report(result, "My Note")
    print(report)
    
    await integration.close()

asyncio.run(monitor())
```

## Installation

```bash
# Install dependencies
pip3 install aiohttp loguru pycryptodome getuseragent

# Or use the install script
chmod +x install.sh
./install.sh
```

## Comment Analysis Categories

### Sentiment Detection
- **Positive (正面)**: Contains words like 喜欢, 好看, 棒, 赞, 美, 不错
- **Negative (负面)**: Contains words like 不好, 差, 失望, 坑, 避雷
- **Neutral (中性)**: Other comments

### Intent Recognition
| Intent | Keywords | Example |
|--------|----------|---------|
| 价格咨询 | 多少钱, 价格, 贵不贵, 费用 | "门票多少钱？" |
| 位置咨询 | 哪里, 地址, 位置, 怎么去 | "具体地址在哪里？" |
| 提问咨询 | 吗, 怎么, 多少, 请问 | "周末去人多吗？" |
| 求资源 | 求, 想要, 链接, 怎么买 | "求购买链接！" |
| 热门评论 | Likes >= 10 | High engagement comments |
| 其他 | Default | Cannot categorize |

## Configuration

Config file location: `~/.xhs_reply_assistant/config.json`

```json
{
  "settings": {
    "max_suggestions": 3,
    "check_interval_minutes": 30
  },
  "reply_templates": {
    "正面反馈": [
      "@{user} 谢谢您的喜欢！😊 欢迎常来互动~",
      "@{user} 感谢您的支持！会继续分享好内容的💪"
    ],
    "负面反馈": [
      "@{user} 感谢您的反馈，我们会认真改进的！",
      "@{user} 抱歉给您带来不好的体验，能否私信详细说说？"
    ],
    "价格咨询": [
      "@{user} 关于价格问题，建议您查看置顶评论或私信了解详情哦~",
      "@{user} 价格会根据不同情况有所调整，欢迎私信咨询最新优惠！"
    ]
  }
}
```

**Template Variables:**
- `{user}`: Commenter's username
- `{answer}`: Custom answer text
- `{location}`: Location information
- `{transportation}`: Transportation instructions

## File Structure

```
Xiaohongshu Reply Assistant/
├── scripts/
│   ├── reply_assistant.py       # Core module (standalone)
│   ├── xhs_reply_cli.py         # CLI tool
│   └── xhs_api_integration.py   # API integration (optional)
├── examples/
│   ├── example_config.json      # Config example
│   └── example_usage.py         # Usage examples
├── install.sh                   # Installation script
└── README.md                    # Full documentation
```

## Data Storage

All data stored in `~/.xhs_reply_assistant/`:
- `config.json` - User configuration
- `history.json` - Processed comment IDs

## Use Cases

1. **Content Creators**: Efficiently manage fan comments and improve engagement quality
2. **Brand Operations**: Monitor brand-related content and respond to user feedback promptly
3. **MCN Agencies**: Batch manage comment replies across multiple accounts
4. **Data Analysis**: Collect user feedback to optimize content strategy

## Notes

- ⚠️ **Privacy**: Do not leak users' personal information
- ⚠️ **Rate Limiting**: Check every 30 minutes to avoid triggering anti-bot measures
- ⚠️ **Manual Review**: Auto-generated suggestions are for reference only; review before sending
- ⚠️ **Compliance**: Follow Xiaohongshu platform rules and relevant laws

## Requirements

- Python 3.8+
- Dependencies: `aiohttp`, `loguru`, `pycryptodome`, `getuseragent`
- Optional: xiaohongshu-mcp server for real API access

## License

MIT License

## Author

小流转 (Xiaoliuzhuan)
