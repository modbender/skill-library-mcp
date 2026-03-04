# Text Detection Skills

Skills for analyzing and detecting AI-generated text content.

## Required Skills

### 1. NLP Toolkit
**Skill ID**: `nlp-toolkit`
**Purpose**: Advanced natural language processing for text analysis

**Features**:
- Perplexity calculation
- Sentence structure analysis
- Entity extraction
- Language detection
- Burstiness measurement

**Installation**:
```bash
npm install @clawhub/nlp-toolkit
```

**Configuration**:
```javascript
{
  "skill": "nlp-toolkit",
  "settings": {
    "models": ["perplexity", "entity", "language"],
    "cacheResults": true,
    "timeout": 5000
  }
}
```

**Usage**:
```javascript
import { analyzeText } from '@clawhub/nlp-toolkit';

const result = await analyzeText(content);
// {
//   perplexity: 45.2,
//   burstiness: 0.65,
//   entities: ['GPT', 'AI'],
//   language: 'en',
//   complexity: 'medium'
// }
```

**Use Cases**:
- Measure text predictability
- Detect AI writing patterns
- Analyze sentence complexity
- Identify language and entities

**Troubleshooting**:
- If slow, enable caching
- For long text, split into chunks
- Language detection requires >100 chars

**Related Skills**: `pattern-matcher`, `gpt-analyzer`

---

### 2. GPT Pattern Analyzer
**Skill ID**: `gpt-analyzer`
**Purpose**: Detect GPT-specific writing patterns

**Features**:
- GPT-3.5/4 signature detection
- Common phrase identification
- Uniform structure detection
- Model fingerprinting

**Installation**:
```bash
npm install @clawhub/gpt-analyzer
```

**Configuration**:
```javascript
{
  "skill": "gpt-analyzer",
  "settings": {
    "models": ["gpt-3.5", "gpt-4"],
    "strictMode": false,
    "minConfidence": 0.7
  }
}
```

**Usage**:
```javascript
import { detectGPT } from '@clawhub/gpt-analyzer';

const result = await detectGPT(text);
// {
//   isGPT: true,
//   confidence: 0.85,
//   modelVersion: 'gpt-3.5',
//   patterns: ['uniform-length', 'formal-tone']
// }
```

**Use Cases**:
- Identify GPT-generated articles
- Detect ChatGPT responses
- Analyze essays and reports

**Troubleshooting**:
- High false positives? Increase minConfidence
- Missing detections? Disable strictMode
- Check model version matches expected output

**Related Skills**: `nlp-toolkit`, `pattern-matcher`

---

### 3. Pattern Matcher
**Skill ID**: `pattern-matcher`
**Purpose**: Fast pattern-based detection

**Features**:
- Regex pattern library
- Sentence structure matching
- Repetitive phrase detection
- Format consistency analysis

**Installation**:
```bash
npm install @clawhub/pattern-matcher
```

**Configuration**:
```javascript
{
  "skill": "pattern-matcher",
  "settings": {
    "patterns": [
      "repetitive-starts",
      "uniform-length",
      "formal-markers"
    ],
    "threshold": 3
  }
}
```

**Usage**:
```javascript
import { matchPatterns } from '@clawhub/pattern-matcher';

const result = matchPatterns(text);
// {
//   matched: 5,
//   patterns: ['repetitive-starts', 'uniform-length'],
//   confidence: 0.65
// }
```

**Use Cases**:
- Quick pre-filtering
- Supplement other methods
- Real-time detection

**Troubleshooting**:
- Too many matches? Increase threshold
- Add custom patterns for specific use cases
- Combine with perplexity for better accuracy

**Related Skills**: `nlp-toolkit`, `gpt-analyzer`

---

## Recommended Skills

### 4. Text Classifier
**Skill ID**: `text-classifier`
**Purpose**: ML-based text classification

**Features**:
- BERT-based classification
- Multi-class support (AI vs human vs mixed)
- Fine-tuned on AI text datasets
- Fast inference (<200ms)

