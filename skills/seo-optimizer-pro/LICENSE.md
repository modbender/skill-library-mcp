# SEO Optimizer Pro - License Agreement

**Version:** 1.0.6
**Copyright © 2026 UnisAI. All Rights Reserved.**

## License Type
Free-to-Use Software with Source Code Included

## Grant of License

UnisAI grants you a free, non-exclusive, non-transferable license to use the SEO Optimizer Pro skill without any subscription or payment required. Source code is included for transparency and security review.

## Usage Rights

### ✅ You ARE Permitted To:
- Use the skill for free, unlimited times
- Analyze unlimited content
- Export and use optimization reports
- Use for commercial purposes
- Use for personal projects
- Store analysis results locally
- **Read and review the source code** for security auditing
- **Modify the source code for personal use only** (not for redistribution)
- Audit the code for security vulnerabilities

### ❌ You ARE NOT Permitted To:
- Redistribute, resell, or relicense the skill outside ClawhHub registry
- Redistribute modified versions of the skill
- Remove or alter copyright notices
- Use as a competitive product
- Sublicense to third parties
- Claim the work as your own

## Free Usage Terms

- **No cost** - Completely free to use
- **Unlimited analyses** - Use as many times as needed
- **Commercial use allowed** - Use for business purposes
- **All features** - Full access to all functionality

## How It Works (Data Flow)

This skill runs **locally** as a Python module. It does NOT connect to any UnisAI backend or hosted service. Here is exactly what happens when you run an analysis:

1. Your content is parsed locally (readability, keywords, structure)
2. Your content excerpt is sent to the AI provider YOU chose (Anthropic, OpenAI, Google, Mistral, or OpenRouter)
3. The AI provider returns optimization suggestions
4. Results are formatted and returned to you locally

**No data is sent to UnisAI servers.** Your content only goes to the AI provider you selected, via their official SDK.

## Intellectual Property

All content, code, algorithms, databases, and materials in the SEO Optimizer Pro skill are the exclusive property of UnisAI. This includes:
- The readability analysis algorithm
- Keyword analysis methodology
- AEO recommendation engine
- Multi-provider AI integration logic
- All generated analyses and reports

You do not own the skill or any part of it. You are granted a license to use it.

## Watermark & Tracking

The skill includes the watermark: `PROPRIETARY_SKILL_SEO_OPTIMIZER_2026`

This watermark identifies the skill's proprietary nature and ensures authentic version tracking.

## API Key Security

You are responsible for:
- Keeping your API keys confidential
- Not sharing keys with unauthorized parties
- Using environment variables (never hardcode)
- Rotating keys if compromised

UnisAI is not liable for unauthorized access via compromised keys.

## Data & Privacy

### What This Skill Stores
- **Nothing** - All analyses run in-memory locally and are discarded after use

### Where Your Content Goes
- **Only to the AI provider you selected** (Anthropic, OpenAI, Google, OpenRouter, or Mistral)
- Subject to that provider's own data handling policies
- No data is sent to UnisAI

### ⚠️ IMPORTANT: Third-Party Data Sharing
**Your content IS sent to third-party AI providers.** Each provider has different data retention policies:
- **Anthropic Privacy Policy**: https://www.anthropic.com/legal/privacy
- **OpenAI Privacy Policy**: https://openai.com/policies/privacy-policy
- **Google Gemini API Terms**: https://ai.google.dev/gemini-api/terms
- **OpenRouter Privacy Policy**: https://openrouter.ai/privacy
- **Mistral AI Terms**: https://mistral.ai/terms/

**RECOMMENDATION**: Review the privacy policy of your chosen provider before sending sensitive content. Test with non-sensitive sample content first.

### Data Retention
- 0 days - No content data retained by this skill locally
- Your AI provider may retain data per their own terms (see links above)

## Disclaimer of Warranties

THE SKILL IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO:
- Merchantability or fitness for a particular purpose
- Non-infringement of third-party rights
- Accuracy of SEO or ranking recommendations
- Guaranteed improvement in search rankings
- Uninterrupted or error-free operation

## Limitation of Liability

IN NO EVENT SHALL UNISAI BE LIABLE FOR:
- Indirect, incidental, consequential damages
- Lost revenue or profits
- Failed rankings or missed opportunities
- Data loss or corruption
- Third-party claims

## Acceptable Use Policy

You agree NOT to:
- Use the skill for illegal purposes
- Exploit bugs or security vulnerabilities
- Scrape or systematically copy functionality
- Use for spamming or manipulating search results

## Changes to Terms

UnisAI may modify these terms at any time. Continued use of the skill after changes constitutes acceptance of new terms. Material changes will result in 30 days notice.

## Termination

### Termination by UnisAI
UnisAI may terminate your license if:
- You violate these terms
- You engage in prohibited activities

Termination is immediate upon violation.

### Termination by You
You may stop using the skill at any time. No action required.

## Cost & Payment

This skill is completely **free**. There are no payments, subscriptions, or refunds because there are no charges.

You provide your own API key for your chosen AI provider (Anthropic, OpenAI, Google, OpenRouter, or Mistral). You are billed directly by that provider for API usage at their standard rates.

## Third-Party Components

This skill uses the following provider SDKs (only the one for your chosen model is loaded at runtime):
- **Anthropic SDK** (`anthropic`) - For Claude models, subject to Anthropic's terms
- **OpenAI SDK** (`openai`) - For GPT and Llama (via OpenRouter) models, subject to OpenAI's terms
- **Google Generative AI SDK** (`google-generativeai`) - For Gemini models, subject to Google's terms
- **Mistral SDK** (`mistralai`) - For Mistral models, subject to Mistral's terms
- **Python Standard Library** - Licensed under PSF License

Using this skill requires acceptance of the relevant provider's terms.

## Governing Law

This agreement is governed by the laws of California, USA, without regard to conflict of law principles.

## Contact

For questions about this license:
- Email: support@unisai.vercel.app
- Website: https://unisai.vercel.app
- GitHub: https://github.com/vedantsingh60/seo-optimizer-pro

---

**Last Updated**: February 14, 2026
**License Version**: 1.0.6
**Skill Version**: 1.0.6
**Status**: Active

© 2026 UnisAI. All rights reserved.
