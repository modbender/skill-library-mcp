# Marketing Drafter

**Value Proposition**: AI-powered content generation for social posts, emails, ads, landing pages. One-shot prompts, batch generation, brand voice consistency.

## Problem Solved
- Writer's block on marketing copy
- Need for scalable content creation
- Maintaining brand voice across channels
- Time-consuming content generation
- A/B testing variations

## Use Cases
- Generate email campaign sequences
- Social media post drafts (Twitter, LinkedIn, Instagram)
- Ad copy (Google, Facebook, TikTok)
- Landing page headlines & CTAs
- Email subject lines (high CTR variants)
- Blog post outlines & drafts
- Product descriptions
- Sales pitch variations

## Quick Start

```bash
npm install marketing-drafter
# or
python -m pip install marketing-drafter
```

```javascript
const MarketingDrafter = require('marketing-drafter');

const drafter = new MarketingDrafter({
  model: 'gpt-4',
  apiKey: process.env.OPENAI_API_KEY
});

const emails = await drafter.generateEmails({
  topic: 'New SaaS product launch',
  audience: 'B2B founders',
  tone: 'professional-friendly',
  variants: 5
});

console.log(emails);
```

## Features
✅ Multi-channel content generation
✅ Brand voice consistency
✅ A/B testing variants
✅ Batch processing
✅ Template-based generation
✅ Image caption generation
✅ SEO-optimized copy
✅ Tone customization
✅ Plagiarism-free guarantee
✅ Performance scoring (predicted CTR)

## Installation

### Node.js
```bash
npm install marketing-drafter
```

### Python
```bash
pip install marketing-drafter
```

### Setup
```bash
export OPENAI_API_KEY=sk-...
# or set in .env file
```

## Configuration

```javascript
const drafter = new MarketingDrafter({
  model: 'gpt-4',  // or 'gpt-3.5-turbo', 'claude-3', 'gemini'
  apiKey: 'sk-...',
  temperature: 0.8,
  maxTokens: 2000,
  brandGuide: {
    voice: 'friendly',
    tone: 'professional',
    keywords: ['innovative', 'trustworthy'],
    neverUse: ['spam', 'clickbait']
  }
});
```

## Example Code

### Email Sequence Generation
```javascript
const drafter = new MarketingDrafter();

const sequence = await drafter.generateEmailSequence({
  productName: 'CloudVault Pro',
  audience: 'CTOs',
  emailCount: 5,
  goal: 'nurture to trial signup',
  existingCustomers: [
    { name: 'Acme Corp', industry: 'Tech' },
    { name: 'Global Inc', industry: 'Finance' }
  ]
});

// Returns: Array of 5 emails with subject, body, CTA
console.log(sequence[0].subject);  // "The $2.3M data disaster that could've been prevented"
console.log(sequence[0].body);     // Full email body
console.log(sequence[0].cta);      // "Start 14-day free trial"
```

### Social Media Posts (Multi-Channel)
```javascript
const posts = await drafter.generateSocialPosts({
  topic: 'AI automation',
  platforms: ['twitter', 'linkedin', 'tiktok'],
  tone: 'thought-leader',
  variants: 3,  // 3 options per platform
  includeHashtags: true,
  includeEmojis: true
});

// posts[0].platform === 'twitter'
// posts[0].content === "🧠 AI is killing the 9-to-5 and I'm here for it..."
```

### Ad Copy Generation
```javascript
const ads = await drafter.generateAds({
  product: 'Project management software',
  targetAudience: 'Busy founders',
  adFormat: 'facebook',  // facebook, google, instagram, linkedin
  budget: 'Budget-conscious',
  variants: 10,
  includeImages: true  // Returns image descriptions too
});

console.log(ads[0].headline);      // Max 60 chars for Facebook
console.log(ads[0].description);   // Max 90 chars
console.log(ads[0].cta);           // e.g., "Learn More"
console.log(ads[0].estimatedCTR);  // Predicted click-through rate
```

### Landing Page Copy
```javascript
const landingPage = await drafter.generateLandingPage({
  product: 'Email marketing platform',
  competitor: 'Mailchimp',
  differentiator: '10x cheaper',
  audienceSize: 'Small teams',
  seoKeywords: ['email automation', 'affordable email']
});

console.log(landingPage.headline);
console.log(landingPage.subheadline);
console.log(landingPage.benefits);  // Array of 3-5 benefits
console.log(landingPage.cta);
console.log(landingPage.socialProof);
```

### Subject Line A/B Testing
```javascript
const subjectLines = await drafter.generateSubjectLines({
  emailType: 'promotional',
  product: 'Fitness tracker',
  variants: 20,
  optimizeFor: 'open-rate'
});

// Returns 20 subject lines ranked by predicted performance
console.log(subjectLines[0].line);      // Highest predicted open rate
console.log(subjectLines[0].predictedOpenRate);  // e.g., 0.38 (38%)
```

## API Reference

### `generateEmails(options)`
Generate email copy.
- `topic` (string): Email topic
- `audience` (string): Target audience
- `tone` (string): 'professional', 'casual', 'urgent', etc.
- `variants` (number): Number of variations
- Returns: `Promise<Email[]>` with subject, body, cta

### `generateSocialPosts(options)`
Generate social media posts.
- `topic` (string): Post topic
- `platforms` (array): ['twitter', 'linkedin', 'instagram', 'tiktok']
- `tone` (string): Voice tone
- `variants` (number): Variations per platform
- Returns: `Promise<SocialPost[]>`

### `generateAds(options)`
Generate ad copy.
- `product` (string): Product name
- `targetAudience` (string): Who are we selling to?
- `adFormat` (string): 'facebook', 'google', 'instagram', 'linkedin'
- `variants` (number): Number of ad variations
- Returns: `Promise<Ad[]>` with headline, description, CTA, estimated CTR

## Troubleshooting

**"API key invalid"?**
→ Check your OPENAI_API_KEY is set correctly

**Too many API calls?**
→ Use batching: `generateEmailSequence()` instead of individual emails

**Need to match brand voice?**
→ Set `brandGuide` in config with your voice guidelines

## Support
📧 support@midas-skills.com
🔗 Docs: https://docs.midas-skills.com/marketing-drafter

---

**Want pro version + updates?** [Buy bundle on Gumroad](https://gumroad.com/midas-skills)