**Installation**:
```bash
npm install @clawhub/text-classifier
```

**Use Cases**:
- High-accuracy classification
- Supplement rule-based methods
- Handle edge cases

**Related Skills**: `nlp-toolkit`

---

### 5. Content Hashing
**Skill ID**: `hash-toolkit`
**Purpose**: Fast content fingerprinting and deduplication

**Features**:
- SHA-256, MD5, xxHash
- Fuzzy matching
- Content deduplication
- Similarity scoring

**Installation**:
```bash
npm install @clawhub/hash-toolkit
```

**Use Cases**:
- Cache content analysis results
- Detect duplicate content
- Fast similarity checks

**Related Skills**: All detection skills

---

## Optional Skills

### 6. Sentiment Analyzer
**Skill ID**: `sentiment-analyzer`
**Purpose**: Analyze text sentiment and tone

**Features**:
- Positive/negative/neutral classification
- Emotion detection
- Tone analysis (formal, casual, technical)

**Use Cases**:
- Detect AI's typically neutral tone
- Identify emotional language (more human)
- Supplement detection methods

---

### 7. Fact Checker Integration
**Skill ID**: `fact-checker`
**Purpose**: Verify claims in text

**Features**:
- API integration with fact-checking services
- Claim extraction
- Source verification

**Use Cases**:
- Verify AI-generated facts
- Cross-reference claims
- Enhance trust scoring

---

## Skill Combinations

### Basic Detection Stack
```json
{
  "skills": [
    "nlp-toolkit",
    "pattern-matcher",
    "hash-toolkit"
  ]
}
```

**Use for**: Quick, lightweight detection

---

### Advanced Detection Stack
```json
{
  "skills": [
    "nlp-toolkit",
    "gpt-analyzer",
    "text-classifier",
    "pattern-matcher",
    "hash-toolkit"
  ]
}
```

**Use for**: Maximum accuracy, research

---

### Performance-Optimized Stack
```json
{
  "skills": [
    "pattern-matcher",
    "hash-toolkit"
  ]
}
```

**Use for**: Real-time, high-volume detection

---

## Skill Configuration Examples

### High Accuracy Mode
```javascript
{
  "nlp-toolkit": {
    "models": ["perplexity", "burstiness", "entity"],
    "minTextLength": 100
  },
  "gpt-analyzer": {
    "strictMode": true,
    "minConfidence": 0.8
  },
  "text-classifier": {
    "threshold": 0.9
  }
}
```

### Fast Mode
```javascript
{
  "pattern-matcher": {
    "patterns": ["basic"],
    "threshold": 2
  },
  "hash-toolkit": {
    "cacheEnabled": true,
    "algorithm": "xxhash"
  }
}
```

---

## Performance Metrics

| Skill | Speed | Accuracy | Memory |
|-------|-------|----------|--------|
| nlp-toolkit | Medium (500ms) | High (85%) | 50MB |
| gpt-analyzer | Fast (200ms) | High (88%) | 20MB |
| pattern-matcher | Very Fast (<50ms) | Medium (65%) | 5MB |
| text-classifier | Medium (300ms) | Very High (92%) | 100MB |
| hash-toolkit | Very Fast (<10ms) | N/A | 1MB |

---

## Troubleshooting

### Low Detection Accuracy
1. Enable all recommended skills
2. Use advanced detection stack
3. Increase minTextLength (>100 chars)
4. Combine multiple methods and average scores

### High False Positives
1. Increase confidence thresholds
2. Enable strictMode
3. Add custom pattern exclusions
4. Test on known human text

### Slow Performance
1. Use hash-toolkit for caching
2. Switch to fast mode configuration
3. Reduce enabled models
4. Process text in background

---

*For implementation examples and architecture details, see [AGENT.SPEC.md](../../AGENT.SPEC.md) and [SKILLS_MANAGEMENT.md](../../SKILLS_MANAGEMENT.md).*
