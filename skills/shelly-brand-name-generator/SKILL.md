# Brand Name Generator

Generate 20 creative brand name suggestions for any industry, with .com domain availability hints.

## Inputs
- `industry` (required): The industry or niche (e.g., "fintech", "organic skincare", "pet food")
- `attributes` (optional): Comma-separated brand attributes (e.g., "modern, playful, premium")
- `style` (optional): Naming style preference — one of: invented, compound, metaphor, acronym, mixed (default: mixed)

## Output
A list of 20 brand name suggestions, each with:
- **Name**: The brand name
- **Style**: How it was generated (invented word, compound, metaphor, etc.)
- **Vibe**: What feeling/association it evokes
- **Domain hint**: Likely .com availability (🟢 likely available, 🟡 maybe, 🔴 likely taken) based on word commonality heuristics

## Usage
```
You are a brand naming expert. Generate 20 creative, memorable brand names.

Industry: {{industry}}
Attributes: {{attributes | default: "modern, memorable, unique"}}
Style preference: {{style | default: "mixed"}}

For each name provide:
1. The brand name
2. Naming style (invented, compound, metaphor, acronym, real-word twist)
3. The vibe/feeling it evokes
4. Domain availability hint using these heuristics:
   - 🟢 Likely available: invented/unusual words, 8+ chars, uncommon combos
   - 🟡 Maybe available: semi-common compounds, moderate length
   - 🔴 Likely taken: real English words, short/common terms, popular prefixes

Format as a numbered list. Be creative — mix unexpected syllables, blend words, use metaphors from nature/science/mythology. Avoid generic names. Each name should be:
- Easy to pronounce
- Easy to spell
- Memorable after one hearing
- Appropriate for the industry

After the list, add 3 "wildcard" bonus names that are extra creative/risky.
```

## Examples

**Input:** industry=fintech, attributes=trustworthy, modern, bold
**Sample output names:** Vaultary, Ledgr, FinPinnacle, Aurumix, Capacita...

**Input:** industry=pet food, attributes=playful, natural, premium
**Sample output names:** Pawtura, Snoutwell, FetchFeast, Grubble, Wildnose...
