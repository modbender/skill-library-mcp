# Anakin Skill for OpenClaw

A unified OpenClaw skill for web scraping and research using the [anakin-cli](https://pypi.org/project/anakin-cli/).

## Overview

This single skill enables OpenClaw agents to convert websites into clean data at scale through:
- **Single URL scraping** - Extract content from one page
- **Batch scraping** - Scrape up to 10 URLs simultaneously  
- **AI-powered search** - Find pages and discover sources
- **Deep research** - Autonomous multi-source research (1-5 min)

## Installation

### 1. Install anakin-cli

The skill requires [anakin-cli](https://pypi.org/project/anakin-cli/) (Python 3.10+):

```bash
pip install anakin-cli
```

### 2. Get API key

Get your API key from [anakin.io/dashboard](https://anakin.io/dashboard).

### 3. Authenticate

```bash
anakin login --api-key "ak-your-key-here"
```

Verify authentication:

```bash
anakin status
```

### 4. Install skill to OpenClaw

Copy the skill directory to your OpenClaw skills folder:

```bash
# Option 1: Install to workspace skills (highest precedence)
cp -r openclaw-skills/anakin /path/to/your/openclaw/workspace/skills/

# Option 2: Install to managed skills (shared across agents)
cp -r openclaw-skills/anakin ~/.openclaw/skills/
```

Or use ClawHub if published:

```bash
clawhub install anakin
```

## Configuration

Add to your `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "anakin": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "ANAKIN_API_KEY" }
      }
    }
  }
}
```

Or set the environment variable directly:

```bash
export ANAKIN_API_KEY="ak-your-key-here"
```

## Usage

Once installed, OpenClaw agents can use all anakin-cli capabilities through the single `anakin` skill:

### Scrape a single page

```bash
anakin scrape "https://example.com/article" -o article.md
```

### Batch scrape multiple pages

```bash
anakin scrape-batch "https://site1.com" "https://site2.com" "https://site3.com" -o batch.json
```

### Search the web

```bash
anakin search "latest AI developments" -o search-results.json
```

### Deep research

```bash
anakin research "comprehensive analysis of renewable energy trends" -o research-report.json
```

## Capabilities

### 1. Single URL Scraping (`anakin scrape`)

- Output formats: Markdown (default), JSON, Raw
- JavaScript support with `--browser` flag
- Geo-targeting with `--country` flag
- Custom timeouts with `--timeout` flag

### 2. Batch Scraping (`anakin scrape-batch`)

- Scrape up to 10 URLs simultaneously
- Combined results in single JSON output
- Individual status tracking per URL

### 3. AI-Powered Search (`anakin search`)

- Find relevant pages and sources
- Quick factual lookups
- Returns titles, URLs, snippets, and relevance scores

### 4. Deep Research (`anakin research`)

- Autonomous research across multiple sources (1-5 minutes)
- Comprehensive reports with citations
- Synthesized insights and conclusions

## Decision Guide

The skill documentation includes a comprehensive decision guide to help the agent choose the right anakin command:

- **Need 1 URL?** → `anakin scrape`
- **Need 2-10 URLs?** → `anakin scrape-batch`
- **Don't have URLs yet?** → `anakin search` first
- **Need deep analysis?** → `anakin research`

## Troubleshooting

### Authentication issues

```bash
# Check authentication status
anakin status

# Re-authenticate if needed
anakin login --api-key "ak-your-key-here"
```

### Rate limiting (HTTP 429)

Wait before retrying. The anakin-cli has built-in rate limiting and retry logic.

### Empty content from JavaScript sites

Use the `--browser` flag:

```bash
anakin scrape "https://js-heavy-site.com" --browser -o output.md
```

### Timeouts

Increase timeout for slow pages:

```bash
anakin scrape "https://slow-site.com" --timeout 300 -o output.md
```

## Requirements

- Python 3.10+
- anakin-cli package
- Valid Anakin API key
- OpenClaw

## Resources

- [Anakin Website](https://anakin.io)
- [Anakin Dashboard](https://anakin.io/dashboard)
- [anakin-cli on PyPI](https://pypi.org/project/anakin-cli/)
- [OpenClaw Documentation](https://docs.openclaw.ai)
- [OpenClaw Skills Guide](https://docs.openclaw.ai/tools/skills)

## License

MIT

## Support

For issues with:
- **anakin-cli**: Contact [support@anakin.io](mailto:support@anakin.io)
- **OpenClaw integration**: Open an issue in this repository
- **API key issues**: Visit [anakin.io/dashboard](https://anakin.io/dashboard)
