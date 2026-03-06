# ContextCompressor API Documentation

## Overview

The ContextCompressor class provides intelligent context compression for AI agents, reducing token usage by 40-60% while maintaining information quality. It supports multiple compression strategies and is optimized for the free tier (no API calls required).

## Installation

```javascript
import { ContextCompressor, createCompressor } from './compressor.js';
```

## Quick Start

```javascript
const compressor = new ContextCompressor();

const result = await compressor.compress(context, 'hybrid');

console.log(`Compressed ${result.metrics.originalTokens} tokens to ${result.metrics.compressedTokens}`);
console.log(`Compression: ${(result.metrics.compressionRatio * 100).toFixed(1)}%`);
console.log(`Quality: ${result.metrics.qualityScore.toFixed(3)}`);
```

---

## Class: ContextCompressor

### Constructor

```javascript
new ContextCompressor(storage = null, options = {})
```

**Parameters:**
- `storage` (optional): Storage instance for persistence
- `options` (optional): Configuration object

**Options:**
- `targetCompressionRatio` (default: `0.5`): Target compression ratio (0.0 to 1.0)
  - `0.5` = 50% compression
  - `0.6` = 60% compression
- `similarityThreshold` (default: `0.9`): Cosine similarity threshold for deduplication
  - Higher values = more conservative (only remove very similar text)
  - Lower values = more aggressive (remove somewhat similar text)
- `minChunkSize` (default: `50`): Minimum chunk size in characters
- `maxChunkSize` (default: `500`): Maximum chunk size in characters
- `preserveCodeBlocks` (default: `true`): Preserve code blocks during compression
- `preserveImportantSections` (default: `true`): Preserve sections marked as important

**Example:**
```javascript
const compressor = new ContextCompressor(null, {
  targetCompressionRatio: 0.6,
  similarityThreshold: 0.85,
  preserveCodeBlocks: true
});
```

---

## Main Methods

### compress()

Compress context using specified strategy.

```javascript
async compress(context, strategy = 'hybrid', options = {})
```

**Parameters:**
- `context` (string|object): Context to compress (string or structured object)
- `strategy` (string): Compression strategy
  - `'deduplication'`: Remove redundant/similar text
  - `'pruning'`: Remove low-value content
  - `'summarization'`: Condense verbose sections
  - `'template'`: Remove boilerplate/templates
  - `'hybrid'`: Combine all strategies (recommended)
- `options` (object): Override default options for this compression

**Returns:** Promise resolving to:
```javascript
{
  original: string,           // Original context
  compressed: string,         // Compressed context
  strategy: string,           // Strategy used
  metrics: {
    originalTokens: number,        // Original token count
    compressedTokens: number,      // Compressed token count
    tokensRemoved: number,         // Tokens removed
    compressionRatio: number,      // Compression ratio (0.0 to 1.0)
    percentageReduction: number,   // Percentage reduction
    compressionTime: number,       // Time taken in ms
    qualityScore: number          // Quality score (0.0 to 1.0)
  }
}
```

**Example:**
```javascript
const result = await compressor.compress(context, 'hybrid', {
  targetCompressionRatio: 0.5
});

console.log(result.compressed);
console.log(result.metrics);
```

---

## Compression Strategies

### 1. Deduplication

Removes redundant and highly similar text using cosine similarity.

```javascript
async deduplicateContext(context, options = {})
```

**Use Case:** Remove duplicate statements or repeated information

**Example:**
```javascript
const context = `User: I prefer TypeScript.
TypeScript is better than JavaScript.
User: I like TypeScript.`;

const result = await compressor.compress(context, 'deduplication');
// Removes duplicate/similar statements about TypeScript preference
```

---

### 2. Pruning

Removes low-value content based on patterns (greetings, filler phrases, etc.).

```javascript
async pruneContext(context, patterns = null, options = {})
```

**Use Case:** Remove conversational fluff and low-value phrases

**Automatically Removes:**
- Greetings: "Hello", "Hi", "Bye"
- Acknowledgments: "Thanks", "Okay", "Sure"
- Common questions: "Can you help me?", "How are you?"
- Filler phrases: "Let me know", "Feel free"

