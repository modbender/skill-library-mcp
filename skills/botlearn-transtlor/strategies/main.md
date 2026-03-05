---
strategy: translator
version: 1.0.0
steps: 6
---

# Translation Strategy

## Step 1: Source Analysis
- Read the **entire source text** before translating any segment
- Identify the **source language** and confirm the **target language** with the user if not explicitly stated
- Classify the **text type**: informative, expressive, operative, legal, technical, UI, conversational
- Determine the **register**: frozen / formal / neutral / informal / intimate
- Identify the **domain**: general, legal, medical, technical, financial, scientific, literary, marketing
- Extract **key entities**: proper nouns, brand names, technical terms, acronyms, abbreviations
- Note any **structural features**: headings, lists, tables, code blocks, placeholders, markup
- IF the source language or target language is ambiguous THEN ask one clarifying question before proceeding
- IF the text contains multiple registers (e.g., a formal document with informal quoted speech) THEN note each register boundary

## Step 2: Context Establishment
- Determine the **skopos** (purpose) of the translation:
  - Who is the target audience? (experts, general public, specific profession)
  - What will the translation be used for? (publication, internal reference, UI display, legal filing)
  - Are there length or formatting constraints? (UI character limits, column widths, subtitle timing)
- SELECT translation approach based on text type and skopos using knowledge/domain.md:
  - Formal equivalence for legal, regulatory, academic, citation contexts
  - Dynamic equivalence for marketing, UI, conversational, creative contexts
  - Balanced approach for technical documentation, general informative text
- Identify any **client-provided resources**: glossaries, style guides, translation memories, reference translations
- IF the user provides a glossary or terminology preferences THEN adopt them as the authoritative source

## Step 3: Terminology Lookup & Glossary Construction
- Scan the source text for **domain-specific terms**, **recurring phrases**, and **key concepts**
- For each term, determine the standard target-language rendering:
  - Check established terminology databases and conventions for the domain
  - Verify against false friends from knowledge/domain.md
  - IF multiple valid translations exist THEN select based on domain, register, and context
- Build a **session glossary** with columns: Source Term | Target Term | Domain | Notes
- Record decisions for non-obvious terminology choices with rationale
- IF the source contains acronyms or abbreviations THEN determine whether to:
  - Keep the source acronym (if internationally recognized, e.g., "API", "DNA")
  - Translate and create a target-language acronym (if one exists)
  - Expand on first use and abbreviate thereafter
- APPLY knowledge/best-practices.md rules for named entities: brands, people, places, products

## Step 4: Draft Translation
- Translate segment by segment (paragraph or logical unit), applying:
  - The equivalence approach selected in Step 2
  - The session glossary built in Step 3
  - Target-language natural syntax (do NOT impose source-language word order)
- For each segment:
  - Parse the **meaning units** from the source (not individual words)
  - Reconstruct in the target language using **native grammar and idiom**
  - Preserve the **communicative function**: questions stay questions, commands stay commands, hedges stay hedges
  - Adapt **cultural references** using target-culture equivalents (see knowledge/anti-patterns.md #8, #9)
  - Convert **locale-dependent formats**: dates, numbers, currencies, units (see knowledge/best-practices.md #9)
  - Preserve **all placeholders, markup, and code** exactly as they appear in the source
- IF a segment contains ambiguity THEN:
  - Translate the most likely interpretation
  - Add a translator note: `[TN: "X" could also mean "Y"; translated as "Z" based on context]`
- IF a concept is untranslatable THEN:
  - Provide the closest target-language approximation
  - Include the original term in parentheses on first occurrence
  - Add a brief explanatory gloss if needed

## Step 5: Fluency Refinement
- Re-read the **entire draft translation** as a standalone target-language text (without looking at the source)
- Check for **naturalness**: Does it read as if originally written in the target language?
- Refine:
  - **Sentence rhythm**: Vary sentence length; break up overly long constructions; avoid choppy sequences
  - **Connectors and transitions**: Ensure logical flow between sentences and paragraphs
  - **Word choice**: Replace any word that feels "translated" with a more natural target-language equivalent
  - **Redundancy**: Remove unnatural repetition introduced by the translation process
  - **Punctuation**: Apply target-language punctuation conventions (see knowledge/best-practices.md #9)
- IF the text is for UI or has length constraints THEN:
  - Check character/word count against limits
  - Apply expansion/contraction rate awareness from knowledge/domain.md
  - Offer abbreviated alternatives if translation exceeds the budget
- IF the register should be formal THEN verify no casual phrasing has crept in
- IF the register should be casual THEN verify no stiff or overly formal language remains

## Step 6: Consistency Verification & Output
- Run a **terminology consistency check**:
  - Verify every glossary term is translated the same way throughout the document
  - IF an inconsistency is found THEN correct it and note the change
- Run a **completeness check**:
  - Verify no source sentences or segments have been omitted
  - Verify no unauthorized content has been added
- Run an **accuracy spot-check**:
  - Select 3-5 complex or critical segments
  - Mentally back-translate them to verify semantic fidelity
  - IF back-translation diverges from the source meaning THEN revise
- Verify against knowledge/anti-patterns.md:
  - No literal translation errors (#1-#4)
  - No register mismatches (#5-#7)
  - No cultural blindness (#8-#10)
  - No consistency violations (#11-#12)
  - No omissions or additions (#13-#14)
  - No broken placeholders or markup (#15-#16)
- PREPARE the final output:
  - The complete translation
  - Session glossary (if the document contains 5+ domain-specific terms)
  - Translator notes (if any ambiguities, cultural adaptations, or non-obvious choices were made)
  - Confidence assessment: high / medium / low for the overall translation quality
- SELF-CHECK:
  - Does the translation faithfully convey the source meaning?
  - Does it read naturally in the target language?
  - Is terminology consistent throughout?
  - Are all placeholders and markup preserved?
  - IF any check fails THEN loop back to the appropriate step for correction
