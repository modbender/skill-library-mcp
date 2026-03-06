---
domain: openclaw-examiner
topic: scoring-methodology
priority: high
ttl: 90d
---

# OpenClaw Examiner Scoring Methodology

## Scoring Overview

The OpenClaw Examiner uses a multi-level scoring system:

1. **Criterion-Level**: Each question has 2-4 criteria scored 0-5
2. **Question-Level**: Criterion scores weighted and summed
3. **Dimension-Level**: Question scores aggregated per dimension
4. **Overall-Level**: Dimension scores weighted and combined

## Point Scale

| Score | Descriptor | Description |
|-------|------------|-------------|
| 5 | Excellent | Exceeds expectations, exceptional quality |
| 4 | Good | Meets expectations with minor issues |
| 3 | Satisfactory | Meets minimum requirements, room for improvement |
| 2 | Fair | Partially meets requirements, significant issues |
| 1 | Poor | Minimal achievement of requirements |
| 0 | No Credit | No meaningful attempt or completely incorrect |

## Scoring Rubrics by Dimension

### Information Retrieval Scoring

#### Criterion 1: Relevance (Weight: 0.35)
| Score | Description |
|-------|-------------|
| 5 | All information highly relevant to query, no noise |
| 4 | Mostly relevant, minimal irrelevant content |
| 3 | Generally relevant with some irrelevant items |
| 2 | Mixed relevance, significant noise |
| 1 | Mostly irrelevant to query |
| 0 | No relevant information found |

#### Criterion 2: Completeness (Weight: 0.30)
| Score | Description |
|-------|-------------|
| 5 | Comprehensive coverage of all aspects |
| 4 | Covers most aspects, minor omissions |
| 3 | Covers main aspects, some omissions |
| 2 | Limited coverage, significant gaps |
| 1 | Minimal coverage |
| 0 | No meaningful information |

#### Criterion 3: Source Quality (Weight: 0.20)
| Score | Description |
|-------|-------------|
| 5 | Authoritative, diverse, high-quality sources |
| 4 | Good sources with minor quality concerns |
| 3 | Acceptable sources, some quality issues |
| 2 | Questionable sources |
| 1 | Poor or unreliable sources |
| 0 | No sources or completely unreliable |

#### Criterion 4: Efficiency (Weight: 0.15)
| Score | Description |
|-------|-------------|
| 5 | Optimal queries, minimal time, well-organized results |
| 4 | Efficient with minor optimization opportunities |
| 3 | Reasonable efficiency |
| 2 | Inefficient query strategy |
| 1 | Very inefficient, excessive queries |
| 0 | No meaningful efficiency demonstrated |

---

### Content Understanding Scoring

#### Criterion 1: Comprehension Accuracy (Weight: 0.40)
| Score | Description |
|-------|-------------|
| 5 | Complete understanding, captures all nuances |
| 4 | Strong understanding with minor gaps |
| 3 | Adequate understanding, some nuances missed |
| 2 | Partial understanding, key elements missed |
| 1 | Surface-level understanding only |
| 0 | No demonstrated understanding |

#### Criterion 2: Insight Quality (Weight: 0.30)
| Score | Description |
|-------|-------------|
| 5 | Deep insights, connections not immediately obvious |
| 4 | Good insights, meaningful observations |
| 3 | Basic insights, obvious observations |
| 2 | Limited insights, superficial analysis |
| 1 | Trivial or no insights |
| 0 | No insights provided |

#### Criterion 3: Extraction Completeness (Weight: 0.30)
| Score | Description |
|-------|-------------|
| 5 | All key information extracted and organized |
| 4 | Most key information extracted |
| 3 | Main information extracted, some gaps |
| 2 | Limited extraction, important elements missing |
| 1 | Minimal extraction |
| 0 | No meaningful extraction |

---

### Logical Reasoning Scoring

#### Criterion 1: Logical Soundness (Weight: 0.40)
| Score | Description |
|-------|-------------|
| 5 | Flawless logic, all steps valid, no assumptions |
| 4 | Sound reasoning with minor issues |
| 3 | Generally valid with some weak points |
| 2 | Significant logical flaws or leaps |
| 1 | Poor reasoning, major fallacies |
| 0 | No valid logic demonstrated |

#### Criterion 2: Step Clarity (Weight: 0.30)
| Score | Description |
|-------|-------------|
| 5 | Clear, well-explained step-by-step reasoning |
| 4 | Clear with some minor explanation gaps |
| 3 | Steps present but some unclear |
| 2 | Unclear or missing steps |
| 1 | Very unclear reasoning |
| 0 | No step-by-step explanation |

#### Criterion 3: Conclusion Validity (Weight: 0.30)
| Score | Description |
|-------|-------------|
| 5 | Conclusion strongly supported, considers alternatives |
| 4 | Well-supported conclusion |
| 3 | Adequately supported conclusion |
| 2 | Weakly supported conclusion |
| 1 | Unsupported or incorrect conclusion |
| 0 | No valid conclusion |

