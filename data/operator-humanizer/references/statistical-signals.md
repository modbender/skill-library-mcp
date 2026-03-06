# Statistical Signals of AI Writing

How to measure AI-likelihood using statistical analysis: burstiness, vocabulary diversity, sentence uniformity, and trigram repetition.

---

## Why Statistical Analysis Matters

Pattern detection catches obvious AI-isms (delve, tapestry, etc.), but statistical analysis reveals deeper structural tells:

- **Humans write in bursts** → Vary sentence length naturally
- **Humans reuse vocabulary** → Lower type-token ratio
- **Humans have rhythm** → High coefficient of variation in sentence length
- **Humans don't repeat phrases** → Low trigram repetition

AI writing is too uniform, too consistent, too perfect.

---

## METRIC 1: Burstiness

### What It Measures

Burstiness measures how much sentence lengths vary. Humans write in bursts—short punchy sentences, then longer ones, then short again. AI writes metronomically.

### Formula

```
Burstiness = (σ - μ) / (σ + μ)

Where:
σ = standard deviation of sentence lengths
μ = mean sentence length
```

### Interpretation

| Score | Likelihood | Meaning |
|-------|------------|---------|
| 0.5 - 1.0 | Human | High variation in sentence length |
| 0.3 - 0.5 | Mixed | Moderate variation |
| 0.1 - 0.3 | AI | Low variation (metronomic) |
| < 0.1 | Very AI | Extremely uniform sentences |

### Example Calculation

**Text:**
"I went to the store. It was closed. I came home and made dinner instead because I was hungry and didn't want to wait."

**Sentence lengths:** 5, 3, 17 words

**Calculation:**
- Mean (μ) = (5 + 3 + 17) / 3 = 8.33
- Standard deviation (σ) = 6.02
- Burstiness = (6.02 - 8.33) / (6.02 + 8.33) = -0.16

**Interpretation:** Negative burstiness (which normalizes to ~0.15) suggests AI-like uniformity.

### Implementation

```javascript
function calculateBurstiness(text) {
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
  const lengths = sentences.map(s => s.trim().split(/\s+/).length);
  
  const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
  const variance = lengths.reduce((sum, len) => sum + Math.pow(len - mean, 2), 0) / lengths.length;
  const stdDev = Math.sqrt(variance);
  
  const burstiness = (stdDev - mean) / (stdDev + mean);
  
  return {
    burstiness,
    mean,
    stdDev,
    sentenceCount: lengths.length,
    lengths
  };
}
```

---

## METRIC 2: Type-Token Ratio (TTR)

### What It Measures

Type-token ratio measures vocabulary diversity. Humans naturally reuse words; AI tends to vary vocabulary excessively (elegant variation).

### Formula

```
TTR = (unique words / total words)
```

### Interpretation

| Score | Likelihood | Meaning |
|-------|------------|---------|
| 0.5 - 0.7 | Human | Natural vocabulary reuse |
| 0.4 - 0.5 | Mixed | Moderate diversity |
| 0.3 - 0.4 | AI | High reuse (or very short text) |
| > 0.7 | AI | Excessive variation (synonym cycling) |

**Note:** TTR is length-dependent. Longer texts naturally have lower TTR. Use MATTR (Moving Average TTR) for texts over 200 words.

### Example Calculation

**Text:** "The cat sat on the mat. The cat was happy. The mat was soft."

**Total words:** 14
**Unique words:** 9 (the, cat, sat, on, mat, was, happy, soft)
**TTR:** 9 / 14 = 0.64

**Interpretation:** 0.64 suggests human-like vocabulary reuse.

### Implementation

```javascript
function calculateTTR(text) {
  const words = text.toLowerCase()
    .replace(/[^a-z\s]/g, '')
    .split(/\s+/)
    .filter(w => w.length > 0);
  
  const uniqueWords = new Set(words);
  
  const ttr = uniqueWords.size / words.length;
  
  return {
    ttr,
    totalWords: words.length,
    uniqueWords: uniqueWords.size
  };
}
```

