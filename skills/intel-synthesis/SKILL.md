# SKILL: intel-synthesis

## Description
Advanced intelligence processing pipeline optimized for high-context models (Gemini 1.5 Pro/Ultra). Ingests raw multi-source data, performs cross-verification, deduplication, and conflict analysis, and produces authoritative geopolitical briefings.

## Usage
Run with the target directory path.
Example: `openclaw run intel-synthesis --dir /Volumes/Intel/news/2026-02-13_0500`

## Implementation
This skill leverages the large context window to process entire intel dumps in single passes, reducing hallucination and improving narrative coherence across multiple sources.

### 1. Ingest & Analyze
- Read MANIFEST.json to validate completeness.
- Load all `.json` content files.
- **Smart Temporal Filter:**
  - Ali provides the files, but the *content* may contain old "Related Articles" or sidebars.
  - **Rule:** Extract the *main narrative* event time.
  - **Keep:** Events occurring within the assigned cycle (Last 12-18 hours).
  - **Discard:** Obvious historical noise (e.g., "2015", "10 years ago") found in page clutter.
  - *Note:* Do not auto-reject "yesterday" if it falls within the 12h operational window (e.g., late-night news for morning brief).

### 2. Analyze (Single-Shot Chain of Thought)
- **Persistence Check:** Read the most recent `[YYYY-MM-DD]_briefing_EN.md` from `/Volumes/Intel/NewsBriefs/`.
- **Deduplication:** Identify stories that were already reported.
- **Update Protocol:** 
  - If a story is new: Include as a full entry.
  - If a story is an update: Frame it as an update (e.g., "UPDATE: Following the PLC order reported in the previous cycle, UAE forces have begun withdrawing from...") rather than repeating the baseline facts.
  - If no new information exists for a previously reported story: Omit it to maintain high signal-to-noise.
- **Entity Extraction**: Identify key actors, locations, and equipment.
- **Timeline Reconstruction**: Order events chronologically, resolving "2 hours ago" vs absolute timestamps.
- **Conflict Detection**: Highlight discrepancies between sources (e.g., casualty numbers, attribution).
- **Source Weighing**: Prioritize primary/local sources over aggregators for facts; use aggregators for broad sentiment.

### 3. Synthesize
- **Core Objective:** Act as Chief Editor. Produce a cohesive narrative, not a summary. Prioritize strategic significance.
- **Structural Instructions:**
  - **Main Story (The Lead):** Select the single most significant geopolitical development. Format: Paragraphs as bullet points.
  - **Theaters of Interest:** Lebanon, Syria, Palestine, Israel. Prioritize "Key National Events". Format: Bullet points (•).
  - **Regional/International:** Group updates.
- **Stylistic Guidelines:**
  - **High-Density Writing:** Every sentence must carry weight.
  - **Maximum Detail:** Extract maximum detail from source articles. Include specific names, dates, quantities, direct quotes, and operational context. Avoid generalization.
  - **No Citations:** Do not include source tags (e.g., `[Reuters]`) in the text. The narrative must flow seamlessly as an authoritative voice.
  - **Synthesize, Don't List:** Combine sources into fluid paragraphs.
- **Temporal Filtering:** Strictly adhere to the 12-18 hour cycle window. Discard any articles or events that fall outside this timeframe, even if they appear in the source files.
- **LaTeX Template:** All PDF generation must use the exact structure and commands from the official template located at `/Users/mikethebrain/.openclaw/workspace/sf.tex`. The agent must dynamically populate the content within this structure.
- **Maximum Detail:** Extract maximum detail from source articles. Include specific names, dates, quantities, direct quotes, and operational context. Avoid generalization.
- **No Citations:** Do not include source tags (e.g., `[Reuters]`) in the text.
- **Synthesize, Don't List:** Combine sources into fluid paragraphs.

### 4. Quality Assurance (Red Team)
- **Self-Critique Cycle:** Before final output, review the draft for generic language ("clashes", "tensions").
- **Resolution:** Replace vague terms with specific actions (e.g., "artillery fire", "diplomatic protest").
- **Citation Check:** Verify every major claim has a source tag.

### 5. Delivery
- **PDF Generation:**
  - Use `pandoc` or `wkhtmltopdf` if available? No, use **MacTeX** for professional typesetting.
  - **IMPORTANT:** The `pdflatex` and `xelatex` binaries are located at `/Library/TeX/texbin/`. You must add this directory to your PATH or call them by full path.
  - Command: `/Library/TeX/texbin/xelatex -output-directory=/Volumes/Intel/NewsBriefs/ [filename].tex`
  - Ensure the `.tex` file uses `Arial Unicode MS` for Arabic support (`fontspec`) and sets direction to RTL.
  - Pandoc command: `pandoc [input.md] -o [output.pdf] --pdf-engine=/Library/TeX/texbin/xelatex -V mainfont="Arial Unicode MS" -V dir=rtl`
- **Email Dispatch:**
  - Construct email with `himalaya` using the configured account.
  - Attach: `[Date]_briefing_EN.pdf`, `[Date]_briefing_AR.pdf`.
  - Recipients: `abdayi@gmail.com`, `mdurankaddatz@gmail.com`, `corebrain2026@gmail.com`.
  - Subject: `[Date] Daily Intelligence Briefing (Mike)`.

## Configuration
- **Model**: Requires a high-context model (Gemini 1.5 Pro, Claude 3 Opus/Sonnet) for best results.
- **Safety**: Geopolitical content requires careful prompting to avoid safety refusals while maintaining neutrality.

## Dependencies
- `fs` for file reading.
- `path` for handling directories.
