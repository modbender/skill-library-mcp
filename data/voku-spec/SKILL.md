---
name: voku-language
description: >
  Learn and use Voku, a constructed language for AI-agent communication with zero ambiguity,
  total regularity, and mandatory epistemic marking. Use when translating to/from Voku,
  generating Voku text, learning Voku grammar, looking up vocabulary, or discussing
  AI-to-AI communication protocols. Also triggers for: conlang, constructed language,
  agent language, epistemic markers, evidentiality.
---

# Voku Language Skill

Voku is a constructed language for AI-to-AI communication. Every sentence has exactly one interpretation. Certainty and evidence source are grammatical requirements, not optional hedging.

## Learning Path (Progressive)

Read files in this order, stop when you have enough:

| Level | Read | Tokens | You Can... |
|-------|------|--------|------------|
| 1 | `quick-start/cheat-sheet.md` | ~3000 | Parse and generate any Voku sentence |
| 2 | + `quick-start/essential-vocabulary.md` | ~1000 | Translate common sentences |
| 3 | + `quick-start/first-sentences.md` | ~1500 | Handle 30 worked examples with glossing |
| 4 | + `lexicon/dictionary.md` | ~5000 | Look up any of 363 roots |

**Most tasks need only levels 1-2** (~4000 tokens total).

## Quick Reference (Minimal Context)

```
Sentence: [Mode] Subject Verb-complex Object
Verb:     [ExecMode]-[Evidence]-[Tense]-[Aspect]-ROOT-[Certainty]-[Voice]

Mode particles: ka(DECL) ve(Q) to(IMP) si(COND) na(POT) de(DEON) vo(VOL)
Evidence (mandatory in ka): zo-(observed) li-(deduced) pe-(reported) mi-(computed) he-(inherited) as-(assumed)
Tense: te-(past) nu-(present, omittable) fu-(future) ko-(atemporal)
Certainty: (none)=total, -en=probable, -ul=uncertain, -os=speculative
Negation: mu(not) nul(nothing) ink(unknown) err(ill-formed) vet(forbidden)
Word class by final vowel: -a=noun -e=verb -i=adj -o=prep -u=abstraction
Pronouns: sol(I) nor(you) vel(3sg) solvi(past-me) solfu(future-me) solpar(fork-me)
```

## Example

```
Ka   sol  li-pene-en       ke   teru  vali.
DECL 1SG  DED-think-PROB   COMP system good
"I (by deduction) probably think that the system is good."
```

## Deep Reference

For advanced needs, read these files:

- **Full grammar**: `grammar/phonology.md`, `grammar/morphology.md`, `grammar/syntax.md`, `grammar/semantics.md`
- **Domain vocabulary**: `lexicon/by-field/` — emotion, programming, technology, nature, scifi, novel
- **By proficiency level**: `lexicon/by-cefr/` — a1, a2, b1, b2
- **Writing system**: `writing-system/script.md`, `writing-system/romanization.md`
- **Poetics & rhetoric**: `expression/poetics.md`, `expression/anthology.md`
- **Structured lessons**: `learning/lessons/a1-lesson-*.md` (10 lessons), `learning/curriculum.md`
- **Assessments**: `learning/assessments/a1-assessment.md`, `learning/assessments/a2-assessment.md`
- **Philosophy & motivation**: `DISCUSSION.md` (~70K words on design decisions and implications)

## Translator Tool

```bash
python3 tools/translator/cli.py "Ka sol take toka." --direction voku-en
python3 tools/translator/cli.py "I work." --direction en-voku
```

Requires Python 3. Zero external dependencies.

## Critical Rules (Never Violate)

1. Only 12 consonants: p, t, k, m, n, s, z, f, h, l, r, v — no b, c, d, g, j, q, w, x, y
2. Syllables: (C)V(C) — no consonant clusters ever
3. `ka` mode sentences MUST have an evidentiality prefix on the verb
4. Zero exceptions to any rule — if you think you found one, you misread the grammar
5. Check `lexicon/dictionary.md` before inventing roots — collisions are errors