---

### Code Generation Scoring

#### Criterion 1: Correctness (Weight: 0.40)
| Score | Description |
|-------|-------------|
| 5 | Fully correct, handles edge cases, production-ready |
| 4 | Correct with minor issues or limited edge cases |
| 3 | Mostly correct, some bugs or limitations |
| 2 | Significant errors, partial implementation |
| 1 | Major errors, barely functional |
| 0 | Non-functional or completely incorrect |

#### Criterion 2: Code Quality (Weight: 0.30)
| Score | Description |
|-------|-------------|
| 5 | Clean, idiomatic, well-structured, documented |
| 4 | Good quality with minor improvements needed |
| 3 | Acceptable quality, some style issues |
| 2 | Poor quality, significant style/structure problems |
| 1 | Very poor quality, hard to read/maintain |
| 0 | Unusable code quality |

#### Criterion 3: Efficiency (Weight: 0.30)
| Score | Description |
|-------|-------------|
| 5 | Optimal algorithm, appropriate data structures |
| 4 | Efficient with minor optimization opportunities |
| 3 | Reasonably efficient |
| 2 | Inefficient approach |
| 1 | Very inefficient, poor algorithm choice |
| 0 | Completely inefficient approach |

---

### Creative Generation Scoring

#### Criterion 1: Originality (Weight: 0.35)
| Score | Description |
|-------|-------------|
| 5 | Highly original, unique perspectives or ideas |
| 4 | Creative with some novel elements |
| 3 | Moderately original, some freshness |
| 2 | Derivative, mostly common ideas |
| 1 | Very cliché or generic |
| 0 | No originality demonstrated |

#### Criterion 2: Relevance (Weight: 0.35)
| Score | Description |
|-------|-------------|
| 5 | Perfectly aligned with requirements and audience |
| 4 | Well-aligned with minor deviations |
| 3 | Generally meets requirements |
| 2 | Partially meets requirements |
| 1 | Barely relevant to requirements |
| 0 | Irrelevant to requirements |

#### Criterion 3: Quality (Weight: 0.30)
| Score | Description |
|-------|-------------|
| 5 | Polished, engaging, professional quality |
| 4 | Good quality with minor polish needed |
| 3 | Acceptable quality, some roughness |
| 2 | Poor quality, needs significant work |
| 1 | Very poor quality |
| 0 | Unacceptable quality |

---

### Tool Usage Scoring

#### Criterion 1: Tool Selection (Weight: 0.40)
| Score | Description |
|-------|-------------|
| 5 | Optimal tool choices for all tasks |
| 4 | Good tool choices with minor improvements possible |
| 3 | Adequate tool selection |
| 2 | Suboptimal tool choices |
| 1 | Poor tool choices |
| 0 | Inappropriate or no tools used |

#### Criterion 2: Parameter Configuration (Weight: 0.35)
| Score | Description |
|-------|-------------|
| 5 | Perfectly configured for optimal results |
| 4 | Well configured with minor adjustments needed |
| 3 | Adequately configured |
| 2 | Poorly configured, affects results |
| 1 | Very poor configuration |
| 0 | No meaningful configuration |

#### Criterion 3: Error Handling (Weight: 0.25)
| Score | Description |
|-------|-------------|
| 5 | Graceful handling of all errors with recovery |
| 4 | Good error handling with minor gaps |
| 3 | Basic error handling |
| 2 | Minimal error handling |
| 1 | Poor error handling |
| 0 | No error handling demonstrated |

---

### Memory & Context Scoring

#### Criterion 1: Retrieval Accuracy (Weight: 0.40)
| Score | Description |
|-------|-------------|
| 5 | Perfect retrieval of all relevant knowledge |
| 4 | Accurate retrieval with minor omissions |
| 3 | Mostly accurate retrieval |
| 2 | Partial retrieval with significant gaps |
| 1 | Minimal accurate retrieval |
| 0 | No relevant knowledge retrieved |

#### Criterion 2: Context Application (Weight: 0.35)
| Score | Description |
|-------|-------------|
| 5 | Perfectly applies context to all aspects |
| 4 | Well-applied context with minor gaps |
| 3 | Adequately applies context |
| 2 | Inconsistent context application |
| 1 | Minimal context application |
| 0 | No context applied |

#### Criterion 3: Knowledge Synthesis (Weight: 0.25)
| Score | Description |
|-------|-------------|
| 5 | Excellent synthesis of multiple knowledge sources |
| 4 | Good synthesis with minor integration issues |
| 3 | Adequate synthesis |
| 2 | Poor synthesis, disjointed knowledge use |
| 1 | Very poor synthesis |
| 0 | No synthesis demonstrated |

---

### Quality & Accuracy Scoring