**Example:**
```javascript
const context = `Hello! How are you?
The project uses microservices.
Thanks for your help!
Each service has its own database.`;

const result = await compressor.compress(context, 'pruning');
// Keeps only: "The project uses microservices. Each service has its own database."
```

---

### 3. Summarization

Condenses verbose sections using extractive summarization (selects most important sentences).

```javascript
async summarizeContext(context, options = {})
```

**Use Case:** Reduce lengthy explanations while keeping key information

**How It Works:**
- Scores each sentence by importance
- Selects top N% of sentences (based on `targetCompressionRatio`)
- Preserves code blocks automatically
- Prioritizes sentences with:
  - Named entities (proper nouns)
  - Technical terms
  - Numbers and data
  - Important markers ("error", "warning", "critical")

**Example:**
```javascript
const result = await compressor.compress(verboseContext, 'summarization', {
  targetCompressionRatio: 0.5  // Keep 50% of content
});
```

---

### 4. Template Removal

Removes boilerplate, templates, and repeated structural patterns.

```javascript
async removeTemplates(context, options = {})
```

**Use Case:** Clean up documentation, remove headers/footers

**Automatically Removes:**
- Horizontal dividers (`---`, `***`, `===`)
- Copyright notices
- License headers
- Auto-generated notices
- HTML comments
- Comment dividers
- Repeated structural patterns (appears 3+ times)

**Example:**
```javascript
const context = `---
Copyright (c) 2024
Licensed under MIT
---

Main content here`;

const result = await compressor.compress(context, 'template');
// Returns only: "Main content here"
```

---

### 5. Hybrid (Recommended)

Combines all strategies for maximum compression while maintaining quality.

```javascript
async hybridCompress(context, options = {})
```

**How It Works:**
1. Remove templates/boilerplate
2. Deduplicate similar sections
3. Prune low-value content
4. Summarize if needed to meet target compression ratio

**Use Case:** Default strategy for most scenarios

**Example:**
```javascript
const result = await compressor.compress(context, 'hybrid');
// Applies all strategies intelligently
```

---

## Utility Methods

### estimateTokens()

Estimate token count using heuristic (4 chars ≈ 1 token).

```javascript
estimateTokens(text)
```

**Parameters:**
- `text` (string): Text to estimate

**Returns:** number - Estimated token count

**Example:**
```javascript
const tokens = compressor.estimateTokens('Hello world');
console.log(tokens); // ~3
```

**Note:** Uses hybrid approach:
- Character-based: `length / 4`
- Word-based: `wordCount * 1.3`
- Returns average for better accuracy

---

### calculateMetrics()

Calculate compression metrics.

```javascript
calculateMetrics(originalContext, compressedContext)
```

**Parameters:**
- `originalContext` (string): Original text
- `compressedContext` (string): Compressed text

**Returns:** object
```javascript
{
  originalTokens: number,
  compressedTokens: number,
  tokensRemoved: number,
  compressionRatio: number,      // 0.0 to 1.0
  percentageReduction: number    // 0 to 100
}
```

---

### calculateQualityScore()

Calculate quality score based on information retention.

```javascript
calculateQualityScore(original, compressed)
```

**Parameters:**
- `original` (string): Original text
- `compressed` (string): Compressed text

**Returns:** number (0.0 to 1.0)

**Quality Factors:**
- Named entities retained
- Code blocks retained
- Numbers/data retained
- Keywords retained
- Sentence structure retained

**Interpretation:**
- `0.8+`: Excellent quality
- `0.6-0.8`: Good quality
- `0.4-0.6`: Acceptable quality
- `<0.4`: Poor quality (too much compression)

**Example:**
```javascript
const score = compressor.calculateQualityScore(original, compressed);
console.log(`Quality: ${(score * 100).toFixed(0)}%`);
```

---

## Helper Methods

### splitIntoChunks()

Split text into logical chunks (paragraphs or lines).

```javascript
splitIntoChunks(text)
```

---

### splitIntoSentences()

Split text into sentences.

```javascript
splitIntoSentences(text)
```

---

### isImportantSection()

Check if section should be preserved.

```javascript
isImportantSection(text)
```

