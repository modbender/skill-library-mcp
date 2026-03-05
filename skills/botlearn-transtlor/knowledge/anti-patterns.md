---
domain: translator
topic: anti-patterns
priority: medium
ttl: 30d
---

# Translation — Anti-Patterns

## Literal Translation Anti-Patterns

### 1. Word-for-Word Rendering
- **Problem**: Translating each word in sequence without considering target-language syntax, resulting in unnatural, confusing, or grammatically incorrect output
- **Example**: "I look forward to hearing from you" --> (DE literal) "Ich schaue vorwärts zu hören von Ihnen" (nonsensical)
- **Fix**: Restructure for target-language idiom: "Ich freue mich auf Ihre Rückmeldung" (standard German business closing)

### 2. Calque / Loan Translation
- **Problem**: Translating a multi-word expression component by component, creating a non-existent phrase in the target language
- **Example**: "skyscraper" --> (ES calque) "rascador de cielos" instead of the accepted "rascacielos"
- **Example**: "cloud computing" --> (ZH calque) "云计算" (this one happens to be correct, but "hot dog" --> "热狗" works only because it has been adopted)
- **Fix**: Check whether the target language has an established equivalent; do not invent compound translations

### 3. Source-Language Syntax Imposition
- **Problem**: Forcing source-language word order onto the target language
- **Example (EN --> JA)**: Keeping SVO order in Japanese instead of restructuring to SOV
  - Wrong: "I ate sushi" --> "私は食べた寿司を" (unnatural order)
  - Correct: "私は寿司を食べた" (natural SOV)
- **Fix**: Parse meaning units from the source, then reconstruct using natural target-language syntax

### 4. False Friend Traps
- **Problem**: Translating a word that looks similar in the target language but has a different meaning
- **Example**: "actually" --> (FR) "actuellement" (means "currently", not "actually")
- **Example**: "sensible" --> (ES) "sensible" (means "sensitive", not "sensible")
- **Fix**: Maintain awareness of common false friends for each language pair; verify meaning, not just form

## Register and Tone Anti-Patterns

### 5. Register Mismatch
- **Problem**: Translating formal text into informal language or vice versa, destroying the communicative intent
- **Example**: A legal contract translated into casual conversational tone — "The parties hereto agree" --> "So basically both sides are cool with this"
- **Example**: A chatbot greeting translated into stiff formal prose — "Hey, what's up?" --> "Greetings, esteemed interlocutor. How may I be of service?"
- **Fix**: Identify the source register first; map it to the equivalent register in the target language using knowledge/domain.md register tables

### 6. Honorific Level Errors
- **Problem**: Using the wrong level of formality in languages with grammaticalized politeness (Japanese keigo, Korean speech levels, German Sie/du)
- **Example (EN --> JA)**: Using casual plain form (だ/る) in a business email instead of keigo (です/ます or 尊敬語)
- **Example (EN --> DE)**: Using "du" with a business client who expects "Sie"
- **Fix**: Determine the social relationship between speaker and audience; select the appropriate honorific level; maintain it consistently

### 7. Tone Flattening
- **Problem**: Producing a translation that is technically accurate but emotionally flat, losing the urgency, humor, warmth, or persuasion of the original
- **Example**: "Don't miss out on this incredible deal!" --> (ZH flat) "不要错过这个交易" (accurate but lacks excitement)
- **Better**: "千载难逢的超值优惠，不容错过！" (preserves urgency and excitement)
- **Fix**: Identify the emotional function of the source text; use target-language devices (exclamations, rhythm, word choice) to recreate the same emotional response

## Cultural Blindness Anti-Patterns

### 8. Untranslated Cultural References
- **Problem**: Leaving culture-specific references that the target audience will not understand
- **Example**: "It was a real Groundhog Day situation" --> translating literally for an audience unfamiliar with the American film/tradition
- **Fix**: Replace with a target-culture equivalent or add a brief explanatory gloss; for widely known references, transliterate and add context on first use

### 9. Culturally Inappropriate Content
- **Problem**: Translating content that is acceptable in the source culture but offensive or inappropriate in the target culture
- **Example**: Humor involving alcohol in translations for markets where alcohol references are restricted; color symbolism (white = mourning in some East Asian cultures vs. purity in Western cultures)
- **Fix**: Flag culturally sensitive content; adapt or add translator notes; consult target-culture conventions for the specific domain

### 10. Date, Number, and Unit Blindness
- **Problem**: Keeping source-locale formatting for dates, numbers, currencies, and measurements without converting to target-locale conventions
- **Example**: "The meeting is on 03/04/2025" — is this March 4 (US) or April 3 (EU)? Ambiguity passed through to the target
- **Example**: "The package weighs 5 lbs" left unconverted for a metric-system audience
- **Fix**: Convert all locale-dependent formats to target conventions; resolve ambiguous dates; convert units when the target audience uses a different system

## Consistency Anti-Patterns

### 11. Terminology Drift
- **Problem**: Translating the same source term differently across a document without justification, confusing the reader
- **Example**: "endpoint" translated as "端点" in paragraph 1, "终结点" in paragraph 5, and "接入点" in paragraph 10
- **Fix**: Build and maintain a session glossary (see best-practices.md); search-and-verify terminology before finalizing; one term = one translation unless context clearly requires a different rendering

### 12. Style Inconsistency
- **Problem**: Mixing formal and informal styles within a single document, or alternating between translation strategies mid-text
- **Example**: Technical documentation that starts with precise formal language but drifts into casual phrasing after several pages
- **Fix**: Establish the target style at the start of the session; reference it throughout; perform a consistency pass after completing the draft

## Omission and Addition Anti-Patterns

### 13. Silent Omission
- **Problem**: Dropping source-text content without annotation — sentences, clauses, or nuances that are difficult to translate are simply left out
- **Example**: Omitting a parenthetical qualifier because it is hard to render naturally in the target language
- **Fix**: Translate everything; if a segment is genuinely untranslatable, provide a translator note explaining the omission and offering the closest approximation

### 14. Unauthorized Addition
- **Problem**: Adding information, opinions, or clarifications that are not present in the source text without marking them as translator additions
- **Example**: The source says "sales increased" and the translation adds "sales increased significantly" for stylistic reasons
- **Fix**: Translate only what is in the source; if clarification is needed for the target audience, mark it explicitly as a translator note: [TN: ...]

## Technical Anti-Patterns

### 15. Broken Placeholders and Markup
- **Problem**: Translating, modifying, or deleting placeholder variables, HTML tags, or markup syntax within the text
- **Example**: `"Welcome, {username}!"` --> `"欢迎，{用户名}！"` (placeholder translated, will break the application)
- **Fix**: Identify all placeholders, tags, and markup before translating; preserve them exactly; only translate the natural-language text surrounding them

### 16. Ignoring String Length Constraints
- **Problem**: Producing translations that are too long for UI elements (buttons, tooltips, menu items) without warning
- **Example**: EN button "Submit" (6 chars) --> DE "Einreichen" (10 chars) or FR "Soumettre" (9 chars) — may overflow the button
- **Fix**: Check expansion/contraction rates from knowledge/domain.md; flag translations that exceed typical length budgets; offer abbreviated alternatives
