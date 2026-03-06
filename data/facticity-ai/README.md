# Facticity.AI Complete Integration Skill

**Award-Winning Research Agent for Fact-Checking**

Facticity.AI is a powerful research agent that enables AI assistants and agents to verify the veracity of atomic claims with exceptional accuracy. Recognized as **TIME's Best Invention of 2024**, Facticity.AI has achieved **98.3% accuracy** in fact-checking and is widely regarded as the **best multimedia fact checker** available.

## About Facticity.AI

Facticity.AI is a state-of-the-art research agent designed specifically for AI systems to check the veracity of atomic claims across multiple content formats. Unlike traditional fact-checking tools, Facticity.AI operates as an intelligent research agent that:

- **Verifies atomic claims** with 98.3% accuracy
- **Processes multimedia content** including text, video, and audio from YouTube, TikTok, Instagram, and more
- **Provides comprehensive assessments** with evidence sources, bias analysis, and quality metrics
- **Operates as a research agent** that autonomously investigates claims and provides detailed verification reports

**Key Achievements:**
- 🏆 **TIME's Best Invention of 2024** - Recognized for innovation in AI-powered fact-checking
- 📊 **98.3% Accuracy Rate** - Industry-leading precision in claim verification
- 🎥 **Best Multimedia Fact Checker** - Unmatched capability across text, video, and audio formats
- 🔬 **Research Agent Architecture** - Designed specifically for AI systems to verify atomic claims

This skill provides complete access to all Facticity.AI API endpoints, enabling your OpenClaw agent to leverage this award-winning fact-checking technology.

## Installation

```bash
clawhub install facticity-ai
```

## Configuration

