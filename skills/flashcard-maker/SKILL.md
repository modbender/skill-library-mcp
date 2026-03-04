---
description: Generate Anki/Quizlet-compatible flashcards from text, notes, or documents using learning science principles.
---

# Flashcard Maker

Generate study flashcards from any text in Anki/Quizlet-importable format.

**Use when** creating flashcards, converting notes to study materials, or preparing for exams.

## Requirements

- No external tools required for TSV output
- Optional: Anki desktop app for `.apkg` import
- No API keys needed

## Instructions

1. **Read input material** — text, notes, file, or URL. Identify key concepts, definitions, facts, formulas, and relationships.

2. **Generate Q&A pairs** following learning science principles:
   - **One concept per card** — avoid compound questions
   - **Active recall** — ask "What is X?" not "Is X true?"
   - **Cloze deletions** — use `{{c1::answer}}` format for Anki cloze cards
   - **Avoid yes/no questions** — they don't test understanding
   - **Use mnemonics** where helpful
   - **Bidirectional cards** for definitions (term→definition AND definition→term)

3. **Output in requested format** (default: TSV):

   **TSV (Anki/Quizlet import):**
   ```
   front\tback
   What is photosynthesis?\tThe process by which plants convert light energy into chemical energy (glucose) using CO2 and water
   ```

   **With Anki tags (3-column TSV):**
   ```
   front\tback\ttag1 tag2
   ```

   **Markdown table** (for preview):
   | Front | Back |
   |-------|------|
   | Question | Answer |

4. **Save to file** when requested: `flashcards.tsv` or user-specified path.

## Guidelines

- Aim for **10-30 cards** per topic unless user specifies a count
- Keep answers **concise but complete** — 1-2 sentences max
- Support **multiple languages** in card content
- For **code/programming** topics: put code on front, explanation on back (or vice versa)
- For **vocabulary**: include example sentences and pronunciation hints

## Edge Cases

- **Very long source material**: Prioritize the most important concepts. Ask user if they want comprehensive or key-points-only.
- **Images in source**: Describe the visual content in text form for the card.
- **Ambiguous content**: Ask user to clarify scope (e.g., "Do you want cards for all terms or just chapter summaries?").
- **Duplicate concepts**: Merge similar ideas into a single card with a comprehensive answer.

## Import Instructions

- **Anki**: File → Import → select TSV file → set separator to Tab
- **Quizlet**: Create Set → Import → paste TSV content → set delimiter to Tab
