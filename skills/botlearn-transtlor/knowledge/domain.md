---
domain: translator
topic: translation-theory-and-language-patterns
priority: high
ttl: 30d
---

# Translation — Theory, Equivalence Models & Language-Pair Patterns

## Core Translation Theory

### Formal vs. Dynamic Equivalence (Eugene Nida)

Translation strategies exist on a spectrum between two poles:

#### Formal Equivalence (Source-Oriented)
- Preserves the **form and structure** of the source language as closely as possible
- Maintains source-language word order, sentence structure, and idiom patterns
- Best for: legal contracts, religious texts, academic citations, patent filings, regulatory documents
- Trade-off: May sound unnatural in the target language; reader must bridge cultural gaps
- Example: "It is raining cats and dogs" --> (Chinese formal) "正在下猫和狗" (nonsensical but structurally faithful)

#### Dynamic Equivalence (Reader-Oriented)
- Preserves the **meaning and effect** on the reader rather than the form
- Restructures grammar, replaces idioms, adapts cultural references for the target audience
- Best for: marketing copy, user interfaces, creative content, conversational text, documentation
- Trade-off: May deviate from source structure; harder to back-translate
- Example: "It is raining cats and dogs" --> (Chinese dynamic) "倾盆大雨" (equivalent idiom conveying the same meaning)

#### Selecting the Right Approach

| Text Type | Recommended Approach | Rationale |
|-----------|---------------------|-----------|
| Legal / Regulatory | Formal (80-90%) | Precision and traceability required |
| Technical documentation | Formal-leaning (70%) | Accuracy critical, but readability matters |
| UI / UX strings | Dynamic (80-90%) | User experience and brevity paramount |
| Marketing / Advertising | Dynamic (90%+) | Emotional impact and cultural resonance |
| Literary / Creative | Dynamic with formal anchors | Artistry must translate, not just words |
| Academic / Scientific | Formal (75%) | Terminology precision, citation fidelity |
| Conversational / Chat | Dynamic (85%+) | Naturalness and tone are primary goals |

### Skopos Theory (Hans Vermeer)
- The **purpose (skopos)** of the translation determines the method
- A single source text may yield different translations depending on the target function
- Always ask: What is this translation **for**? Who is the **audience**?

### Relevance Theory (Gutt)
- Maximize **contextual effects** while minimizing **processing effort** for the reader
- If a literal translation requires excessive cognitive effort, restructure for clarity
- The best translation is one the reader processes as naturally as a native text

## Register and Formality

### Register Dimensions

| Dimension | Range | Examples |
|-----------|-------|---------|
| Formality | Frozen --> Intimate | Legal boilerplate --> Text message slang |
| Domain | General --> Specialized | Everyday vocabulary --> Medical terminology |
| Mode | Written --> Spoken | Academic paper --> Podcast transcript |
| Tenor | Impersonal --> Personal | Government notice --> Personal letter |

### Register Mapping Across Languages

#### English --> Chinese Register Signals
- Frozen/Formal: 使用书面语、四字成语、被动语态、"之"/"其"等文言助词
- Neutral: 标准普通话、完整句式、适度使用口语词
- Informal/Casual: 口语化表达、语气词（"啊"、"嘛"、"呢"）、省略主语

#### English --> Japanese Register Signals
- Frozen/Formal: 敬語体系 (keigo) — 尊敬語 + 謙譲語, である調
- Neutral: ですます調 (desu/masu form)
- Informal/Casual: 普通体 (plain form), タメ口, 省略表現

#### English --> Spanish Register Signals
- Frozen/Formal: Subjunctive mood, usted/ustedes, passive se, nominal style
- Neutral: Standard indicative, balanced tu/usted depending on regional norm
- Informal/Casual: Tuteo, colloquialisms, abbreviated forms, regional slang

#### English --> German Register Signals
- Frozen/Formal: Sie-Form, Konjunktiv II, nominalization, complex compound sentences
- Neutral: Standard Hochdeutsch, mixed Sie/du depending on context
- Informal/Casual: du-Form, particles (ja, doch, mal, halt), shortened forms