**Preserves:**
- Code blocks
- Sections with markers: "error", "warning", "critical", "important", "todo", "fixme"
- Numbered/bulleted lists
- Technical code patterns

---

## Factory Function

### createCompressor()

Factory function for creating compressor instances.

```javascript
createCompressor(storage = null, options = {})
```

**Example:**
```javascript
import { createCompressor } from './compressor.js';

const compressor = createCompressor(null, {
  targetCompressionRatio: 0.6
});
```

---

## Performance

### Token Estimation
- **Method:** Heuristic-based (no API calls)
- **Speed:** Instant (<1ms)
- **Accuracy:** ±10% compared to actual tokenizers

### Compression Speed
- **Small context** (<1000 tokens): <5ms
- **Medium context** (1000-5000 tokens): <20ms
- **Large context** (5000-10000 tokens): <100ms

### Memory Usage
- Minimal (no external dependencies for compression)
- Linear with input size

---

## Best Practices

### 1. Choose the Right Strategy

- **Hybrid:** Default for most cases
- **Deduplication:** When you have repeated information
- **Pruning:** For conversational logs with fluff
- **Summarization:** For long, verbose explanations
- **Template:** For documentation cleanup

### 2. Tune Compression Ratio

```javascript
// Conservative (40% compression)
{ targetCompressionRatio: 0.4 }

// Balanced (50% compression)
{ targetCompressionRatio: 0.5 }

// Aggressive (60-70% compression)
{ targetCompressionRatio: 0.7 }
```

### 3. Monitor Quality

```javascript
const result = await compressor.compress(context);

if (result.metrics.qualityScore < 0.5) {
  console.warn('Quality too low, reduce compression');
}
```

### 4. Preserve Important Content

```javascript
const compressor = new ContextCompressor(null, {
  preserveCodeBlocks: true,
  preserveImportantSections: true
});
```

---

## Examples

### Example 1: Basic Compression

```javascript
const compressor = new ContextCompressor();
const result = await compressor.compress(longContext, 'hybrid');

console.log(`Saved ${result.metrics.tokensRemoved} tokens`);
```

### Example 2: Custom Options

```javascript
const compressor = new ContextCompressor(null, {
  targetCompressionRatio: 0.6,
  similarityThreshold: 0.85
});

const result = await compressor.compress(context, 'hybrid');
```

### Example 3: Quality Check

```javascript
const result = await compressor.compress(context);

if (result.metrics.compressionRatio < 0.3) {
  console.warn('Low compression achieved');
}

if (result.metrics.qualityScore < 0.5) {
  console.warn('Quality too low');
}
```

### Example 4: Structured Data

```javascript
const contextObj = {
  user: { name: 'John', preferences: [...] },
  history: [...]
};

const result = await compressor.compress(contextObj, 'hybrid');
```

---

## Error Handling

The compressor handles errors gracefully:

```javascript
try {
  const result = await compressor.compress(context);
  console.log(result.compressed);
} catch (error) {
  console.error('Compression failed:', error);
}
```

**Common Issues:**
- Empty input: Returns empty output with 0 metrics
- Invalid input: Converts to string automatically
- Large input: May take longer but won't crash

---

## Integration

### With OpenClaw Memory System

```javascript
import { ContextCompressor } from './compressor.js';
import { MemoryStorage } from './storage.js';

const storage = new MemoryStorage(dbPath);
const compressor = new ContextCompressor(storage);

// Compress before storing
const result = await compressor.compress(context);
await storage.storeContext(result.compressed);
```

### With API Calls

```javascript
// Before API call
const result = await compressor.compress(conversationHistory);

const response = await fetch(apiUrl, {
  method: 'POST',
  body: JSON.stringify({
    context: result.compressed  // Reduced tokens!
  })
});
```

---

## Testing

Run tests:

```bash
node --test src/compressor.test.js
```

Run examples:

```bash
node src/compressor.example.js
```

---

## License

MIT License - Part of OpenClaw Context Optimizer

---

## See Also

- [MemoryAnalyzer](../openclaw-memory/src/analyzer.js) - Pattern detection reference
- [Embeddings](../openclaw-memory/src/embeddings.js) - Similarity calculation reference
