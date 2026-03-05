# 🐦 Twitter/X Reader

**Professional-grade tweet extraction and analysis for OpenClaw**

Extract complete tweet data from X/Twitter URLs including content, engagement stats, media, and more. Built for reliability, security, and comprehensive data coverage.

## ✨ Features

- 🔗 **Universal URL Support** - Works with x.com, twitter.com, and mobile URLs
- 📊 **Complete Data Extraction** - Text, author, timestamps, engagement stats, media
- 🎯 **Multi-Source Reliability** - FxTwitter API primary + Nitter fallback
- 🔒 **Security First** - No data collection, fully auditable, open source
- ⚡ **Fast & Reliable** - Optimized for speed with robust error handling
- 🧵 **Thread Aware** - Handles quote tweets and conversation context

## 🚀 Quick Start

Simply share any tweet URL with your OpenClaw agent:

```
"What does this tweet say? https://x.com/elonmusk/status/1234567890"
```

Your agent will automatically extract and present:
- Tweet content with proper formatting
- Author name and handle
- Post timestamp and engagement metrics  
- Any attached media (photos/videos)
- Quoted tweets with full context

## 📋 What Gets Extracted

### Core Data
- **Tweet Text** - Full content with formatting preserved
- **Author Info** - Display name and @handle
- **Timestamps** - Human-readable and original format
- **Source URL** - Canonical link to the tweet

### Engagement Metrics
- **Likes** - Heart reactions count
- **Retweets** - Share count including quote tweets
- **Replies** - Comment count
- **Quotes** - Quote tweet count

### Media Content
- **Photos** - Direct links to full-resolution images
- **Videos** - MP4 URLs when available
- **GIFs** - Animated content links

### Advanced Features
- **Quote Tweets** - Embedded tweet content and author
- **Thread Context** - Related tweet identification
- **Link Preservation** - External URLs maintained in text

## 🔧 Technical Approach

### Primary: FxTwitter API
- **Fast & Reliable** - Sub-second response times
- **No Authentication** - Works without API keys or tokens
- **Complete Data** - Full metadata including engagement stats
- **Rate Limit Friendly** - Generous limits for personal use

### Fallback: Nitter Scraping (Best-Effort)
- **Multiple Instances** - Tries several public instances, though many are defunct
- **Privacy Focused** - No JavaScript or tracking
- **Basic Extraction** - Core tweet content when API fails
- **Automatic Switching** - Seamless fallback activation
- **⚠️ Reliability Note** - Most public Nitter instances have shut down since 2024. This fallback may not yield results.

## 🛡️ Security & Privacy

### Zero Data Collection
- **No Analytics** - Usage not tracked or reported
- **No Storage** - Data processed in memory only
- **No Telemetry** - No phone-home functionality
- **Local Processing** - All parsing done on your system

### Network Security
- **Approved Hosts Only** - Connections limited to FxTwitter and Nitter
- **Safe URL Handling** - Input validation and sanitization
- **Clear User Agent** - Identifies as OpenClaw TwitterReader
- **Minimal Headers** - No unnecessary data transmitted

### Open Source Transparency
- **Fully Auditable** - All code available for review
- **No Hidden Behavior** - Every network call documented
- **Readable Scripts** - Clear, commented shell scripts
- **Security Focused** - Designed to pass enterprise security reviews

## 📦 Dependencies

**System Requirements:**
- `curl` - HTTP client for API requests
- `jq` - JSON parsing and formatting
- `bash` - Shell script execution

**Optional Enhancements:**
- `gdate` (macOS) - Better timestamp formatting via Homebrew

All dependencies are standard system tools available on macOS, Linux, and Windows (WSL).

## 🎯 Use Cases

### Content Analysis
- **Research** - Extract tweets for academic studies
- **Journalism** - Quote tweets accurately with context
- **Documentation** - Archive important announcements
- **Fact Checking** - Verify tweet content and engagement

### Social Media Management
- **Monitoring** - Track mentions and replies
- **Engagement** - Analyze performance metrics
- **Content Creation** - Reference trending tweets
- **Community Management** - Respond to customer feedback

### Development & Automation
- **Bot Development** - Process tweet content programmatically  
- **Data Analysis** - Extract metrics for dashboards
- **Content Moderation** - Review reported tweets
- **API Integration** - Bridge to other social platforms

## 🔍 Error Handling

The skill gracefully handles common issues:

- **Invalid URLs** - Clear format guidance provided
- **Deleted Tweets** - Appropriate error messaging
- **Rate Limits** - Automatic fallback to alternative sources
- **Network Issues** - Automatic fallback to alternative sources
- **Protected Accounts** - Privacy-respecting error responses

## 🚦 Rate Limits & Fair Use

### FxTwitter API
- **Generous Limits** - Designed for personal/small business use
- **No Authentication** - No API key management required
- **Respectful Usage** - Built-in delays prevent abuse

### Nitter Instances
- **Multiple Sources** - Automatic instance rotation
- **Graceful Degradation** - Falls back when instances unavailable
- **Community Friendly** - Minimal load per instance

## 🛠️ Installation

This skill is designed for OpenClaw and installs automatically when downloaded from ClawHub. For manual installation:

1. Clone to your skills directory
2. Ensure scripts are executable (`chmod +x scripts/*.sh`)
3. Verify dependencies are available (`curl`, `jq`, `bash`)
4. Test with a sample tweet URL

## 📈 Performance

- **Response Time** - Typically 200-500ms via FxTwitter
- **Reliability** - High availability through fallback methods
- **Data Completeness** - Full metadata extraction
- **Memory Usage** - Minimal footprint, no persistent storage

## 🤝 Contributing

We welcome contributions to improve the Twitter Reader skill:

- **Bug Reports** - Document issues with specific URLs
- **Feature Requests** - Suggest new data extraction capabilities
- **Code Contributions** - Submit pull requests with tests
- **Documentation** - Improve examples and troubleshooting

## 📄 License

Open source under MIT License. Free for commercial and personal use.

## 🔗 Related Skills

Pairs well with:
- **Content Summarizer** - Analyze extracted tweet content
- **Media Downloader** - Save photos and videos locally
- **Translation Service** - Convert tweets to other languages
- **Sentiment Analysis** - Gauge tweet emotional tone

---

**Ready to extract tweet data like a pro?**  
Add this skill to your OpenClaw setup and never manually copy-paste tweet content again.