#### Criterion 1: Factual Accuracy (Weight: 0.40)
| Score | Description |
|-------|-------------|
| 5 | Completely accurate, no factual errors |
| 4 | Accurate with minor factual issues |
| 3 | Generally accurate with some errors |
| 2 | Significant factual errors |
| 1 | Mostly inaccurate |
| 0 | Completely incorrect |

#### Criterion 2: Completeness (Weight: 0.35)
| Score | Description |
|-------|-------------|
| 5 | Complete response addressing all requirements |
| 4 | Mostly complete with minor omissions |
| 3 | Addresses main requirements with gaps |
| 2 | Incomplete with significant omissions |
| 1 | Very incomplete |
| 0 | No meaningful response |

#### Criterion 3: Consistency (Weight: 0.25)
| Score | Description |
|-------|-------------|
| 5 | Perfectly consistent throughout |
| 4 | Consistent with minor inconsistencies |
| 3 | Generally consistent |
| 2 | Some inconsistencies |
| 1 | Many inconsistencies |
| 0 | Completely inconsistent |

## Score Aggregation

### Question Score Formula

```
QuestionScore = Σ(CriterionScore × Weight) × 20
```

*Multiplied by 20 to scale to 0-100*

**Example**:
- Relevance: 4 × 0.35 = 1.4
- Completeness: 3 × 0.30 = 0.9
- Source Quality: 4 × 0.20 = 0.8
- Efficiency: 3 × 0.15 = 0.45
- Sum: 3.55 × 20 = **71/100**

### Dimension Score Formula

```
DimensionScore = Σ(QuestionScores) / NumberOfQuestions
```

**Example** (5 questions):
- Q1: 85, Q2: 72, Q3: 88, Q4: 65, Q5: 78
- Dimension Score: (85+72+88+65+78) / 5 = **77.6/100**

### Overall Score Formula

```
OverallScore = Σ(DimensionScore × DimensionWeight) / ΣWeights
```

With equal weights (0.125 each):
```
OverallScore = Average of all 8 dimension scores
```

## Benchmark Comparisons

### Population Percentiles

| Score | Percentile | Label |
|-------|------------|-------|
| 95+ | 99th | Exceptional |
| 90-94 | 95th | Excellent |
| 85-89 | 85th | Superior |
| 80-84 | 70th | Advanced |
| 75-79 | 55th | Proficient |
| 70-74 | 40th | Competent |
| 65-69 | 25th | Developing |
| 60-64 | 15th | Basic |
| <60 | <10th | Beginner |

### Dimension-Specific Benchmarks

```
Dimension           25th    50th    75th    90th
────────────────────────────────────────────────
Information          65      73      81      88
Content              64      72      80      87
Logical              60      70      79      85
Code                 52      66      76      84
Creative             58      71      80      86
Tools                66      74      82      89
Memory               59      69      78      85
Quality              67      75      83      90
```

## Improvement Calculation

### Session-to-Session Growth

```
Growth = CurrentScore - PreviousScore
GrowthPercent = (Growth / (100 - PreviousScore)) × 100
```

**Example**:
- Previous: 65
- Current: 78
- Growth: +13 points
- Growth Percent: 13/(100-65) = 37% of remaining potential

### Expected Growth Rates

| Time Period | Expected Growth |
|-------------|-----------------|
| 1 week (with practice) | +3-5 points |
| 1 month (focused) | +8-12 points |
| 3 months (consistent) | +15-20 points |

## Score Interpretation Guidelines

### When Scores Are Low (<60)

**Don't panic** - Low scores indicate learning opportunities, not failure.

1. **Identify the bottleneck**: Is it knowledge, skills, or practice?
2. **Focus on one dimension**: Don't try to improve everything at once
3. **Use practice mode**: Immediate feedback accelerates learning
4. **Install relevant skills**: Tools can boost specific dimensions

### When Scores Plateau (70-80 range)

**Common plateau causes**:
- Practicing same difficulty repeatedly
- Missing foundational knowledge
- Not using available tools effectively
- Inefficient workflows

**Break through by**:
- Increasing question difficulty
- Learning advanced tool combinations
- Studying high-scoring examples
- Seeking community feedback

### When Scores Are High (85+)

**Maintenance and growth**:
- Explore advanced questions
- Help others (teaching reinforces learning)
- Contribute to question bank
- Focus on edge cases and optimization

## Automated vs. Human Scoring

### Fully Automated Criteria
- Code correctness (syntax tests, unit tests)
- Factual accuracy (knowledge base verification)
- Completeness (requirement checklist)
- Consistency (internal validation)

### Human-Augmented Criteria
- Originality (requires judgment)
- Insight quality (contextual)
- Code quality (style, maintainability)
- Creative quality (subjective elements)

### Hybrid Approach
1. Auto-score all criteria
2. Flag low-confidence scores for review
3. Human validates borderline cases
4. Continuous training of auto-scorer
