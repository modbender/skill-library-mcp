---
domain: translator
topic: translation-quality-and-consistency
priority: high
ttl: 30d
---

# Translation — Best Practices

## Context-First Translation

### 1. Understand Before Translating
Before translating a single word, establish full context:
- **Purpose**: Why was this text written? What action should the reader take?
- **Audience**: Who will read the translation? What is their expertise level?
- **Medium**: Where will this translation appear? (UI, document, speech, legal filing)
- **Tone**: What is the emotional register? (authoritative, friendly, urgent, neutral)
- **Constraints**: Are there length limits, formatting requirements, or platform restrictions?

### 2. Read the Entire Source First
- Never translate sentence-by-sentence in isolation — read the full text to understand:
  - Recurring themes and terminology
  - Internal cross-references ("as mentioned above", "see Section 3")
  - Tone shifts and rhetorical structure
  - Key terms that require consistent rendering
- For long documents, skim the full text, then translate section by section

### 3. Identify the Text Type
Map the source text to a translation strategy:

| Text Type | Strategy | Priority |
|-----------|----------|----------|
| Informative (reports, manuals) | Accuracy > Style | Terminology precision |
| Expressive (literature, poetry) | Style > Literal accuracy | Voice and aesthetic |
| Operative (ads, instructions, CTAs) | Effect > Form | Reader action and persuasion |
| Legal / Regulatory | Precision + Convention | Jurisdiction-appropriate terms |
| User Interface | Brevity + Clarity | Space constraints and usability |

## Terminology Consistency

### 4. Build a Session Glossary
For every translation session, maintain a running glossary:

```
| Source Term | Target Term | Domain | Notes |
|-------------|-------------|--------|-------|
| machine learning | 机器学习 | tech | Standard; do not use 自动学习 |
| compliance | 合规 | legal/finance | Not 遵守 in regulatory context |
| endpoint | 端点 | API/tech | Not 终端 (which means terminal) |
```

Rules for glossary management:
- **One source term = one target term** within a single document (unless context demands otherwise)
- Record the decision and rationale for non-obvious choices
- When the client provides a glossary or style guide, it overrides default choices
- Flag any source terms with multiple valid translations and select based on context

### 5. Handle Terminology Conflicts
When a source term has multiple valid translations:
1. Check if the client has a preferred glossary or translation memory
2. Examine how the term is used in context (noun vs verb, technical vs general)
3. Select the rendering that best fits the document's domain and register
4. Document the choice and apply it consistently
5. Provide a translator note if the choice is non-obvious

### 6. Preserve Named Entities Correctly
- **Brand names**: Keep in source language unless an official localized name exists (e.g., "Microsoft" stays; "Volkswagen" may become "大众" in Chinese consumer contexts)
- **Personal names**: Transliterate according to target-language convention (e.g., "Elon Musk" --> "埃隆·马斯克" in Chinese)
- **Place names**: Use the official target-language name (e.g., "Germany" --> "Allemagne" in French, "ドイツ" in Japanese)
- **Product names**: Follow the company's official localization; if none exists, keep the source name

## Quality Assurance

### 7. Self-Review Checklist
After completing a translation, verify:

- [ ] **Completeness**: Every source sentence has a corresponding target sentence; nothing omitted or added
- [ ] **Accuracy**: Factual content, numbers, dates, names are preserved without error
- [ ] **Terminology**: Glossary terms are applied consistently throughout
- [ ] **Register**: Formality level matches the source and is appropriate for the target audience
- [ ] **Grammar**: Target text follows target-language grammar rules natively
- [ ] **Fluency**: Text reads as if originally written in the target language
- [ ] **Cultural fit**: Idioms, metaphors, humor adapted appropriately; no cultural offense
- [ ] **Formatting**: Punctuation, number formats, date formats follow target-locale conventions
- [ ] **Placeholders**: All variables, tags, and placeholders preserved intact

### 8. Back-Translation Verification
For critical translations (legal, medical, safety):
- Mentally back-translate the target text into the source language
- If the back-translation diverges from the original meaning, revise the target text
- This catches semantic drift that may not be obvious reading only the target

### 9. Locale-Specific Formatting

| Element | EN (US) | ZH (CN) | DE | JA | ES |
|---------|---------|---------|----|----|-----|
| Decimal | 1,234.56 | 1,234.56 | 1.234,56 | 1,234.56 | 1.234,56 |
| Date | MM/DD/YYYY | YYYY年MM月DD日 | DD.MM.YYYY | YYYY年MM月DD日 | DD/MM/YYYY |
| Quotes | "text" | "text" or "text" | „text" | 「text」 | "text" or <<text>> |
| List separator | , (comma) | 、(enumeration comma) | , (comma) | 、(toten) | , (comma) |
| Honorific | Mr./Ms. | 先生/女士 | Herr/Frau | 様/さん | Sr./Sra. |

## Handling Ambiguity

### 10. Translate Ambiguity Transparently
When the source text is ambiguous:
- **Do not silently resolve ambiguity** — the translator should not assume meaning the author did not specify
- Provide the most likely translation with a translator note explaining the ambiguity
- Offer an alternative rendering if the other interpretation is plausible
- Format: `[Translation] (TN: The source "X" could also mean "Y"; translated as "Z" based on context)`

### 11. Manage Untranslatable Concepts
Some concepts lack a direct equivalent in the target language:
- **Cultural concepts**: Use a brief explanatory phrase + the original term in parentheses
  - Example: "hygge" --> "温馨惬意的氛围 (丹麦语: hygge)"
- **Technical neologisms**: Transliterate + explain on first use, then use the transliteration alone
  - Example: "blockchain" --> "区块链 (blockchain)" on first mention, "区块链" thereafter
- **Wordplay / Puns**: Explain the original wordplay in a note; create target-language wordplay if possible

## Handling Multi-Segment and Structured Content

### 12. Preserve Document Structure
- Maintain heading hierarchy, bullet points, numbering, and paragraph breaks
- Translate table headers and cell content while preserving table structure
- Keep code blocks, URLs, and file paths untranslated unless they contain user-facing strings
- Preserve Markdown, HTML, or other markup formatting intact
