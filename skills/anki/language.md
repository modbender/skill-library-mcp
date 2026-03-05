# Language Learning with Anki

## Vocabulary Card Template

**Minimum fields:**
- Word (target language)
- Translation/meaning
- Example sentence
- Audio (if available)

**Recommended additions:**
- IPA/pronunciation guide
- Part of speech
- Gender/plural (for gendered languages)
- Frequency level (A1-C2)
- Collocations

## Audio Integration

**Sources:**
- Forvo (human pronunciation, multiple accents)
- Google TTS (robotic but consistent)
- Native speaker recordings (best quality)

**Auto-generation:**
- AwesomeTTS add-on integrates multiple TTS services
- Download once, embed in card

**Trap:** Don't rely on audio alone. Visual recognition matters too.

## Sentence Cards vs Word Cards

**Word cards (isolated vocabulary):**
- ✅ Fast to create
- ✅ Good for recognition
- ❌ No context = poor production
- ❌ Interference between similar words

**Sentence cards (word in context):**
- ✅ Shows real usage
- ✅ Tests comprehension
- ❌ Slower to create
- ❌ Might pass by understanding context, not word

**Best approach:** Start with word + example sentence. Add sentence cards for confusing words.

## Cloze for Languages

**Good uses:**
```
Ich {{c1::fahre}} mit dem Bus. (I go/drive by bus)
El libro está {{c1::sobre}} la mesa. (The book is on the table)
```

**Bad uses:**
```
{{c1::Je m'appelle Marie.}} (entire sentence — tests nothing specific)
J'{{c1::ai}} {{c2::mangé}}. (multiple clozes testing different things)
```

## Conjugation Tables

**Don't make one card per conjugation.** Instead:

1. **Pattern recognition cards:**
   - "What's the present tense ending for -AR verbs, yo?" → `-o`
   
2. **High-frequency forms:**
   - Only conjugations you'll actually use
   - "How do you say 'I went' in Spanish?" → `Fui`

3. **Reference table (on back):**
   - Show full table but test individual forms

## False Friends

Cards that explicitly contrast confusing pairs:

```
Front: [ES→EN] "Embarazada" means...
Back: Pregnant (NOT embarrassed — that's "avergonzada")
```

```
Front: [Warning] "Actualmente" in Spanish means...
Back: Currently (NOT "actually" — that's "en realidad")
```

## Frequency-Based Learning

**Priority order:**
1. Top 1000 words (covers 85% of daily speech)
2. Top 3000 words (covers 95%)
3. Domain-specific vocabulary

**Tag by frequency:** `#A1`, `#A2`, `#B1`, `#B2`, `#C1`

**Study order:** Learn high-frequency first. Don't waste time on rare words early.

## Bidirectional Cards

**Recognition (L2→L1):** See target language, recall meaning
**Production (L1→L2):** See native language, produce target

**Both are necessary but different skills.**

**Tip:** Make production cards slightly easier:
- Include first letter hint
- Show related words
- Accept synonyms as correct

## Regional Variations

Track when words differ by region:
```
Front: How do you say "car" in Spanish?
Back: Coche (Spain) / Carro (Latin America) / Auto (Argentina)
```

Or use tags: `#spain`, `#latam`, `#neutral`

## Common Mistakes to Prevent

- **Misspelled cards** — Check source before adding
- **Translation without context** — "Run" has 20 meanings
- **Ignoring pronunciation** — Add audio or IPA
- **Skipping gender** — "El problema" (masc) not "la problema"
- **Lists as cards** — "Days of the week" should be 7 cards
- **Only recognition** — Test production too