### MATTR (Moving Average Type-Token Ratio)

For longer texts, use MATTR with a sliding window:

```javascript
function calculateMATTR(text, windowSize = 50) {
  const words = text.toLowerCase()
    .replace(/[^a-z\s]/g, '')
    .split(/\s+/)
    .filter(w => w.length > 0);
  
  if (words.length < windowSize) {
    return calculateTTR(text).ttr;
  }
  
  let sum = 0;
  let count = 0;
  
  for (let i = 0; i <= words.length - windowSize; i++) {
    const window = words.slice(i, i + windowSize);
    const unique = new Set(window);
    sum += unique.size / windowSize;
    count++;
  }
  
  return sum / count;
}
```

---

## METRIC 3: Sentence Length Coefficient of Variation (CoV)

### What It Measures

Coefficient of variation measures relative variability in sentence length. Humans have high CoV (varied rhythm); AI has low CoV (uniform rhythm).

### Formula

```
CoV = (standard deviation / mean) × 100
```

### Interpretation

| Score | Likelihood | Meaning |
|-------|------------|---------|
| > 60% | Human | High variation in sentence length |
| 40-60% | Mixed | Moderate variation |
| 20-40% | AI | Low variation |
| < 20% | Very AI | Extremely uniform sentences |

### Example Calculation

**Text with three sentences:**
- Sentence 1: 15 words
- Sentence 2: 8 words
- Sentence 3: 22 words

**Calculation:**
- Mean = (15 + 8 + 22) / 3 = 15
- Standard deviation = 5.72
- CoV = (5.72 / 15) × 100 = 38.1%

**Interpretation:** 38.1% suggests AI-like uniformity.

### Implementation

```javascript
function calculateSentenceLengthCoV(text) {
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
  const lengths = sentences.map(s => s.trim().split(/\s+/).length);
  
  const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
  const variance = lengths.reduce((sum, len) => sum + Math.pow(len - mean, 2), 0) / lengths.length;
  const stdDev = Math.sqrt(variance);
  
  const cov = (stdDev / mean) * 100;
  
  return {
    cov,
    mean,
    stdDev,
    min: Math.min(...lengths),
    max: Math.max(...lengths)
  };
}
```

---

## METRIC 4: Trigram Repetition Rate

### What It Measures

Trigrams are 3-word sequences. AI writing repeats trigrams more frequently than human writing (due to pattern reinforcement in training).

### Formula

```
Trigram Repetition Rate = (repeated trigrams / total trigrams)
```

### Interpretation

| Score | Likelihood | Meaning |
|-------|------------|---------|
| < 0.05 | Human | Low trigram reuse |
| 0.05 - 0.08 | Mixed | Moderate reuse |
| 0.08 - 0.12 | AI | High reuse |
| > 0.12 | Very AI | Excessive phrase repetition |

### Example Calculation

**Text:** "I went to the store. I went to the park. I went to the gym."

**Trigrams:**
- "I went to" (repeated 3 times)
- "went to the" (repeated 3 times)
- "to the store" (once)
- "to the park" (once)
- "to the gym" (once)

**Total trigrams:** 9
**Repeated trigrams:** 6 (the two repeated 3 times each = 6 repetitions)
**Rate:** 6 / 9 = 0.67

**Interpretation:** 67% repetition is extremely high, suggesting AI or very repetitive human writing.

### Implementation

```javascript
function calculateTrigramRepetition(text) {
  const words = text.toLowerCase()
    .replace(/[^a-z\s]/g, '')
    .split(/\s+/)
    .filter(w => w.length > 0);
  
  const trigrams = [];
  for (let i = 0; i < words.length - 2; i++) {
    trigrams.push(words.slice(i, i + 3).join(' '));
  }
  
  const trigramCounts = {};
  trigrams.forEach(t => {
    trigramCounts[t] = (trigramCounts[t] || 0) + 1;
  });
  
  const repeated = Object.values(trigramCounts)
    .filter(count => count > 1)
    .reduce((sum, count) => sum + count, 0);
  
  const rate = repeated / trigrams.length;
  
  return {
    rate,
    totalTrigrams: trigrams.length,
    uniqueTrigrams: Object.keys(trigramCounts).length,
    repeatedTrigrams: repeated,
    mostCommon: Object.entries(trigramCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
  };
}
```

