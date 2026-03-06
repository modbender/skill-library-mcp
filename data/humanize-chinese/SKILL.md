---
name: humanize-chinese
description: Detect and humanize AI-generated Chinese text with 6 style transforms (casual/zhihu/xiaohongshu/wechat/academic/literary). Removes "AI flavor" using 16 detection patterns. Pure Python, no dependencies. v1.1.0
allowed-tools:
  - Read
  - Write
  - Edit
  - exec
---

# Humanize Chinese AI Text

Comprehensive CLI for detecting and transforming Chinese AI-generated text. Makes robotic AI writing natural and human-like with 6 specialized writing style transforms.

**NEW in v1.1:** Style transforms (知乎/小红书/公众号/口语化/学术/文艺), enhanced detection (16 patterns), emotional analysis

## Quick Start

```bash
# Detect AI patterns (16 categories)
python scripts/detect_cn.py text.txt

# Humanize text
python scripts/humanize_cn.py text.txt -o clean.txt

# Scene-specific humanization
python scripts/humanize_cn.py text.txt --scene social  # Social media
python scripts/humanize_cn.py text.txt --scene tech    # Tech blog
python scripts/humanize_cn.py text.txt --scene formal  # Formal article

# NEW: Apply writing styles
python scripts/humanize_cn.py text.txt --style zhihu -o zhihu.txt
python scripts/humanize_cn.py text.txt --style xiaohongshu -o xhs.txt
python scripts/style_cn.py text.txt --style casual -o casual.txt

# List all available styles
python scripts/style_cn.py --list

# Compare before/after
python scripts/compare_cn.py text.txt -o clean.txt
```

---

## Detection Categories

The analyzer checks for **16 pattern categories** specific to Chinese AI text (v1.1 added 4 new patterns):

### Critical (Immediate AI Detection)
| Category | Examples |
|----------|----------|
| Three-Part Structure | 首先...其次...最后, 一方面...另一方面 |
| Mechanical Connectors | 值得注意的是, 综上所述, 不难发现 |
| Empty Grand Words | 赋能, 闭环, 智慧时代, 数字化转型 |

### High Signal
| Category | Examples |
|----------|----------|
| AI High-Frequency Words | 助力, 彰显, 凸显, 焕发, 深度剖析 |
| Technical Jargon Misuse | 解构, 量子纠缠, 光谱 (in non-tech context) |
| Excessive Rhetoric | 对偶句 (>2x), 排比句 (>1x), 引用句 (>4x) |

### Medium Signal
| Category | Examples |
|----------|----------|
| Punctuation Overuse | Dense em dashes, excessive semicolons |
| Obscure Metaphors | Forced, disconnected comparisons |
| Uniform Paragraphs | Equal-length paragraphs (no rhythm) |

### Style Signal
| Category | Examples |
|----------|----------|
| Low Burstiness | Monotonous sentence structure |
| Low Perplexity | Predictable word choices |
| Emotional Flatness | **NEW** Lack of emotional words and expressions |
| Repetitive Structure | **NEW** Sentence starters repeat >3 times |
| Slang Overuse | **NEW** Internet slang in formal context |
| Vocabulary Homogeneity | **NEW** Low diversity in word choice |

---

## Writing Style Transforms (NEW in v1.1)

Transform text into 6 specialized Chinese writing styles:

| Style | Name | Description | Best For |
|-------|------|-------------|----------|
| `casual` | 口语化风格 | Like chatting with friends — natural, relaxed | Social media, messaging |
| `zhihu` | 知乎风格 | Rational, in-depth, with personal opinions | Q&A platforms, thoughtful analysis |
| `xiaohongshu` | 小红书风格 | Enthusiastic, emoji-rich, product-focused | Lifestyle sharing, reviews, recommendations |
| `wechat` | 公众号风格 | Storytelling, engaging, relatable | WeChat articles, newsletters |
| `academic` | 学术风格 | Rigorous but not stiff, precise terminology | Academic papers, research reports |
| `literary` | 文艺风格 | Poetic, imagery-rich, metaphorical | Creative writing, essays |

### Usage

```bash
# Apply style directly
python scripts/style_cn.py input.txt --style zhihu -o output.txt

# Combine humanization + style
python scripts/humanize_cn.py ai_text.txt --style xiaohongshu -o natural.txt

# List all styles
python scripts/style_cn.py --list
```

### Style Features

#### Casual (口语化)
- Removes formal structure (首先/其次/最后)
- Adds colloquial connectors (说实话, 确实, 其实)
- Includes tone particles (吧, 呢, 啊)
- Light emoji usage

#### Zhihu (知乎)
- Personal opinion markers (从我的经验来看, 个人认为)
- Data/evidence support (实测发现, 根据XX调研)
- Example-driven (举个例子)
- Logical but conversational