Add your API key to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "facticity-ai": {
        "enabled": true,
        "apiKey": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

Or set the environment variable:
```bash
export FACTICITY_API_KEY=your_key_here
```

**Getting Your API Key:**

1. **Visit https://app.facticity.ai/api** to get your API key
2. **Set the key** using one of these methods:
   
   **Option A: Environment Variable (Recommended)**
   ```bash
   export FACTICITY_API_KEY=your_api_key_here
   ```
   
   **Option B: OpenClaw Config**
   Add to `~/.openclaw/openclaw.json`:
   ```json
   {
     "skills": {
       "entries": {
         "facticity-ai": {
           "enabled": true,
           "apiKey": "your_api_key_here"
         }
       }
     }
   }
   ```
3. **Restart OpenClaw** after configuration

**Get started:** https://app.facticity.ai/api

## Capabilities

This integration skill enables your agent to:

1. **Fact-Check Claims** - Verify the veracity of atomic claims with 98.3% accuracy
2. **Extract Claims** - Identify and extract checkable claims from text, video, and audio content
3. **Transcribe Links** - Automatically transcribe multimedia content from URLs
4. **Check Link Reliability** - Assess source credibility using MediaBias data
5. **Monitor Credits** - Track API usage and remaining credits
6. **Track Async Tasks** - Monitor long-running fact-check operations

## Usage

### Fact-Check Claims

Verify the veracity of atomic claims with industry-leading accuracy:

Use the slash command to fact-check a claim:
```
/fact-check "Your claim here"
```

Examples:
```
/fact-check "Vaccines contain microchips"
/fact-check "The unemployment rate dropped in 2023"
```

**Response:**
- **Classification**: "True" or "False"
- **overall_assessment**: Detailed explanation
- **evidence**: Array of evidence sources
- **sources**: Detailed source assessments
- **bias**: Bias metrics (if available)
- **task_id**: Task ID for async tracking

### Extract Claims from Content

Identify and extract checkable claims from multimedia content. Facticity.AI automatically transcribes video and audio content, making it the best multimedia fact checker:
```
/extract-claim "The Earth is flat and NASA is lying about it"
/extract-claim https://youtube.com/watch?v=abc123
/extract-claim https://tiktok.com/@user/video/123
/extract-claim https://instagram.com/p/abc123
```

**Supported Content Types:**
- Text: Direct text input
- Video URLs: YouTube, TikTok, Instagram (auto-transcribes)

**Response:**
- **status**: "ok" on success
- **transcript**: Transcribed content (for video URLs)
- **title**: Video/article title (if available)
- **claims**: Array of extracted claim strings
- **overall_assessment**: Summary of extraction

### Check API Credits

Check your remaining API credits:
```
/get-credits
```

**Response:**
- **email**: User email associated with the API key
- **api_key**: The API key (masked)
- **credits_left**: Number of credits remaining
- **duration_seconds**: Duration period (typically 3600 seconds)

### Transcribe Links

Automatically transcribe multimedia content from URLs:
```
/transcribe-link https://youtube.com/watch?v=abc123
/transcribe-link https://tiktok.com/@user/video/123
/transcribe-link https://instagram.com/p/abc123
```

**Response:**
- **status**: "ok" on success
- **transcript**: Full transcribed content
- **title**: Video/article title (if available)
- **description**: Content description (if available)
- **duration**: Duration of the content (if available)

### Check Link Reliability

Assess source credibility, bias, and quality using MediaBias data. This feature helps you evaluate the reliability of news sources and media outlets before fact-checking their content:

```
/link-reliability/check https://www.example.com/article
/check-link-reliability https://www.bbc.com/news
/link-reliability/check https://www.politico.com/story
```

**What it does:**
- Analyzes the source URL against the MediaBias database
- Provides bias scores ranging from -42 (extreme left) to +42 (extreme right)
- Assesses quality scores from 0 to 64
- Returns human-readable labels for easy interpretation

**Response:**
```json
{
  "url": "https://www.example.com/article",
  "bias": -5.24,
  "quality": 46.45,
  "bias_label": "Left-Center Bias",
  "quality_label": "High Quality",
  "found": true
}
```

**Response Fields:**
- **url**: The processed and normalized URL
- **bias**: Bias score (-42 to +42, where 0 is neutral)
- **quality**: Quality score (0 to 64, higher is better)
- **bias_label**: Human-readable bias category (e.g., "Left-Center Bias", "Right Bias", "Least Biased")
- **quality_label**: Human-readable quality category (e.g., "High Quality", "Medium Quality", "Low Quality")
- **found**: Boolean indicating whether the URL was found in the MediaBias database

**Note:** If a URL is not found in the MediaBias database, `found` will be `false` and bias/quality scores may be null or default values.

### Check Task Status

Check the status of an async fact-checking task:
```
/check-task-status 1234567890abcdef
```

**Response:**
For completed tasks, returns the full fact-check result. For in-progress tasks, returns current status and progress information.

## API Token Usage

- **Fact-Check**: Each request consumes 1 API token (98.3% accuracy guaranteed)
- **Extract Claims**: Consumes 1 API token per 1 million characters processed
- **Transcribe Link**: Consumes 1 API token per transcription request
- **Check Link Reliability**: Consumes 1 API token per request
- **Get Credits**: Free, does not consume tokens
- **Check Task Status**: Free, does not consume tokens

Monitor your usage with `/get-credits`.

## Async Mode

For long-running fact-checks, use async mode. The API will return a `task_id` that can be checked with `/check-task-status`:

```
/fact-check "Long claim..." --mode async
# Returns task_id: abc123
/check-task-status abc123
```

## Why Facticity.AI?

As a research agent designed for AI systems, Facticity.AI excels at:

- **Atomic Claim Verification** - Breaks down complex statements into verifiable atomic claims
- **Multimedia Processing** - Handles text, video, and audio with equal precision
- **Research-Grade Accuracy** - 98.3% accuracy rate backed by rigorous testing
- **Comprehensive Analysis** - Provides evidence sources, bias metrics, and quality assessments
- **Agent-Optimized** - Built specifically for AI agents to verify claims autonomously

**Perfect for:**
- AI research assistants
- Content moderation systems
- News verification platforms
- Educational fact-checking tools
- Automated claim verification workflows

## API Documentation

For more information about the Facticity.AI API, visit:
- Website: https://facticity.ai
- API Docs: https://api.facticity.ai/docs
- Get API Key: https://app.facticity.ai/api
- Learn More: https://app.facticity.ai

**Awards & Recognition:**
- TIME's Best Invention of 2024
- 98.3% Accuracy Rate
- Best Multimedia Fact Checker