---

## METRIC 5: Readability Scores

### Flesch Reading Ease

Measures how easy text is to read. AI tends toward moderate readability (not too simple, not too complex).

**Formula:**
```
206.835 - 1.015 × (total words / total sentences) - 84.6 × (total syllables / total words)
```

**Interpretation:**
- 90-100: Very easy (5th grade)
- 60-70: Standard (8th-9th grade)
- 30-50: Difficult (college level)
- 0-30: Very difficult (professional)

**AI tends to score:** 50-70 (moderate readability)

### Gunning Fog Index

Measures years of formal education needed to understand text.

**Formula:**
```
0.4 × [(words/sentences) + 100 × (complex words/words)]
```

Where complex words = 3+ syllables

**AI tends to score:** 10-14 (high school to college)

### Implementation

```javascript
function calculateReadability(text) {
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
  const words = text.match(/\b[a-z]+\b/gi) || [];
  const syllables = words.reduce((sum, word) => sum + countSyllables(word), 0);
  
  const fleschScore = 206.835 
    - 1.015 * (words.length / sentences.length)
    - 84.6 * (syllables / words.length);
  
  return {
    flesch: Math.max(0, Math.min(100, fleschScore)),
    sentences: sentences.length,
    words: words.length,
    syllables
  };
}

function countSyllables(word) {
  word = word.toLowerCase();
  if (word.length <= 3) return 1;
  
  const vowels = word.match(/[aeiouy]+/g);
  let count = vowels ? vowels.length : 1;
  
  if (word.endsWith('e')) count--;
  if (word.endsWith('le') && word.length > 2) count++;
  
  return Math.max(1, count);
}
```

---

## COMPOSITE AI SCORE

Combine multiple metrics for comprehensive AI detection:

### Scoring Formula

```
AI Score = (
  burstinessScore × 0.25 +
  ttrScore × 0.20 +
  covScore × 0.25 +
  trigramScore × 0.20 +
  readabilityScore × 0.10
) × 100
```

### Individual Metric Scoring

**Burstiness:**
- < 0.2 = 1.0 (very AI)
- 0.2-0.4 = 0.5
- > 0.4 = 0.0 (human)

**TTR:**
- < 0.35 = 1.0 (AI)
- 0.35-0.5 = 0.3
- 0.5-0.7 = 0.0 (human)
- > 0.7 = 0.8 (synonym cycling)

**CoV:**
- < 30% = 1.0 (very AI)
- 30-50% = 0.5
- > 50% = 0.0 (human)

**Trigram Rate:**
- > 0.12 = 1.0 (very AI)
- 0.08-0.12 = 0.7
- 0.05-0.08 = 0.3
- < 0.05 = 0.0 (human)

**Readability:**
- 55-65 Flesch = 0.5 (AI sweet spot)
- Outside range = 0.0

### Interpretation

| Score | Likelihood |
|-------|------------|
| 0-20 | Very likely human |
| 21-40 | Probably human |
| 41-60 | Mixed/uncertain |
| 61-80 | Probably AI |
| 81-100 | Very likely AI |

### Implementation

