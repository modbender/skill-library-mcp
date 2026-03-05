# Google Search Skill

Google Search powered by Serper.dev API. Replaces Brave Search with richer results including Knowledge Graph, Answer Box, People Also Ask, and specialized search types.

## When to Use
Use this skill for any Google search request. Auto-detect intent:
- Default → `search`
- "news about X" / "latest X" → `news`
- "images of X" / "pictures of X" → `images`
- "videos of X" / "how to X video" → `videos`
- "restaurants near X" / "X near me" → `places`
- "how much does X cost" / "buy X" → `shopping` (⚠️ 2 credits — only when explicitly requested)
- "papers on X" / "research about X" → `scholar`
- "patents for X" → `patents`
- "suggestions for X" → `suggest`

## Usage

```bash
SCRIPT_DIR="~/.openclaw/workspace/skills/google-search/scripts"

# Web search (default)
npx tsx $SCRIPT_DIR/google-search.ts search "query" [--num 10] [--time day|week|month|year] [--country us] [--lang en]

# Specialized
npx tsx $SCRIPT_DIR/google-search.ts news "query" [--num 10]
npx tsx $SCRIPT_DIR/google-search.ts images "query"
npx tsx $SCRIPT_DIR/google-search.ts videos "query"
npx tsx $SCRIPT_DIR/google-search.ts places "query"
npx tsx $SCRIPT_DIR/google-search.ts shopping "query"
npx tsx $SCRIPT_DIR/google-search.ts scholar "query" [--year 2023]
npx tsx $SCRIPT_DIR/google-search.ts patents "query"
npx tsx $SCRIPT_DIR/google-search.ts suggest "query"
npx tsx $SCRIPT_DIR/google-search.ts credits
```

Add `--json` to any command for raw JSON output.

## Environment
Requires `SERPER_API_KEY` env var.

## Workflow
1. Run the appropriate search command
2. Parse the formatted output
3. If deeper content is needed, use `web_fetch` on promising links
4. Credit balance is shown in every response — monitor usage
5. Shopping costs 2 credits — only use when user explicitly asks for prices/shopping

## Time Filters
`--time` accepts: `hour`, `day`, `week`, `month`, `year` (or `h`, `d`, `w`, `m`, `y`)

## Notes
- Rate limit: 5 req/sec on free tier
- All searches cost 1 credit except shopping (2 credits)
- Results include rich data: Knowledge Graph, Answer Box, People Also Ask, Related Searches