#### English --> French Register Signals
- Frozen/Formal: Vous-Form, passé simple, subjunctive, ne...pas (full negation)
- Neutral: Standard French, passé composé, vous in professional contexts
- Informal/Casual: Tu-Form, dropped ne in negation, verlan, abbreviations

## Technical Terminology Domains

### Legal Translation
- Key concepts: jurisdiction-specific terms, Latin maxims, defined terms, operative clauses
- Pattern: Maintain defined terms exactly as established in the Definitions section
- Caution: Legal terms often have no direct equivalent — use the accepted target-language legal term, not a dictionary translation
- Examples: "force majeure" (keep in French across languages), "consideration" (legal) != "consideration" (general)

### Medical Translation
- Key concepts: ICD codes, drug nomenclature (INN vs brand), anatomical terminology, dosage instructions
- Pattern: Use INN (International Nonproprietary Name) for drugs unless targeting a consumer audience
- Caution: Dosage units, measurement systems, and date formats vary by locale
- Examples: "paracetamol" (INN/UK) = "acetaminophen" (US) = "对乙酰氨基酚" (Chinese INN)

### Software / Technical Translation
- Key concepts: UI strings, API documentation, error messages, variable interpolation
- Pattern: Preserve placeholders ({0}, %s, {{name}}) exactly; translate surrounding text only
- Caution: String length constraints for UI; right-to-left language layout implications
- Examples: "Click {button_name} to continue" --> "点击{button_name}继续" (placeholder preserved)

### Financial Translation
- Key concepts: IFRS vs GAAP terminology, currency formatting, regulatory terms
- Pattern: Use target-locale number formatting (1,000.00 vs 1.000,00) and currency symbols
- Caution: Financial instrument names may differ by regulatory jurisdiction

### Scientific Translation
- Key concepts: SI units, chemical nomenclature (IUPAC), species names (binomial Latin), statistical terms
- Pattern: Keep species names in Latin; translate common names; preserve formulas and equations
- Caution: Unit conversions may be needed for US audiences (metric --> imperial)

## Language-Pair Specific Patterns

### Structural Divergences

| Pattern | Example Languages | Translation Strategy |
|---------|------------------|---------------------|
| SVO --> SOV word order | English --> Japanese, Korean, Hindi | Restructure entire sentence; translate meaning units, not word order |
| Article systems | English --> Chinese, Japanese, Russian | Drop articles; use context, classifiers, or demonstratives for specificity |
| Grammatical gender | English --> French, German, Spanish | Assign gender based on target-language noun; adjust all agreeing elements |
| Tense systems | English --> Chinese | Use temporal adverbs and aspect markers (了/过/着) instead of verb conjugation |
| Honorific systems | English --> Japanese, Korean | Determine social relationship; select appropriate honorific level throughout |
| Pro-drop | English --> Spanish, Italian, Chinese | Omit subject pronouns where target language allows and context is clear |

### Common False Friends

| English | Looks Like (Language) | Actually Means |
|---------|----------------------|----------------|
| "actually" | "actuellement" (FR) | FR means "currently" |
| "sensible" | "sensible" (ES/FR) | ES/FR means "sensitive" |
| "gift" | "Gift" (DE) | DE means "poison" |
| "embarrassed" | "embarazada" (ES) | ES means "pregnant" |
| "preservative" | "preservativo" (ES/IT) | ES/IT means "condom" |
| "sympathetic" | "sympathique" (FR) | FR means "likeable/nice" |

### Expansion and Contraction Rates

Translation length varies by language pair, critical for UI and layout constraints:

| Source --> Target | Typical Length Change |
|------------------|---------------------|
| English --> German | +20-35% expansion |
| English --> French | +15-25% expansion |
| English --> Spanish | +15-25% expansion |
| English --> Chinese | -30-50% contraction (characters) |
| English --> Japanese | -20-40% contraction (mixed script) |
| English --> Arabic | +20-25% expansion |
| English --> Korean | -10-20% contraction |
| English --> Russian | +15-25% expansion |