```javascript
function calculateCompositeAIScore(text) {
  const burstiness = calculateBurstiness(text);
  const ttr = calculateMATTR(text);
  const cov = calculateSentenceLengthCoV(text);
  const trigram = calculateTrigramRepetition(text);
  const readability = calculateReadability(text);
  
  // Score individual metrics (0 = human, 1 = AI)
  const bScore = burstiness.burstiness < 0.2 ? 1.0 : 
                 burstiness.burstiness < 0.4 ? 0.5 : 0.0;
  
  const tScore = ttr < 0.35 ? 1.0 :
                 ttr < 0.5 ? 0.3 :
                 ttr > 0.7 ? 0.8 : 0.0;
  
  const cScore = cov.cov < 30 ? 1.0 :
                 cov.cov < 50 ? 0.5 : 0.0;
  
  const trScore = trigram.rate > 0.12 ? 1.0 :
                  trigram.rate > 0.08 ? 0.7 :
                  trigram.rate > 0.05 ? 0.3 : 0.0;
  
  const rScore = readability.flesch >= 55 && readability.flesch <= 65 ? 0.5 : 0.0;
  
  // Weighted composite
  const composite = (
    bScore * 0.25 +
    tScore * 0.20 +
    cScore * 0.25 +
    trScore * 0.20 +
    rScore * 0.10
  ) * 100;
  
  return {
    compositeScore: Math.round(composite),
    metrics: {
      burstiness: { value: burstiness.burstiness, score: bScore },
      ttr: { value: ttr, score: tScore },
      cov: { value: cov.cov, score: cScore },
      trigram: { value: trigram.rate, score: trScore },
      readability: { value: readability.flesch, score: rScore }
    }
  };
}
```

---

## PRACTICAL USAGE

### Quick Statistical Check (2 minutes)

```javascript
// 1. Calculate burstiness
const burst = calculateBurstiness(text);
console.log(`Burstiness: ${burst.burstiness.toFixed(2)}`);

// 2. Calculate sentence length CoV
const cov = calculateSentenceLengthCoV(text);
console.log(`CoV: ${cov.cov.toFixed(1)}%`);

// 3. If both are low, likely AI
if (burst.burstiness < 0.3 && cov.cov < 40) {
  console.log("⚠️ Statistical signals suggest AI writing");
}
```

### Comprehensive Analysis (5 minutes)

```javascript
const analysis = calculateCompositeAIScore(text);

console.log(`Composite AI Score: ${analysis.compositeScore}/100`);
console.log("Breakdown:");
console.log(`  Burstiness: ${analysis.metrics.burstiness.value.toFixed(2)}`);
console.log(`  TTR: ${analysis.metrics.ttr.value.toFixed(2)}`);
console.log(`  CoV: ${analysis.metrics.cov.value.toFixed(1)}%`);
console.log(`  Trigrams: ${(analysis.metrics.trigram.value * 100).toFixed(1)}%`);
console.log(`  Readability: ${analysis.metrics.readability.value.toFixed(0)}`);

if (analysis.compositeScore > 60) {
  console.log("⚠️ High probability of AI generation");
}
```

---

## LIMITATIONS

### When Statistical Analysis Fails

**False positives (flagging human as AI):**
- Technical documentation (naturally uniform)
- News articles (standardized AP style)
- Academic abstracts (formal structure)
- Legal writing (consistent language)

**False negatives (missing AI):**
- Heavily edited AI content
- AI trained to vary sentence length
- Short texts (< 200 words)
- Lists and bullet points

### Best Practices

1. **Combine with pattern detection** → Use both statistical and pattern-based methods
2. **Consider context** → Technical writing is naturally more uniform
3. **Check multiple metrics** → Don't rely on one signal alone
4. **Use human judgment** → Statistics inform, don't decide

---

## SUMMARY

| Metric | What It Measures | Human Range | AI Range |
|--------|------------------|-------------|----------|
| Burstiness | Sentence length variation | 0.4-1.0 | 0.1-0.3 |
| TTR | Vocabulary diversity | 0.5-0.7 | 0.3-0.5 or >0.7 |
| CoV | Sentence rhythm | >50% | <40% |
| Trigram | Phrase repetition | <5% | >10% |
| Flesch | Readability | Varied | 50-70 |

**Quick check:** If burstiness < 0.3 AND CoV < 40%, text is likely AI.

**Comprehensive check:** Use composite score combining all 5 metrics.
