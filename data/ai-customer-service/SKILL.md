---
name: AI Customer Service Knowledge Base Builder
description: Help SMBs quickly build AI-powered customer service systems. Input
  FAQ documents or website URLs to automatically generate a knowledge base and
  configure auto-reply capabilities.
---

# AI Customer Service Knowledge Base Builder

## Description
Help SMBs quickly build AI-powered customer service systems. Input FAQ documents or website URLs to automatically generate a knowledge base and configure auto-reply capabilities.

帮助中小企业快速搭建AI客服系统。输入FAQ文档或网站URL，自动生成知识库并配置自动回复功能。

## Use When
- Setting up customer service automation
- Building FAQ knowledge bases
- Configuring auto-reply systems
- Migrating customer service to AI

## Capabilities
- Extract FAQ from documents (PDF, TXT, MD, DOCX)
- Scrape FAQ from website URLs
- Generate structured knowledge base (JSON)
- Test Q&A matching
- Export to common formats (JSON, CSV, Markdown)

## Usage

### Basic Commands
```bash
# Extract from document
node kb-builder.js extract --file ./faq.pdf --output ./kb.json

# Extract from website
node kb-builder.js scrape --url https://example.com/faq --output ./kb.json

# Test knowledge base
node kb-builder.js test --kb ./kb.json --query "退货政策是什么？"

# Export to different formats
node kb-builder.js export --kb ./kb.json --format csv --output ./kb.csv
```

### Configuration
Create `config.json`:
```json
{
  "language": "zh-CN",
  "minConfidence": 0.7,
  "maxResults": 3,
  "fallbackMessage": "抱歉，我没有找到相关答案。请联系人工客服。"
}
```

## Examples

### Example 1: Build from PDF
```bash
node kb-builder.js extract --file ./company-faq.pdf --output ./kb.json
node kb-builder.js test --kb ./kb.json --query "如何退货？"
```

### Example 2: Build from Website
```bash
node kb-builder.js scrape --url https://shop.example.com/help --output ./kb.json
node kb-builder.js export --kb ./kb.json --format markdown --output ./faq.md
```

### Example 3: Interactive Mode
```bash
node kb-builder.js interactive --kb ./kb.json
# Then type questions to test responses
```

## Output Format
Knowledge base JSON structure:
```json
{
  "version": "1.0",
  "language": "zh-CN",
  "entries": [
    {
      "id": "q001",
      "question": "如何退货？",
      "answer": "您可以在收到商品后7天内申请退货...",
      "keywords": ["退货", "退款", "return"],
      "category": "售后服务"
    }
  ]
}
```

## Requirements
- Node.js 18+
- No external API keys needed for basic features
- Optional: OpenAI API key for enhanced matching

## Security
- All processing is local
- No data sent to external services (unless using OpenAI enhancement)
- Safe for sensitive business information

## Limitations
- PDF extraction requires readable text (not scanned images)
- Website scraping respects robots.txt
- Best results with structured FAQ pages

## Author
Created for OpenClaw by Claude

## License
MIT

## Tags
customer-service, ai, knowledge-base, faq, automation, chatbot, 客服, 知识库
