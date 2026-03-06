# AI Platform Guide

## Platform-Specific Characteristics

### ChatGPT (OpenAI)

**Answer Style**: Conversational, comprehensive

**Citation Behavior**:
- Rarely cites sources explicitly in default mode
- Browse with Bing provides citations
- Training data cutoff limits recency

**Prompt Types That Perform Well**:
- Definition questions
- How-to guides
- Creative tasks
- Exploratory queries

**Content Preferences**:
- Clear, direct answers
- Structured with headers
- Bulleted lists
- Comprehensive coverage

**GEO Implications**:
- Brand mentions require training data presence
- Older content has advantage (pre-2024)
- Web browsing mode increasingly important
- Direct answers prioritized

**Monitoring Approach**:
- Test in both standard and browse modes
- Check brand mentions across GPT-3.5 and GPT-4
- Monitor for hallucinations

---

### Perplexity

**Answer Style**: Research-focused, citation-heavy

**Citation Behavior**:
- Always cites sources
- Links to original content
- Shows multiple perspectives
- Real-time web search

**Prompt Types That Perform Well**:
- Comparison queries
- Research questions
- Current events
- Fact-checking

**Content Preferences**:
- Authoritative sources
- Recent publications
- Well-structured articles
- FAQ format

**GEO Implications**:
- Citations are visible and trackable
- Source diversity matters
- Recency heavily weighted
- Domain authority signals important

**Monitoring Approach**:
- Track citation frequency
- Monitor source position (first cited = high value)
- Check answer accuracy
- Watch for competitor citations

---

### Gemini (Google)

**Answer Style**: Balanced, Google-ecosystem integrated

**Citation Behavior**:
- Moderate citation frequency
- Often synthesizes without explicit attribution
- Links to Google sources (YouTube, Maps)

**Prompt Types That Perform Well**:
- Local queries
- How-to with visual elements
- Product comparisons
- YouTube-related content

**Content Preferences**:
- YouTube video content
- Local business data
- Structured data (Schema.org)
- Comprehensive guides

**GEO Implications**:
- YouTube presence valuable
- Local SEO factors apply
- Google Business Profile important
- Schema markup helps understanding

**Monitoring Approach**:
- Test across query types
- Monitor YouTube citations
- Check local pack integration
- Track knowledge panel presence

---

### Claude (Anthropic)

**Answer Style**: Nuanced, safety-conscious

**Citation Behavior**:
- Limited explicit citation
- References sources in text
- Conservative about claims

**Prompt Types That Perform Well**:
- Complex reasoning
- Ethical considerations
- Long-form analysis
- Creative writing

**Content Preferences**:
- High-quality sources
- Balanced perspectives
- Detailed explanations
- Original insights

**GEO Implications**:
- Quality over quantity
- Unique data highly valued
- Safety and accuracy important
- Long-form content performs well

**Monitoring Approach**:
- Test for brand comprehension
- Monitor for balanced mentions
- Check accuracy of representations

---

## Platform Comparison

| Factor | ChatGPT | Perplexity | Gemini | Claude |
|--------|---------|------------|--------|--------|
| **Citation Style** | Minimal/Contextual | Explicit links | Moderate | Textual |
| **Recency** | Limited (browse mode) | Real-time | Real-time | Limited |
| **Source Visibility** | Low | High | Medium | Low |
| **Answer Length** | Medium-Long | Medium | Medium | Long |
| **Best For** | Definitions, How-to | Research, Compare | Local, Visual | Analysis, Complex |
| **Training Data** | Pre-2024 + Browse | Real-time | Real-time | Pre-2024 |
| **Commercial Intent** | Medium | High | High | Low |

---

## Platform-Specific Optimization

### For ChatGPT

**Tactics**:
- Ensure brand is in training data (pre-2024 content)
- Create comprehensive definitional content
- Use clear, direct answer formats
- Structure with headers and lists
- Target how-to and tutorial content

**Content Types**:
- Ultimate guides
- Glossaries
- Step-by-step tutorials
- Comparison articles

---

### For Perplexity

**Tactics**:
- Publish authoritative, citable content
- Keep content current and updated
- Use FAQ format for common questions
- Include data and statistics
- Ensure fast page load (crawl frequency)

**Content Types**:
- Research reports
- Data studies
- Comprehensive FAQs
- Comparison pages

---

### For Gemini

**Tactics**:
- Optimize YouTube content
- Maintain Google Business Profile
- Implement Schema markup
- Create visual/multimedia content
- Target local queries

**Content Types**:
- Video tutorials
- Local landing pages
- How-to with images
- Product demos

---

### For Claude

**Tactics**:
- Publish original research
- Provide nuanced analysis
- Ensure factual accuracy
- Create long-form, comprehensive content
- Address ethical considerations

**Content Types**:
- Industry analysis
- Thought leadership
- Research papers
- In-depth guides

---

## Cross-Platform Strategy

### Universal Best Practices

1. **Direct Answers First**: All platforms favor clear, upfront answers
2. **Structured Content**: Headers, lists, and tables help all platforms parse
3. **Entity Clarity**: Named brands, products, and people understood by all
4. **Factual Accuracy**: Corrections and accuracy matter across platforms
5. **Comprehensive Coverage**: Thorough content outperforms thin pages

### Platform-Specific Monitoring

Set up monitoring for each platform:

```
Weekly Checks:
├── ChatGPT: Brand comprehension, answer accuracy
├── Perplexity: Citation frequency, source position
├── Gemini: Knowledge panel, YouTube citations
└── Claude: Brand mention context, accuracy

Monthly Analysis:
├── Compare visibility across platforms
├── Identify platform-specific gaps
├── Adjust content strategy per platform
└── Track competitor presence
```

### Measurement Framework

| Platform | Primary Metric | Secondary Metrics |
|----------|----------------|-------------------|
| ChatGPT | Mention accuracy | Answer completeness |
| Perplexity | Citation rate | Source position |
| Gemini | Knowledge panel | YouTube integration |
| Claude | Mention frequency | Context accuracy |