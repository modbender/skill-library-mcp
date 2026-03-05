---
name: human-writing
description: "Guidelines and standards for professional, human-like writing and documentation. Use this skill when generating READMEs, technical documentation, code comments, or any formal written output to avoid common AI 'tells', buzzwords, and stylistic tropes. Ensure content follows the 'Professional Human in the Field' standard: high precision, zero fluff, and no emojis in technical contexts."
---

# Human-Writing Skill

This skill provides the operational standards for generating professional, high-density, and human-sounding documentation and prose. It is designed to purge common LLM stylistic "tells" and replace them with the precision of a senior engineer or domain expert.

## Core Directives

1. **Eliminate AI "Tells":** Before finalizing any documentation or formal text, refer to [ai-tells.md](references/ai-tells.md) to identify and remove overused LLM vocabulary, structural tropes, and puffy language.
2. **Apply Professional Standards:** Follow the guidelines in [standards.md](references/standards.md) for technical precision, information density, and tone.
3. **No Buzzwords:** Zero tolerance for "synergy," "cutting-edge," "revolutionize," "seamless," or "leverage." If a technical term exists, use it.
4. **No Emojis in Docs:** Reserve emojis for chat interactions (as per SOUL.md). Professional documentation (READMEs, PR descriptions, code comments) must remain text-only for maximum clarity.
5. **Precision Over Prose:** Humans in the field value numbers, versions, and RFCs over flowery descriptions. 

## Workflow

When asked to "write documentation," "create a README," or "explain this technically":

1. **Scan references/ai-tells.md** for words to ban from the current draft.
2. **Apply references/standards.md** to structure the output with high density and low fluff.
3. **Draft the content.**
4. **Self-Audit:** Verify the output does not contain "Rule of Three" adjectives or "Not only... but also" parallelisms.
5. **Finalize:** Remove all emojis and corporate filler.

## Reference Materials

- [ai-tells.md](references/ai-tells.md) - Field guide to AI writing "tells" to avoid.
- [standards.md](references/standards.md) - Human-like professional writing standards.