#### Xiaohongshu (小红书)
- Enthusiastic openers (姐妹们！分享一下～)
- High emoji density (😊✨💯)
- Intensifiers (超级, 巨, 绝绝子, yyds)
- Hashtags (#好物分享)
- Short paragraphs

#### Wechat (公众号)
- Story-driven openings
- Questions for engagement (你有没有想过)
- Relatable scenarios
- Emotional connection

#### Academic (学术)
- Removes colloquialisms
- Precise terminology
- Formal connectors (研究表明, 数据显示)
- Reduces emotional expressions

#### Literary (文艺)
- Metaphors and imagery
- Poetic language
- Descriptive phrases (在XX的光影里)
- Artistic expressions

---

## Scripts

### detect_cn.py — Scan Chinese AI Patterns

```bash
python scripts/detect_cn.py essay.txt
python scripts/detect_cn.py essay.txt -j  # JSON output
python scripts/detect_cn.py essay.txt -s  # score only
echo "文本" | python scripts/detect_cn.py
```

**Output:**
- AI feature statistics (by category)
- AI probability score (low/medium/high/very high)
- Auto-fixable patterns marked
- Perplexity and burstiness indicators

### humanize_cn.py — Transform to Human-Like

```bash
python scripts/humanize_cn.py essay.txt
python scripts/humanize_cn.py essay.txt -o output.txt
python scripts/humanize_cn.py essay.txt --scene social  # Social media style
python scripts/humanize_cn.py essay.txt -a              # Aggressive mode
```

**Scene Parameters (--scene):**
- `social`: Social media (casual, conversational)
- `tech`: Tech blog (professional but approachable)
- `formal`: Formal article (rigorous but natural)
- `chat`: Chat/dialogue (friendly, concise)

**Auto-fixes:**
- Remove three-part structure (首先/其次/最后)
- Replace mechanical connectors (值得注意的是 → 注意/要提醒的是)
- Simplify empty words (赋能 → 帮助/提升, 闭环 → 完整流程)
- Reduce punctuation density (em dash, semicolon)
- Control rhetoric frequency (对偶, 排比, 比喻)

**Aggressive Mode (-a):**
- Add colloquial expressions
- Inject emotional color
- Vary sentence rhythm
- Add personal perspective

### compare_cn.py — Before/After Analysis

```bash
python scripts/compare_cn.py essay.txt
python scripts/compare_cn.py essay.txt --scene tech -o clean.txt
```

Shows AI feature comparison and score changes before/after transformation.

### style_cn.py — Writing Style Transform (NEW)

```bash
python scripts/style_cn.py essay.txt --style zhihu -o essay_zhihu.txt
python scripts/style_cn.py blog.txt --style xiaohongshu -o blog_xhs.txt
python scripts/style_cn.py --list  # Show all available styles
```

**Supported styles:** casual, zhihu, xiaohongshu, wechat, academic, literary

Transform text into specific Chinese writing styles with style-appropriate vocabulary, tone, and structure.

---

## Workflow

1. **Scan** for detection risk:
   ```bash
   python scripts/detect_cn.py document.txt
   ```

2. **Transform** with comparison:
   ```bash
   python scripts/compare_cn.py document.txt --scene tech -o document_v2.txt
   ```

3. **Verify** improvement:
   ```bash
   python scripts/detect_cn.py document_v2.txt -s
   ```

4. **Manual review** for content quality and scene appropriateness

---

## AI Probability Scoring

| Rating | Criteria |
|--------|----------|
| Very High | Three-part structure, mechanical connectors, or empty grand words present |
| High | >20 issues OR issue density >3% |
| Medium | >10 issues OR issue density >1.5% |
| Low | <10 issues AND density <1.5% |

---

## Scene-Specific Guidelines

### Social Media (社交媒体)
**Style:** Casual, conversational, like chatting with friends
- ✅ Short paragraphs (1-3 sentences)
- ✅ Colloquial expressions (说实话, 没想到, 真的绝了)
- ✅ Specific details (product names, locations, personal feelings)
- ✅ Emoji and hashtags
- ❌ Avoid: 值得注意的是, 总而言之
- ❌ Avoid: Long paragraphs, complex sentences

### Tech Blog (技术博客)
**Style:** Professional but approachable, can be humorous
- ✅ Specific tech stack, tool names
- ✅ Code examples, performance data
- ✅ Real experiences ("踩过的坑", "实测效果")
- ✅ Clear structure with headings (not numbered lists)
- ❌ Avoid: 赋能, 闭环, 生态
- ❌ Avoid: 首先/其次/最后structure

### Formal Article (正式文章)
**Style:** Objective, rigorous, but natural
- ✅ Clear logic with proper evidence
- ✅ Precise academic expressions
- ✅ Cited research sources
- ✅ Data and charts supporting arguments
- ❌ Avoid: Excessive rhetoric (对偶, 排比)
- ❌ Avoid: Empty grand words

### Chat/Dialogue (对话场景)
**Style:** Friendly, patient, genuine
- ✅ Concise, targeted responses
- ✅ Empathy and understanding
- ✅ Direct solutions
- ✅ Moderate emoji use
- ❌ Avoid: 很高兴为您服务 (template phrases)
- ❌ Avoid: Lengthy explanations, repetitive questions

---

## Customizing Patterns

Edit `scripts/patterns_cn.json` to add/modify:
- `ai_vocabulary_cn` — Chinese AI high-frequency words
- `filler_phrases_cn` — Clichés and replacements
- `empty_words_cn` — Empty grand vocabulary
- `rhetoric_limits` — Rhetoric frequency limits
- `scene_styles` — Scene-specific style configs

---

## Batch Processing

```bash
# Scan all files
for f in *.txt; do
  echo "=== $f ==="
  python scripts/detect_cn.py "$f" -s
done

# Transform all markdown (tech blog style)
for f in *.md; do
  python scripts/humanize_cn.py "$f" --scene tech -o "${f%.md}_clean.md"
done
```

---

## Reference

Based on comprehensive Chinese AI writing research:
- Tencent News: "Deconstructing 'AI Flavor': Why We Dislike AI Writing"
- 53AI: "Detection and Optimization of Article 'AI Flavor'"
- AIGCleaner and other Chinese de-AI tools
- Wikipedia: "Signs of AI Writing" (English reference)

Key insights:
- **Perplexity**: AI text has low perplexity (predictable word choices)
- **Burstiness**: AI text has low burstiness (uniform sentence structure)
- **Emotion**: AI text lacks strong opinions and personal color
